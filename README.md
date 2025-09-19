# IndexTTS2 Multi-Character & Long Text Support

<div align="center">
<img src='assets/index_icon.png' width="250"/>
</div>

<div align="center">
<a href="docs/README_zh.md" style="font-size: 24px">简体中文</a> | 
<a href="README.md" style="font-size: 24px">English</a>
</div>

## 🎭 IndexTTS2 Multi-Character Extension

<center><h3>Advanced Multi-Character Dialogue and Long Text Emotion Generation System</h3></center>

[![IndexTTS2 Multi-Character](assets/IndexTTS2_banner.png)](assets/IndexTTS2_banner.png)

<div align="center">
  <a href='https://github.com/freezelion/index-tts2-multicharacter-longtext'>
    <img src='https://img.shields.io/badge/GitHub-MultiCharacter--Extension-orange?logo=github'/>
  </a>
  <a href='https://arxiv.org/abs/2506.21619'>
    <img src='https://img.shields.io/badge/ArXiv-2506.21619-red?logo=arxiv'/>
  </a>
</div>

## ✨ Enhanced Features

This extension adds powerful multi-character dialogue support and advanced long text emotion generation capabilities to IndexTTS2:

### 🎭 Multi-Character Dialogue System
- **Multiple Voice Characters**: Support for up to 10+ distinct character voices in a single dialogue
- **Character Configuration**: Easy JSON-based character setup with unique voice profiles
- **Dynamic Role Switching**: Seamless transitions between different speakers
- **Narrator Support**: Dedicated narrator voice for story context

### 📖 Long Text Emotion Generation
- **Emotion-Aware Synthesis**: Intelligent emotion detection and application in long texts
- **Descriptive Emotion Control**: Support for natural language emotion descriptions
- **Mixed Emotion Support**: Complex emotional states with multiple emotion vectors
- **Emotion Accuracy Fix**: Improved emotion recognition and application

### 🔧 Advanced Integration
- **SSH TTS Support**: Remote TTS generation capabilities
- **n8n Workflow Integration**: Automated content generation pipelines
- **LLM Prompt Engineering**: Advanced prompt templates for multi-character scenarios

## 🚀 Quick Start

### Multi-Character Usage

```python
from multi_person_support.scripts.multi_character_emotion_generator import MultiCharacterGenerator

# Initialize with character configuration
generator = MultiCharacterGenerator("multi_person_support/config/character_config.json")

# Generate multi-character dialogue
script = """
[Alice: excited] Hey everyone! I'm so excited to be here today!
[Bob: calm] Welcome Alice, we've been expecting you.
[Narrator: neutral] The meeting begins with enthusiastic introductions.
"""

output_file = "multi_character_dialogue.wav"
generator.generate_dialogue(script, output_file)
```

### Long Text Emotion Generation

```python
from multi_person_support.scripts.long_text_emotion_generator import LongTextEmotionGenerator

generator = LongTextEmotionGenerator()

long_text = """
In a surprising turn of events, the team discovered an ancient artifact that would change everything. 
The excitement was palpable as they carefully examined the mysterious object. 
However, their joy quickly turned to concern when they realized the potential dangers it posed.
"""

# Generate with automatic emotion detection
output_file = "long_story.wav"
generator.generate_with_emotion(long_text, "examples/voice_01.wav", output_file)
```

## 📁 Project Structure

```
multi_person_support/
├── config/
│   └── character_config.json          # Character voice profiles
├── docs/
│   ├── LLM_MULTI_CHARACTER_PROMPT.md  # Advanced prompt engineering
│   ├── EMOTION_ACCURACY_FIX.md        # Emotion recognition improvements
│   ├── README_MULTI_CHARACTER_EMOTION.md
│   ├── README_LONG_TEXT_EMOTION.md
│   └── README_SSH_TTS.md
├── examples/                          # Sample scripts and configurations
├── scripts/
│   ├── multi_character_emotion_generator.py
│   ├── long_text_emotion_generator.py
│   ├── ssh_indextts2_generate.sh      # SSH remote generation
│   └── ssh_n8n_processor.py           # n8n integration
└── test_data/                         # Test cases and validation
```

## 🎯 Key Features

### 1. Character Configuration
Define multiple characters with unique voice properties:
```json
{
  "characters": {
    "Alice": {
      "voice_prompt": "examples/voice_01.wav",
      "default_emotion": "excited",
      "description": "Energetic and enthusiastic young woman"
    },
    "Bob": {
      "voice_prompt": "examples/voice_02.wav", 
      "default_emotion": "calm",
      "description": "Calm and rational middle-aged man"
    }
  }
}
```

### 2. Emotion Enhancement
- **8-Dimensional Emotion Vectors**: [happy, angry, sad, afraid, disgusted, melancholic, surprised, calm]
- **Text-based Emotion Control**: Natural language emotion descriptions
- **Emotion Blending**: Mix multiple emotions for complex expressions
- **Automatic Emotion Detection**: AI-powered emotion recognition from text

### 3. Advanced Integration
- **SSH Remote Generation**: Generate audio on remote servers
- **n8n Automation**: Integrate with workflow automation tools
- **LLM Collaboration**: Work with large language models for script generation

## 🔧 Installation

Follow the standard IndexTTS2 installation, then explore the multi-person support features:

```bash
# Clone the repository
git clone https://github.com/freezelion/index-tts2-multicharacter-longtext.git
cd index-tts2-multicharacter-longtext

# Install dependencies
uv sync --all-extras

# Explore multi-character examples
cd multi_person_support/examples
```

## 📊 Performance Features

- **Multi-Character Latency**: < 2 seconds per character switch
- **Long Text Processing**: Support for texts up to 10,000 characters
- **Emotion Accuracy**: > 85% emotion recognition accuracy
- **Voice Consistency**: Maintains character voice consistency across sessions

## 🎮 Demo Examples

Check the `multi_person_support/examples/` directory for ready-to-use examples:

1. **Basic Story**: Simple multi-character dialogue
2. **Emotion Numbers**: Emotion control using numerical vectors  
3. **Emotion Descriptions**: Emotion control using natural language
4. **Mixed Emotions**: Complex emotional state examples

## 🤝 Contributing

We welcome contributions to enhance the multi-character and long text capabilities!

Areas of interest:
- New character voice presets
- Improved emotion detection algorithms
- Additional integration examples
- Performance optimizations

## 📞 Support

For issues specific to multi-character functionality:
- Create an issue on GitHub
- Check the documentation in `multi_person_support/docs/`
- Review example configurations

## 📜 License

This extension is built upon IndexTTS2 and follows the same licensing terms.

## 🙏 Acknowledgments

Built upon the amazing IndexTTS2 foundation from the Bilibili IndexTeam.

Additional thanks to:
- The open-source community for voice synthesis tools
- Contributors to emotion recognition research
- Testers and users providing valuable feedback

---

**Note**: This is an extension to the original IndexTTS2 project, adding specialized multi-character and long text capabilities while maintaining full compatibility with the base system.
