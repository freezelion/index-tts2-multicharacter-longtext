# IndexTTS2 Multi-Person Examples

This directory contains structured examples demonstrating different features of the IndexTTS2 multi-person long text support system.

## Example Files

### 1. `1_basic_story.json` - Basic Story Without Emotions
- **Purpose**: Simple multi-character dialogue without explicit emotion tags
- **Features**: Basic character voice differentiation
- **Use Case**: Simple narratives where default emotions are sufficient

### 2. `2_emotion_numbers.json` - Numeric Emotion Intensity
- **Purpose**: Same story with numeric emotion values (0.0-1.0)
- **Features**: Precise emotion control using numeric intensity
- **Use Case**: When you need exact control over emotion strength

### 3. `3_emotion_descriptions.json` - Descriptive Emotion Text
- **Purpose**: Same story with natural language emotion descriptions
- **Features**: Uses IndexTTS2's Qwen emotion model for natural expression
- **Use Case**: When you want more natural, nuanced emotional expression

### 4. `4_mixed_emotions.json` - Multiple Characters with Mixed Emotions
- **Purpose**: Complex scene with 4 characters using both emotion formats
- **Features**: Demonstrates both numeric and descriptive emotions in one script
- **Use Case**: Complex narratives with multiple emotional states

## Usage

```bash
# Test any example
cd /media/george/AI/Voice/index-tts2
source .venv/bin/activate
uv run integration/scripts/multi_character_emotion_generator.py \
    --config integration/config/character_config.json \
    --input integration/examples/1_basic_story.json \
    --output test_example.wav
```

## Emotion Format Comparison

| Format | Example | Advantage | Use Case |
|--------|---------|-----------|----------|
| None (Default) | Basic dialogue | Simple to use | Simple narratives |
| Numeric | `[angry:0.8]` | Precise control | Technical applications |
| Descriptive | `[angry:very frustrated]` | Natural expression | Creative content |
| Mixed | Both formats | Maximum flexibility | Complex scenes |

## Tips

- Start with basic story to test character voice differentiation
- Use numeric emotions for precise control
- Use descriptive emotions for more natural expression
- Mix formats in complex scenes for maximum flexibility
- All examples use the same basic story structure for easy comparison