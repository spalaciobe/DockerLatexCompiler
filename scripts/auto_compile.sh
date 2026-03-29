#!/bin/bash

# Script para compilar automáticamente LaTeX detectando la carpeta del archivo .tex actual
# Uso: ./auto_compile.sh [ruta_del_archivo_tex]
# Soporta archivos dentro de ws_latex/ o en cualquier ubicación del sistema

PROJECT_ROOT="$(cd "$(dirname "$0")/.."; pwd)"
source ${PROJECT_ROOT}/config_docker.sh

# Función para mostrar ayuda
show_help() {
    echo "Uso: $0 [ruta_del_archivo_tex]"
    echo ""
    echo "Si no se proporciona ruta, busca archivos .tex en el directorio actual"
    echo "Si se proporciona ruta, detecta automáticamente la carpeta del proyecto"
    echo ""
    echo "Ejemplos:"
    echo "  $0                                    # Busca .tex en directorio actual"
    echo "  $0 /ruta/a/archivo.tex               # Compila desde cualquier ubicación"
    echo "  $0 ws_latex/docking_article/main.tex # Detecta carpeta del archivo"
}

# Función para encontrar archivos .tex
find_tex_files() {
    local search_dir="$1"
    find "$search_dir" -maxdepth 1 -name "*.tex" -type f
}

# Función para seleccionar archivo .tex cuando hay múltiples
select_tex_file() {
    local tex_files="$1"
    local file_count=$(echo "$tex_files" | wc -l)

    if [ "$file_count" -eq 1 ]; then
        echo "$tex_files"
        return
    fi

    echo "Se encontraron $file_count archivos .tex:" >&2
    echo "" >&2

    # Crear array de archivos
    local files=()
    local i=1
    while IFS= read -r file; do
        files+=("$file")
        echo "  $i) $(basename "$file")" >&2
        ((i++))
    done <<< "$tex_files"

    echo "" >&2
    echo -n "Selecciona el archivo a compilar (1-$file_count): " >&2
    read -r selection

    # Validar selección
    if [[ "$selection" =~ ^[0-9]+$ ]] && [ "$selection" -ge 1 ] && [ "$selection" -le "$file_count" ]; then
        local selected_index=$((selection - 1))
        echo "${files[$selected_index]}"
    else
        echo "Selección inválida. Usando el primer archivo por defecto." >&2
        echo "${files[0]}"
    fi
}

# Función para detectar la carpeta del proyecto y el modo (internal/external)
# Devuelve: "project_folder:mode" donde mode es "internal" o "external"
detect_project_folder() {
    local tex_file="$1"

    # Verificar si el archivo está dentro de ws_latex (internal)
    if [[ "$tex_file" == *"ws_latex"* ]]; then
        local relative_path=$(echo "$tex_file" | sed "s|.*ws_latex/||")
        local project_folder=$(echo "$relative_path" | cut -d'/' -f1)
        echo "${project_folder}:internal"
    else
        # External: usar el nombre del directorio padre
        local parent_dir=$(dirname "$tex_file")
        local folder_name=$(basename "$parent_dir")
        if [ "$folder_name" = "/" ] || [ -z "$folder_name" ]; then
            echo ""
            return
        fi
        echo "${folder_name}:external"
    fi
}

# Función principal de compilación
compile_project() {
    local project_folder="$1"
    local tex_file="$2"
    local mode="$3"

    echo "[INFO] Detectando proyecto: $project_folder (modo: $mode)"

    # Determinar el volumen Docker según el modo
    local volume_mount
    if [ "$mode" = "external" ]; then
        local host_dir=$(dirname "$tex_file")
        host_dir=$(cd "$host_dir" && pwd)
        volume_mount="${host_dir}:/home/dockeruser/ws_latex/${project_folder}"
        echo "[INFO] Compilando proyecto externo: $host_dir"
    else
        # Verificar que la carpeta del proyecto existe
        if [ ! -d "${PROJECT_ROOT}/ws_latex/${project_folder}" ]; then
            echo "[ERROR] No se encontró la carpeta 'ws_latex/${project_folder}'"
            echo "   Proyectos disponibles:"
            ls -1 "${PROJECT_ROOT}/ws_latex/" 2>/dev/null | sed 's/^/   - /'
            return 1
        fi
        volume_mount="${PROJECT_ROOT}/ws_latex:/home/dockeruser/ws_latex"
    fi

    echo "[COMPILE] LaTeX en ${project_folder}/"

    # Si se especifica un archivo .tex, compilar solo ese archivo
    if [ -n "$tex_file" ]; then
        local tex_filename=$(basename "$tex_file")
        echo "[FILE] Compilando archivo específico: $tex_filename"

        docker run --rm \
            --volume ${volume_mount} \
            --network ${DOCKER_NETWORK} \
            --dns=8.8.8.8 \
            ${DOCKER_IMAGE_NAME} \
            "${project_folder}" "${tex_filename}"
    else
        docker run --rm \
            --volume ${volume_mount} \
            --network ${DOCKER_NETWORK} \
            --dns=8.8.8.8 \
            ${DOCKER_IMAGE_NAME} \
            "${project_folder}"
    fi
}

# Procesar argumentos
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
    exit 0
fi

# Si se proporciona un archivo .tex como argumento
if [ $# -gt 0 ]; then
    tex_file="$1"

    # Convertir a ruta absoluta si es relativa
    if [[ "$tex_file" != /* ]]; then
        tex_file="$(pwd)/$tex_file"
    fi

    # Verificar que el archivo existe
    if [ ! -f "$tex_file" ]; then
        echo "[ERROR] El archivo '$tex_file' no existe"
        exit 1
    fi

    # Detectar la carpeta del proyecto y el modo
    result=$(detect_project_folder "$tex_file")
    project_folder=$(echo "$result" | cut -d':' -f1)
    mode=$(echo "$result" | cut -d':' -f2)

    if [ -z "$project_folder" ]; then
        echo "[ERROR] No se pudo detectar la carpeta del proyecto"
        exit 1
    fi

    compile_project "$project_folder" "$tex_file" "$mode"

else
    # Si no se proporcionan argumentos, buscar archivos .tex en el directorio actual
    current_dir="$(pwd)"
    tex_files=$(find_tex_files "$current_dir")

    if [ -z "$tex_files" ]; then
        echo "[ERROR] No se encontraron archivos .tex en el directorio actual: $current_dir"
        echo ""
        echo "Uso: $0 <ruta_del_archivo_tex>"
        echo "O ejecuta desde un directorio que contenga archivos .tex"
        exit 1
    fi

    # Si hay múltiples archivos .tex, permitir al usuario seleccionar
    selected_tex=$(select_tex_file "$tex_files")
    echo "[FILE] Usando archivo: $(basename "$selected_tex")"

    # Detectar la carpeta del proyecto y el modo
    result=$(detect_project_folder "$selected_tex")
    project_folder=$(echo "$result" | cut -d':' -f1)
    mode=$(echo "$result" | cut -d':' -f2)

    if [ -z "$project_folder" ]; then
        echo "[ERROR] No se pudo detectar la carpeta del proyecto"
        exit 1
    fi

    compile_project "$project_folder" "$selected_tex" "$mode"
fi
