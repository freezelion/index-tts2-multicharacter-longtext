# Multi-Person Long Text Support for IndexTTS2

This directory contains all the multi-person long text support files for IndexTTS2, organized to avoid confusion with the original project code.

## 📁 File Structure

```
multi_person_support/
├── scripts/           # Core processing scripts
│   ├── ssh_n8n_processor.py          # Main Python processor for TTS generation
│   ├── ssh_indextts2_generate.sh     # Bash wrapper script
│   ├── long_text_emotion_generator.py    # Single-voice generator
│   └── multi_character_emotion_generator.py # Multi-character system
├── examples/          # Structured example files
│   ├── 1_basic_story.json              # Basic story without emotions
│   ├── 2_emotion_numbers.json          # Numeric emotion intensity
│   ├── 3_emotion_descriptions.json     # Descriptive emotion text
│   ├── 4_mixed_emotions.json           # Mixed emotion formats
│   └── README_examples.md               # Examples guide
└── docs/              # Documentation
    ├── README_SSH_TTS.md               # Comprehensive SSH TTS guide
    └── LLM_MULTI_CHARACTER_PROMPT.md   # LLM prompt for multi-character generation
```

## 🚀 Quick Start

### ⚠️ Important: Virtual Environment Required

**Before running any scripts, you must activate the virtual environment:**

```bash
cd /media/george/AI/Voice/index-tts2
source .venv/bin/activate
```

### Using the Scripts

1. **Direct Python Script Usage**:
```bash
# With text input (requires --config)
cd /media/george/AI/Voice/index-tts2
source .venv/bin/activate
uv run multi_person_support/scripts/ssh_n8n_processor.py \
    --config multi_person_support/config/character_config.json \
    --script "{[narrator]:[calm:0.3]}Hello world" \
    --output output.wav

# With JSON input (self-contained, no --config needed)
uv run multi_person_support/scripts/ssh_n8n_processor.py \
    --input-json multi_person_support/examples/1_basic_story.json \
    --output output.wav
```

2. **Bash Wrapper Script**:
```bash
cd /media/george/AI/Voice/index-tts2
source .venv/bin/activate
bash multi_person_support/scripts/ssh_indextts2_generate.sh \
    --input multi_person_support/examples/1_basic_story.json \
    --output output.wav
```

### Testing with Examples

```bash
# Test with basic story (no emotions)
cd /media/george/AI/Voice/index-tts2
source .venv/bin/activate
bash multi_person_support/scripts/ssh_indextts2_generate.sh \
    --input multi_person_support/examples/1_basic_story.json \
    --output multi_person_support/generated/1_basic_story_test.wav

# Test with numeric emotions
uv run multi_person_support/scripts/multi_character_emotion_generator.py \
    --input multi_person_support/examples/2_emotion_numbers.json \
    --output multi_person_support/generated/2_emotion_numbers_test.wav

# Test with descriptive emotions
uv run multi_person_support/scripts/multi_character_emotion_generator.py \
    --input multi_person_support/examples/3_emotion_descriptions.json \
    --output multi_person_support/generated/3_emotion_descriptions_test.wav

# Test with mixed emotions (multiple characters)
uv run multi_person_support/scripts/multi_character_emotion_generator.py \
    --input multi_person_support/examples/4_mixed_emotions.json \
    --output multi_person_support/generated/4_mixed_emotions_test.wav

# Test with text input (requires --config)
uv run multi_person_support/scripts/multi_character_emotion_generator.py \
    --config multi_person_support/config/character_config.json \
    --text "{[narrator]:[calm:0.3]}Hello world" \
    --output multi_person_support/generated/test_text.wav
```

## 📋 Format Specifications

### Character Format (Enhanced!)
All character lines must use one of these formats:
```
{[character_name]:[emotion:intensity]}Text content
{[character_name]:[emotion:description]}Text content
```

**Two Formats Supported**:

