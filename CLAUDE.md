# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

IndexTTS2 is a state-of-the-art text-to-speech (TTS) system that provides emotionally expressive and duration-controlled auto-regressive zero-shot voice synthesis. It supports multiple languages including Chinese and English, with advanced features like voice cloning, emotional control, precise duration management, and multi-character dialogue generation.

## Development Environment

### Required Dependencies
- **Package Manager**: `uv` (required - o
ther managers like pip/conda are not supported)
- **Python**: >=3.10
- **CUDA**: 12.8+ recommended for GPU acceleration
- **Git LFS**: Required for large model files

### Installation Commands
```bash
# Install dependencies
uv sync --all-extras

# For Chinese users (mirror alternatives)
uv sync --all-extras --default-index "https://mirrors.aliyun.com/pypi/simple"
uv sync --all-extras --default-index "https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple"

# Check GPU detection
uv run tools/gpu_check.py
```

### Model Downloads
```bash
# Via HuggingFace
uv tool install "huggingface_hub[cli]"
hf download IndexTeam/IndexTTS-2 --local-dir=checkpoints

# Via ModelScope
uv tool install "modelscope"
modelscope download --model IndexTeam/IndexTTS-2 --local_dir checkpoints
```

## Key Commands

### Web Interface
```bash
# Launch WebUI (Gradio interface)
uv run webui.py

# With specific options
uv run webui.py --fp16 --deepspeed --cuda_kernel --port 7858 --host 0.0.0.0
```

### Command Line Interface
```bash
# Basic TTS synthesis
uv run indextts "Text to synthesize" -v voice.wav -o output.wav

# With options
uv run indextts "Hello world" -v examples/voice_01.wav -o gen.wav --fp16 --force

# Show CLI help
uv run indextts --help
```

### Python API Usage
```bash
# Run Python scripts with proper environment
PYTHONPATH="$PYTHONPATH:." uv run script.py

# Example with IndexTTS2
PYTHONPATH="$PYTHONPATH:." uv run indextts/infer_v2.py
```

### Testing
```bash
# Run regression tests
PYTHONPATH="$PYTHONPATH:." uv run tests/regression_test.py

# Run specific tests
PYTHONPATH="$PYTHONPATH:." uv run tests/padding_test.py
```

## Project Architecture

### Core Components

1. **IndexTTS2 Engine** (`indextts/infer_v2.py`):
   - Main inference class with advanced features
   - Supports emotional control via audio prompts or text descriptions
   - Implements duration control and voice cloning
   - Provides pure voice cloning mode for original sound quality

5. **Multi-Character Generator** (`multi_person_support/scripts/multi_character_emotion_generator.py`):
   - Advanced multi-character dialogue generation with emotional control
   - Supports automatic character detection and voice assignment
   - Handles both emotion vector and descriptive emotion processing
   - Includes speech rate optimization and audio format flexibility

2. **Legacy IndexTTS** (`indextts/infer.py`):
   - Previous generation model
   - Basic zero-shot TTS capabilities

3. **WebUI** (`webui.py`):
   - Gradio-based interface for easy experimentation
   - Supports all major features including emotion control

4. **CLI Tool** (`indextts/cli.py`):
   - Command-line interface for batch processing
   - Device auto-detection and error handling

### Model Architecture

- **GPT-based Autoregressive Model**: `indextts/gpt/`
- **VQ-VAE Encoder**: `indextts/vqvae/`
- **Speech-to-Mel Converter**: `indextts/s2mel/`
- **Utility Functions**: `indextts/utils/`

### Key Features

#### Voice Cloning
```python
from indextts.infer_v2 import IndexTTS2
tts = IndexTTS2(cfg_path="checkpoints/config.yaml", model_dir="checkpoints")
tts.infer(spk_audio_prompt='voice.wav', text="Hello world", output_path="output.wav")
```

