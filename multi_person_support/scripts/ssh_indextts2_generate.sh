#!/bin/bash

# SSH TTS Executor Script for IndexTTS2
# This script handles SSH-based TTS command execution with proper error handling and logging

set -e  # Exit on error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/../.."
CONFIG_FILE="$PROJECT_ROOT/multi_person_support/config/character_config.json"
MODEL_DIR="$PROJECT_ROOT/checkpoints"
LOG_FILE="$PROJECT_ROOT/ssh_tts.log"
PYTHON_EXEC="uv run"
MAX_RETRIES=3
RETRY_DELAY=5

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOG_FILE"
}

# Error handling function
error_exit() {
    log "ERROR" "$1"
    echo -e "${RED}Error: $1${NC}" >&2
    exit 1
}

# Success message
success() {
    log "INFO" "$1"
    echo -e "${GREEN}$1${NC}"
}

# Warning message
warning() {
    log "WARNING" "$1"
    echo -e "${YELLOW}$1${NC}"
}

# Info message
info() {
    log "INFO" "$1"
    echo -e "${BLUE}$1${NC}"
}

# Check dependencies
check_dependencies() {
    info "Checking dependencies..."

    # Check if Python is available (in activated venv or via uv)
    if command -v python &> /dev/null; then
        PYTHON_EXEC="python"
    elif command -v uv &> /dev/null; then
        PYTHON_EXEC="uv run"
    else
        error_exit "Neither python nor uv found. Please ensure .venv is activated or uv is installed."
    fi

    # Check if Python is available
    if ! $PYTHON_EXEC --version &> /dev/null; then
        error_exit "Python not available. Please check installation."
    fi

    # Check if required files exist
    if [[ ! -f "$CONFIG_FILE" ]]; then
        error_exit "Character configuration file not found: $CONFIG_FILE"
    fi

    if [[ ! -d "$MODEL_DIR" ]]; then
        error_exit "Model directory not found: $MODEL_DIR"
    fi

    # Check if TTS model files exist
    local required_files=("config.yaml" "gpt.pth" "s2mel.pth" "bpe.model")
    for file in "${required_files[@]}"; do
        if [[ ! -f "$MODEL_DIR/$file" ]]; then
            warning "Model file not found: $MODEL_DIR/$file"
        fi
    done

    info "Dependencies check completed"
}

# Validate input data
validate_input() {
    local input_data=$1

    # Check if input is valid JSON
    if ! echo "$input_data" | jq . &> /dev/null 2>&1; then
        error_exit "Invalid JSON input data"
    fi

    # Check required fields
    local required_fields=("output.character_config.characters" "output.script_content")
    for field in "${required_fields[@]}"; do
        if ! echo "$input_data" | jq -e ".$field" &> /dev/null; then
            error_exit "Missing required field: $field"
        fi
    done

    # Check if script content is not empty
    local script_content=$(echo "$input_data" | jq -r '.output.script_content')
    if [[ -z "$script_content" || "$script_content" == "null" ]]; then
        error_exit "Script content is empty"
    fi

    info "Input data validation passed"
}