1. **Numeric Intensity Format** (Original):
   - `{[narrator]:[calm:0.3]}Once upon a time...`
   - `{[sarah]:[excited:0.8]}Hello world!`
   - `{[tom]:[calm:0.7]}Welcome to our story.`

2. **Descriptive Emotion Format** (New!):
   - `{[narrator]:[calm:very peaceful and calm]}Once upon a time...`
   - `{[sarah]:[excited:very excited and enthusiastic]}Hello world!`
   - `{[tom]:[calm:calm and professional]}Welcome to our story.`

### Supported Emotions
- `calm`, `excited`, `sad`, `angry`, `surprised`, `afraid`, `disgusted`, `melancholic`

### Format Specifications

**Numeric Intensity Format**:
- **Range**: `0.0` to `1.0` (float values supported)
- **Use Case**: Precise control over emotion intensity
- **Example**: `{[narrator]:[calm:0.9]}` (very calm)

**Descriptive Emotion Format**:
- **Format**: Natural language descriptions
- **Use Case**: More expressive, natural emotion control
- **Advantage**: Uses IndexTTS2's Qwen emotion model for better voice adaptation
- **Examples**:
  - `{[narrator]:[calm:very peaceful and serene]}`
  - `{[sarah]:[excited:extremely enthusiastic and energetic]}`
  - `{[tom]:[sad:melancholy and nostalgic]}`

### Backward Compatibility
- Existing scripts with numeric intensity continue to work unchanged
- New descriptive format provides enhanced emotion expression
- Both formats can be mixed in the same script

## 🔧 Integration Points

### n8n SSH Node Configuration
```bash
# Command for n8n SSH node (self-contained JSON input)
N8N_JSON='{{ $json }}' bash /path/to/ssh-indextts2-simple.sh "{{ $json.postId }}"
```

### Environment Variables
- `N8N_JSON`: Complete n8n output data
- `SSH_TTS_CONFIG`: Alternative character config path
- `SSH_TTS_MODEL`: Alternative model directory path
- `SSH_TTS_LOG`: Alternative log file path

## 📖 Documentation

- **SSH TTS Guide**: `multi_person_support/docs/README_SSH_TTS.md`
- **LLM Prompt Guide**: `multi_person_support/docs/LLM_MULTI_CHARACTER_PROMPT.md`
- **Examples Guide**: `multi_person_support/examples/README_examples.md`
- **Tools Documentation**: `/media/george/AI/my_share_folder/tools/README.md`

## 🎯 Key Features

- **Multi-character support**: Process scripts with multiple voice characters
- **Emotion control**: Parse and apply emotion tags with intensity levels
- **SSH integration**: Secure remote execution via SSH
- **Error handling**: Comprehensive error handling and retry logic
- **Strict format**: Enforces exact `{[character]:[emotion:intensity]}` format
- **Flexible input**: Support for both JSON files and direct script input
- **Automatic stereo-to-mono conversion**: Automatically converts stereo voice samples to mono for optimal IndexTTS2 compatibility
- **Enhanced text parsing**: Improved text content extraction for accurate audio generation
- **Descriptive emotion support**: Natural language emotion descriptions via Qwen emotion model

## 🔍 Related Files

The multi-person support scripts work with these core IndexTTS2 files:
- `multi_character_emotion_generator.py` - Core TTS generation engine
- `character_config.json` - Character voice configuration
- `checkpoints/` - Model files and configuration

## ⚠️ Important Notes

- All multi-person support scripts are self-contained and won't interfere with original IndexTTS2 code
- The system maintains strict format validation to prevent parsing errors
- Virtual environment (.venv) is automatically activated when running scripts
- All file paths are relative to the IndexTTS2 project root
- **Voice sample requirements**: Audio files are automatically converted to mono if needed (IndexTTS2 requires mono input)
- **Text content extraction**: Enhanced parsing ensures only actual text content is spoken, not character tags
- **Mixed format support**: Both numeric (`[calm:0.9]`) and descriptive (`[excited:very enthusiastic]`) emotions work seamlessly