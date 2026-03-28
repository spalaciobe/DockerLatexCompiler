FROM alpine:3.19
LABEL maintainer="Alejandro Gomez (aldajo92)" \
      description="A lightweight Alpine-based docker image that provides pdflatex and common packages" \
      repo="https://github.com/<pending>"

# Install pdflatex, essential LaTeX packages, and Python
RUN apk add --no-cache \
    texlive \
    texlive-luatex \
    texlive-xetex \
    python3 \
    py3-pip

RUN apk add --no-cache \
    inkscape

# TODO:Install LaTeX packages FROM HERE
# RUN apk add --no-cache \
#     <packages>

# Install additional LaTeX packages (keycommand is in latexextra, fontawesome5 in fontsextra)
RUN apk add --no-cache \
    texmf-dist-latexextra \
    texmf-dist-fontsextra

# Copy the compile script
COPY compile_latex.py /usr/local/bin/compile_latex.py
RUN chmod +x /usr/local/bin/compile_latex.py

# Create a non-root user for better security
RUN addgroup -g 1000 dockeruser && \
    adduser -u 1000 -G dockeruser -s /bin/bash -D dockeruser

# Switch to the created user
USER dockeruser
WORKDIR /home/dockeruser/ws_latex

# Create a wrapper script for compilation
USER root
RUN echo '#!/bin/bash' > /usr/local/bin/compile_article.sh && \
    echo 'if [ $# -eq 0 ]; then' >> /usr/local/bin/compile_article.sh && \
    echo '    echo "Usage: compile_article.sh <article_directory> [specific_file]"' >> /usr/local/bin/compile_article.sh && \
    echo '    exit 1' >> /usr/local/bin/compile_article.sh && \
    echo 'fi' >> /usr/local/bin/compile_article.sh && \
    echo 'cd /home/dockeruser/ws_latex' >> /usr/local/bin/compile_article.sh && \
    echo 'if [ $# -eq 2 ]; then' >> /usr/local/bin/compile_article.sh && \
    echo '    python3 /usr/local/bin/compile_latex.py "$1" "$2"' >> /usr/local/bin/compile_article.sh && \
    echo 'else' >> /usr/local/bin/compile_article.sh && \
    echo '    python3 /usr/local/bin/compile_latex.py "$1"' >> /usr/local/bin/compile_article.sh && \
    echo 'fi' >> /usr/local/bin/compile_article.sh && \
    chmod +x /usr/local/bin/compile_article.sh

USER dockeruser
WORKDIR /home/dockeruser/ws_latex

# Default command
ENTRYPOINT ["/usr/local/bin/compile_article.sh"]