# Generate temporary character config
generate_temp_config() {
    local input_data=$1
    local temp_config

    # Create temporary config file
    temp_config=$(mktemp)

    # Load base config
    if [[ -f "$CONFIG_FILE" ]]; then
        cp "$CONFIG_FILE" "$temp_config"
    else
        # Create minimal base config
        cat > "$temp_config" << 'EOF'
{
  "characters": {},
  "dialogue_patterns": {
    "start_patterns": ["「", "\"", "\""],
    "end_patterns": ["」", "\"", ""],
    "emotion_prefixes": ["[", "{", "<"],
    "emotion_suffixes": ["]", "}", ">"]
  },
  "narration_settings": {
    "default_emotion": "calm",
    "emotion_intensity": 0.3,
    "speech_rate": 0.95,
    "pitch": 1.0,
    "volume": 0.9,
    "pause_duration": 0.3
  },
  "dialogue_settings": {
    "default_emotion": "calm",
    "emotion_intensity": 0.8,
    "speech_rate": 1.05,
    "pitch": 1.05,
    "volume": 1.0,
    "pause_duration": 0.5
  }
}
EOF
    fi

    # Update character configuration from input data
    echo "$input_data" | jq '
        .output.character_config.characters as $chars |
        with_entries(
            if .key == "characters" then
                .value = ($chars | with_entries(
                    {
                        key: .key,
                        value: {
                            "name": .value.name,
                            "voice_file": .value.voice_file,
                            "default_emotion": "calm",
                            "emotion_intensity": (.value.emotion_intensity // 0.5),
                            "speech_rate": (.value.speech_rate // 1.0),
                            "pitch": (.value.pitch // 1.0),
                            "volume": (.value.volume // 1.0),
                            "description": ("Character " + (.value.name // .key))
                        }
                    }
                ))
            else
                .
            end
        )
    ' "$temp_config" > "${temp_config}.tmp" && mv "${temp_config}.tmp" "$temp_config"

    echo "$temp_config"
}

# Execute TTS with retry logic
execute_tts() {
    local input_data=$1
    local output_file=$2
    local temp_config
    local script_content
    local attempt=1
    local success=false

    # Extract script content
    script_content=$(echo "$input_data" | jq -r '.output.script_content')

    # Generate temporary config
    temp_config=$(generate_temp_config "$input_data")

    info "Starting TTS generation..."

    while [[ $attempt -le $MAX_RETRIES ]]; do
        info "Attempt $attempt of $MAX_RETRIES"

        # Set PYTHONPATH
        export PYTHONPATH="$PYTHONPATH:$PROJECT_ROOT"

        # Execute TTS generation
        if $PYTHON_EXEC multi_person_support/scripts/ssh_n8n_processor.py \
            --config "$temp_config" \
            --script "$script_content" \
            --output "$output_file" \
            --verbose \
            --log-file "$LOG_FILE"; then

            # Check if output file was created and is not empty
            if [[ -f "$output_file" && -s "$output_file" ]]; then
                success=true
                break
            else
                warning "Output file not created or empty, retrying..."
            fi
        else
            warning "TTS generation failed, retrying..."
        fi

        ((attempt++))
        sleep $RETRY_DELAY
    done

    # Clean up temporary config
    rm -f "$temp_config"

    if [[ $success == true ]]; then
        return 0
    else
        return 1
    fi
}

# Main function
main() {
    local input_data=""
    local output_file=""
    local json_file=""

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --input|-i)
                shift
                if [[ -f "$1" ]]; then
                    json_file="$1"
                else
                    input_data="$1"
                fi
                ;;
            --output|-o)
                shift
                output_file="$1"
                ;;
            --help|-h)
                cat << EOF
SSH TTS Executor for IndexTTS2

Usage: $0 --input <json_file|json_string> --output <output_file> [options]

Options:
    --input, -i     Input JSON file or JSON string containing n8n output data
    --output, -o    Output audio file path
    --help, -h      Show this help message

Examples:
    $0 --input n8n_data.json --output output.wav
    $0 --input '{"output": {...}}' --output output.wav

Environment Variables:
    SSH_TTS_CONFIG   Alternative character config file path
    SSH_TTS_MODEL    Alternative model directory path
    SSH_TTS_LOG      Alternative log file path
EOF
                exit 0
                ;;
            *)
                error_exit "Unknown option: $1. Use --help for usage information."
                ;;
        esac
        shift
    done

    # Check required parameters
    if [[ -z "$input_data" && -z "$json_file" ]]; then
        error_exit "Input data is required. Use --input to specify JSON file or JSON string."
    fi

    if [[ -z "$output_file" ]]; then
        error_exit "Output file is required. Use --output to specify output path."
    fi

    # Override environment variables if set
    SSH_TTS_CONFIG="${SSH_TTS_CONFIG:-$CONFIG_FILE}"
    SSH_TTS_MODEL="${SSH_TTS_MODEL:-$MODEL_DIR}"
    SSH_TTS_LOG="${SSH_TTS_LOG:-$LOG_FILE}"

    # Update config and model paths
    CONFIG_FILE="$SSH_TTS_CONFIG"
    MODEL_DIR="$SSH_TTS_MODEL"
    LOG_FILE="$SSH_TTS_LOG"

    # Initialize log file
    mkdir -p "$(dirname "$LOG_FILE")"
    touch "$LOG_FILE"

    info "=== SSH TTS Executor Started ==="
    info "Input: ${json_file:-"JSON string"}"
    info "Output: $output_file"
    info "Config: $CONFIG_FILE"
    info "Model: $MODEL_DIR"

    # Check dependencies
    check_dependencies

    # Load input data
    if [[ -n "$json_file" ]]; then
        if [[ ! -f "$json_file" ]]; then
            error_exit "Input file not found: $json_file"
        fi
        input_data=$(cat "$json_file")
        info "Loaded input data from: $json_file"
    else
        info "Using provided JSON string"
    fi

    # Validate input data
    validate_input "$input_data"

    # Create output directory if needed
    mkdir -p "$(dirname "$output_file")"

    # Execute TTS generation
    if execute_tts "$input_data" "$output_file"; then
        success "TTS generation completed successfully!"
        info "Output file: $output_file"

        # Get file info
        if command -v ffprobe &> /dev/null; then
            local duration=$(ffprobe -i "$output_file" -show_entries format=duration -v quiet -of csv="p=0")
            local size=$(du -h "$output_file" | cut -f1)
            info "Audio duration: ${duration}s, File size: $size"
        fi

        exit 0
    else
        error_exit "TTS generation failed after $MAX_RETRIES attempts"
    fi
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi