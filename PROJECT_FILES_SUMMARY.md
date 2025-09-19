# IndexTTS2 Project Files Summary

## 🎯 Project Overview

IndexTTS2 is a state-of-the-art text-to-speech system with emotionally expressive voice synthesis and multi-character support. This project contains both the core TTS engine and SSH/N8N integration capabilities.

## 📁 Core Project Structure

```
index-tts2/
├── indextts/                    # Core TTS engine modules
│   ├── gpt/                     # GPT-based autoregressive model
│   ├── vqvae/                   # VQ-VAE encoder
│   ├── s2mel/                   # Speech-to-mel converter
│   └── utils/                   # Utility functions
├── checkpoints/                 # Model files and configuration
├── examples/                     # Original example files
├── tests/                        # Test scripts
├── tools/                        # Utility tools
├── multi_person_support/        # Multi-person long text support (NEW)
└── [Core project files]          # webui.py, README.md, CLAUDE.md, etc.
```

## 🚀 Multi-Person Long Text Support (Organized)

The multi-person long text support system has been moved to a dedicated `multi_person_support/` folder to avoid confusion with core project files.

### Multi-Person Support Structure
```
multi_person_support/
├── scripts/                     # Processing scripts
│   ├── ssh_n8n_processor.py      # Main Python processor
│   ├── ssh_indextts2_generate.sh # Bash wrapper
│   ├── long_text_emotion_generator.py    # Single-voice generator
│   └── multi_character_emotion_generator.py # Multi-character system
├── config/                      # Configuration files
│   └── character_config.json    # Character voice settings
├── examples/                    # Sample files and test data
│   ├── n8n_json_sample_new_format.json    # n8n format examples
│   ├── ssh_n8n_example.json              # Test examples
│   ├── simple_multi_character_example.txt  # Text examples
│   └── llm_prompt_example.py              # LLM prompt examples
├── docs/                        # Documentation
│   ├── README_SSH_TTS.md               # SSH integration guide
│   ├── LLM_MULTI_CHARACTER_PROMPT.md   # LLM prompt guide
│   ├── README_LONG_TEXT_EMOTION.md      # Basic emotion guide
│   └── README_MULTI_CHARACTER_EMOTION.md # Multi-character guide
├── generated/                    # Generated audio files
│   ├── deep_sea_story.wav          # Sample outputs
│   ├── story.wav
│   └── test_*.wav
└── README.md                     # Multi-person support overview
```

## 🔧 Core IndexTTS2 Files

### Main Applications
- **`webui.py`** - Gradio web interface for TTS generation
- **`indextts/cli.py`** - Command-line interface
- **`indextts/infer_v2.py`** - Main inference engine
- **`indextts/infer.py`** - Legacy inference engine

### Configuration
- **`checkpoints/config.yaml`** - Model configuration
- **`checkpoints/`** - Model weights and files (gpt.pth, s2mel.pth, etc.)

### Documentation
- **`README.md`** - Main project documentation
- **`CLAUDE.md`** - Claude Code integration guide
- **`PROJECT_FILES_SUMMARY.md`** - This file

## 🎯 SSH/N8N Integration Features

### Key Capabilities
- **Multi-character support** - Process scripts with multiple voice characters
- **Emotion control** - Parse and apply emotion tags with intensity levels
- **SSH integration** - Secure remote execution via SSH
- **n8n compatibility** - Works with n8n workflow automation
- **Strict format** - Enforces `{[character]:[emotion:intensity]}` format
- **🆕 Automatic stereo-to-mono conversion** - Converts stereo voice samples to mono for optimal IndexTTS2 compatibility
- **🆕 Enhanced text parsing** - Improved text content extraction for accurate audio generation
- **🆕 Descriptive emotion support** - Natural language emotion descriptions via Qwen emotion model
- **🆕 Fixed speech rate control** - Proper speech rate implementation with use_speed parameter, plain text uses normal speed without emotion processing slowdown

### Usage Examples
```bash
# Direct Python usage - text input (requires --config)
uv run multi_person_support/scripts/ssh_n8n_processor.py \
    --config multi_person_support/config/character_config.json \
    --script "{[narrator]:[calm:0.3]}Hello world" \
    --output output.wav

# Direct Python usage - JSON input (self-contained)
uv run multi_person_support/scripts/ssh_n8n_processor.py \
    --input-json multi_person_support/examples/1_basic_story.json \
    --output output.wav

# Bash wrapper usage (self-contained JSON input)
bash multi_person_support/scripts/ssh_indextts2_generate.sh \
    --input multi_person_support/examples/1_basic_story.json \
    --output output.wav
```

## 📋 Format Specifications

### Enhanced Character Format (Two Formats Supported)

#### 1. Numeric Intensity Format (Original)
```
{[character_name]:[emotion:intensity]}Text content
```
**Examples:**
- `{[narrator]:[calm:0.3]}Once upon a time...`
- `{[sarah]:[excited:0.8]}Hello world!`
- `{[tom]:[calm:0.7]}Welcome to our story.`

#### 2. Descriptive Emotion Format (New!)
```
{[character_name]:[emotion:description]}Text content
```
**Examples:**
- `{[narrator]:[calm:very peaceful and calm]}Once upon a time...`
- `{[sarah]:[excited:very excited and enthusiastic]}Hello world!`
- `{[tom]:[sad:melancholy and nostalgic]}Welcome to our story.`

### Supported Emotions
- `calm`, `excited`, `sad`, `angry`, `surprised`, `afraid`, `disgusted`, `melancholic`

### Format Benefits
- **Numeric format**: Precise control over emotion intensity (0.0-1.0)
- **Descriptive format**: Natural language descriptions using IndexTTS2's Qwen emotion model
- **Backward compatibility**: Existing numeric format scripts continue to work
- **Mixed usage**: Both formats can be used in the same script

## 🔄 Integration Points

### n8n SSH Node Configuration
```bash
# Command for n8n SSH node
N8N_JSON='{{ $json }}' bash /path/to/ssh-indextts2-simple.sh "{{ $json.postId }}"
```

### External Tools Integration
- **Tools directory**: `/media/george/AI/my_share_folder/tools/`
- **SSH scripts**: `ssh-indextts2-simple.sh`, `n8n-indextts2-env.sh`
- **Documentation**: Comprehensive guides available

## 🎨 Generator Selection Guide

### Multi-Character Generator (Recommended)
- **Location**: `multi_person_support/scripts/multi_character_emotion_generator.py`
- **Use when**: Multiple characters, stories, complex narratives
- **Features**: Auto dialogue detection, voice differentiation, advanced emotions, stereo-to-mono conversion, enhanced text parsing, descriptive emotion support

### SSH/N8N Processor (Integration)
- **Location**: `multi_person_support/scripts/ssh_n8n_processor.py`
- **Use when**: Remote execution, n8n workflows, automation
- **Features**: SSH integration, JSON input/output, strict format validation, all new enhancements

### Basic Emotion Generator (Simple)
- **Location**: `multi_person_support/scripts/long_text_emotion_generator.py`
- **Use when**: Single voice, simple emotion control, quick tests
- **Features**: Straightforward emotion control, easy setup, basic stereo-to-mono conversion

## 📊 File Organization Benefits

### Before Organization
- Files scattered across project root
- Confusion between core and integration files
- Difficult to maintain and extend

### After Organization
- **Clear separation**: Core TTS vs. integration files
- **Logical structure**: Scripts, config, examples, docs separated
- **Easy maintenance**: Each component has dedicated location
- **No conflicts**: Integration files don't interfere with core system
- **Better documentation**: Organized docs with specific purposes

## 💡 Quick Start

### For Multi-Person Support
1. **Review multi-person documentation**: `multi_person_support/docs/README_SSH_TTS.md`
2. **Test with examples**: Use files in `multi_person_support/examples/`
3. **Configure characters**: Edit `multi_person_support/config/character_config.json`
4. **Run tests**: Use scripts in `multi_person_support/scripts/`
5. **🆕 New features**: Automatic stereo-to-mono conversion and enhanced text parsing work transparently

### For Core TTS Features
1. **Web interface**: `uv run webui.py`
2. **Command line**: `uv run indextts "text" -v voice.wav -o output.wav`
3. **Read main docs**: `README.md` for comprehensive guide

### 🆕 Testing New Features
```bash
# Test with both numeric and descriptive emotions
cd /media/george/AI/Voice/index-tts2
source .venv/bin/activate
uv run multi_person_support/scripts/multi_character_emotion_generator.py \
    --config multi_person_support/config/character_config.json \
    --script "{[narrator]:[calm:0.9]}我是旁白。\n{[sarah]:[excited:very enthusiastic]}我是Sarah！" \
    --output test_new_features.wav
```

## 🔍 Related Projects

### External Tools
- **SSH scripts**: `/media/george/AI/my_share_folder/tools/`
- **Audio samples**: `/media/george/AI/my_share_folder/山波声音采样20250824/`

### Model Files
- **HuggingFace**: `IndexTeam/IndexTTS-2`
- **ModelScope**: `IndexTeam/IndexTTS-2`

The project now has a clean, organized structure with clear separation between core TTS functionality and SSH/N8N integration capabilities!