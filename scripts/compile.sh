#!/bin/bash

# Compila archivos LaTeX usando Docker
# Uso: ./compile.sh <directorio>
# El directorio puede ser relativo a ws_latex/ o una ruta absoluta

PROJECT_ROOT="$(cd "$(dirname "$0")"; cd ..; pwd)"
source ${PROJECT_ROOT}/config_docker.sh

# Check if article parameter is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <article_directory>"
    echo "Examples:"
    echo "  $0 master-thesis              # Compile ws_latex/master-thesis/"
    echo "  $0 /path/to/latex/project     # Compile from any location"
    exit 1
fi

ARTICLE_DIR="$1"

# Determine if this is an external path (absolute or contains /)
if [[ "$ARTICLE_DIR" == /* ]]; then
    # External absolute path
    DIR_PATH=$(cd "$ARTICLE_DIR" 2>/dev/null && pwd)
    if [ -z "$DIR_PATH" ] || [ ! -d "$DIR_PATH" ]; then
        echo "[ERROR] Directory '$ARTICLE_DIR' does not exist"
        exit 1
    fi
    FOLDER_NAME=$(basename "$DIR_PATH")
    VOLUME_MOUNT="${DIR_PATH}:/home/dockeruser/ws_latex/${FOLDER_NAME}"
    echo "[COMPILE] LaTeX files in ${DIR_PATH}/"
else
    # Internal: relative to ws_latex/
    FOLDER_NAME="$ARTICLE_DIR"
    if [ ! -d "${PROJECT_ROOT}/ws_latex/${ARTICLE_DIR}" ]; then
        echo "[ERROR] Directory 'ws_latex/${ARTICLE_DIR}' does not exist"
        exit 1
    fi
    VOLUME_MOUNT="${PROJECT_ROOT}/ws_latex:/home/dockeruser/ws_latex"
    echo "[COMPILE] LaTeX files in ws_latex/${ARTICLE_DIR}/"
fi

docker run --rm \
    --volume ${VOLUME_MOUNT} \
    --network ${DOCKER_NETWORK} \
    --dns=8.8.8.8 \
    ${DOCKER_IMAGE_NAME} \
    "${FOLDER_NAME}"