#### Emotional Control
```python
# Via audio reference
tts.infer(spk_audio_prompt='voice.wav', text="Text", emo_audio_prompt="emotion.wav")

# Via emotion vector [happy, angry, sad, afraid, disgusted, melancholic, surprised, calm]
tts.infer(spk_audio_prompt='voice.wav', text="Text", emo_vector=[0, 0.95, 0, 0, 0, 0, 0, 0], emo_alpha=0.95)

# Pure voice cloning (no emotion processing) for original sound quality
tts.infer(spk_audio_prompt='voice.wav', text="Text", use_random=False, verbose=False)

# MP3 format output support
tts.infer(spk_audio_prompt='voice.wav', text="Text", output_path="output.mp3")

# Via text description
tts.infer(spk_audio_prompt='voice.wav', text="Text", use_emo_text=True, emo_text="Scary emotion")
```

#### Performance Options
- `--fp16`: Half-precision inference (faster, less VRAM)
- `--deepspeed`: DeepSpeed acceleration (system-dependent)
- `--cuda_kernel`: CUDA kernel optimization
- `--device`: Manual device selection (cpu, cuda, mps, xpu)
- `use_speed`: Speech rate control (0=normal, 1=fast)

#### Multi-Character Support
```bash
# Generate multi-character dialogue with emotions
PYTHONPATH="$PYTHONPATH:." uv run multi_person_support/scripts/multi_character_emotion_generator.py \
  --config multi_person_support/config/character_config.json \
  --input multi_person_support/examples/1_basic_story.json \
  --output story.wav

# Supports both WAV and MP3 output formats
--output story.wav  # WAV format
--output story.mp3  # MP3 format
```

## File Structure

```
index-tts2/
├── indextts/              # Core TTS modules
│   ├── gpt/               # GPT model components
│   ├── vqvae/             # VQ-VAE encoder
│   ├── s2mel/             # Speech-to-mel converter
│   └── utils/             # Utility functions
├── multi_person_support/  # Multi-character dialogue system
│   ├── scripts/          # Multi-character generator
│   ├── config/           # Character configurations
│   ├── examples/         # Dialogue examples
│   └── docs/             # Documentation
├── checkpoints/           # Model files and config
├── examples/             # Example audio files
├── tests/                # Test scripts
├── tools/                # Utility tools
├── webui.py              # Gradio web interface
└── pyproject.toml        # Project configuration
```

## Configuration

### Environment Variables
```bash
# For slow HuggingFace access
export HF_ENDPOINT="https://hf-mirror.com"

# Model cache location
export HF_HUB_CACHE='./checkpoints/hf_cache'
```

### Required Model Files
- `config.yaml` - Model configuration
- `gpt.pth` - Main GPT model weights
- `s2mel.pth` - Speech-to-mel converter weights
- `bpe.model` - Tokenizer model
- `wav2vec2bert_stats.pt` - Audio feature extractor statistics

## Development Notes

### Code Execution
- Always use `uv run` for Python execution to ensure proper environment
- Add current directory to `PYTHONPATH` for module imports
- Model files should be in `./checkpoints/` directory

### Performance Considerations
- FP16 inference recommended for most use cases (quality impact is minimal)
- DeepSpeed performance varies by system - test with/without
- CUDA kernels can provide significant speedups on compatible hardware
- Use high-quality stereo audio files for best voice cloning results
- MP3 format provides smaller file sizes with minimal quality loss
- Multi-character generator optimizes speech rate automatically based on character settings

### Multi-language Support
- Chinese/English mixed text processing
- Pinyin annotation support for precise pronunciation control
- Cross-lingual voice cloning capabilities
- Emotion vector format: [happy, angry, sad, afraid, disgusted, melancholic, surprised, calm]

### Audio Format Support
- **WAV**: Uncompressed audio format (highest quality)
- **MP3**: Compressed audio format (smaller file size)
- Automatic format detection based on file extension
- Stereo audio recommended for best voice cloning results

### Error Handling
- Comprehensive validation of model files and audio inputs
- Automatic device detection with fallback options
- Graceful degradation for missing optional features
- Emotion vector order validation to prevent incorrect emotion mapping
- Speech rate optimization to prevent slow audio playback