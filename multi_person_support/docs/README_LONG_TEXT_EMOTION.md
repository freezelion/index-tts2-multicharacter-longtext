# Long Text Emotion Generator for IndexTTS2

This tool enables generation of long-form speech with dynamic emotion control using embedded emotion tags within text content.

## 🆕 NEW: Multi-Character Support!

We now have an enhanced version with multi-character support:
- **Multiple Character Voices**: Each character has unique voice parameters
- **Automatic Dialogue Detection**: Smart识别角色对话
- **Differentiated Emotions**: Dialogue emotions are stronger, narration emotions are more subtle
- **Character Profiles**: Individual pitch, speed, and volume settings

📖 **Multi-character version**: [README_MULTI_CHARACTER_EMOTION.md](README_MULTI_CHARACTER_EMOTION.md) - Advanced version with character voices

## Features

- **Emotion Tag Parsing**: Parse emotion tags embedded in text (e.g., `[happy]`, `[sad]`, `[angry]`)
- **Automatic Text Segmentation**: Break long text into manageable chunks for TTS processing
- **Smooth Emotion Transitions**: Handle emotion changes between text segments
- **Batch Processing**: Efficient generation of multiple audio segments
- **Multiple Input Formats**: Support for direct text input and text files
- **Configurable Parameters**: Adjustable emotion intensity, segment length, and processing options

## Installation

Ensure IndexTTS2 is properly installed with all dependencies:

```bash
uv sync --all-extras
```

## Usage

### Basic Usage

Generate from text with emotion tags:
```bash
uv run long_text_emotion_generator.py --voice examples/voice_01.wav --text "[happy]Hello world! [sad]Goodbye..." --output output.wav
```

Generate from text file:
```bash
uv run long_text_emotion_generator.py --voice examples/voice_01.wav --input examples/emotional_story_example.txt --output story.wav
```

### Advanced Usage

```bash
# With custom default emotion intensity and segment length
uv run long_text_emotion_generator.py \
  --voice examples/voice_01.wav \
  --input examples/podcast_example.txt \
  --output podcast.wav \
  --default-emo-alpha 0.6 \
  --segment-chars 150 \
  --cuda-kernel \
  --verbose
```

## Supported Emotions

### English Tags
- `[happy]`, `[happy:0.8]`, `[happiness]`, `[joy]`, `[excited]`
- `[sad]`, `[sad:0.5]`, `[sadness]`
- `[angry]`, `[angry:1.0]`, `[anger]`, `[rage]`, `[fury]`
- `[afraid]`, `[afraid:0.3]`, `[fear]`, `[scared]`, `[terrified]`
- `[disgusted]`, `[disgusted:0.7]`, `[disgust]`, `[revolted]`
- `[melancholic]`, `[melancholic:0.9]`, `[melancholy]`, `[depressed]`
- `[surprised]`, `[surprised:0.4]`, `[surprise]`, `[amazed]`, `[shocked]`
- `[calm]`, `[calm:0.6]`, `[neutral]`, `[normal]`, `[peaceful]`

### Chinese Tags
- `[高兴]`, `[高兴:0.7]`, `[快乐]`
- `[悲伤]`, `[悲伤:0.5]`, `[难过]`
- `[愤怒]`, `[愤怒:1.0]`, `[生气]`
- `[恐惧]`, `[恐惧:0.3]`, `[害怕]`
- `[反感]`, `[反感:0.8]`, `[厌恶]`
- `[低落]`, `[低落:0.9]`, `[忧郁]`
- `[惊讶]`, `[惊讶:0.4]`, `[吃惊]`
- `[自然]`, `[自然:0.6]`, `[平静]`

## Alpha Control

Each emotion tag can include an alpha value to control intensity:

**Format**: `[emotion:alpha]` where alpha is a float between 0.0 and 1.0

**Examples**:
- `[happy:0.2]` - Slight happiness (subtle)
- `[happy:0.5]` - Moderate happiness (balanced)
- `[happy:0.8]` - Strong happiness (noticeable)
- `[happy:1.0]` - Maximum happiness (intense)

**Alpha Value Guide**:
- `0.0-0.3`: Subtle, barely noticeable emotion
- `0.4-0.6`: Moderate, natural emotion
- `0.7-0.9`: Strong, clear emotion
- `1.0`: Maximum intensity emotion

If no alpha is specified, the default value from `--default-emo-alpha` is used (default: 0.8).

## Command Line Options

```
--voice, -v           Path to voice reference audio (required)
--text, -t            Input text with emotion tags
--input, -i           Input text file with emotion tags
--output, -o          Output audio file path (required)
--model-dir           Model directory (default: checkpoints)
--config              Model config file (default: checkpoints/config.yaml)
--default-emo-alpha   Default emotion intensity 0.0-1.0 (default: 0.8)
--segment-chars       Max characters per segment (default: 200)
--fp16                Use FP16 inference (default: True)
--cuda-kernel         Use CUDA kernel optimization
--deepspeed           Use DeepSpeed acceleration
--verbose             Enable verbose output
```

## Examples

### Storytelling
Create engaging stories with emotional narration:

```python
story = """
[happy]Once upon a time, in a beautiful forest...
[calm]The peaceful woods were home to many creatures...
[surprised]One day, something unexpected happened!
[afraid]A strange noise echoed through the trees...
[angry]The animals decided to investigate the disturbance...
[sad]They found their friend had fallen into a trap...
[happy]But working together, they rescued their friend!
[calm]And they all lived happily ever after.
"""
```

### Podcast/Audiobook
Produce professional audio content with emotional delivery:

```python
podcast = """
[calm]Welcome to today's episode of our podcast...
[happy]We have some exciting news to share with you...
[sad]In more somber news today...
[angry]I have to express my frustration about...
[surprised]And now for something completely unexpected!
[calm]Join us next time for more discussions...
"""
```

### Educational Content
Create engaging educational materials:

```python
lesson = """
[calm]Welcome to today's science lesson...
[happy]We're going to learn something fascinating today...
[surprised]Did you know that light can behave both as a wave and a particle?
[afraid]This concept might seem confusing at first...
[calm]But don't worry, we'll break it down step by step...
[happy]By the end of this lesson, you'll understand this amazing concept!
"""
```

## Technical Details

### Text Segmentation
The script automatically segments long text into chunks suitable for TTS processing:
- Default maximum segment length: 200 characters
- Splits at sentence boundaries when possible
- Maintains emotion consistency within segments
- Handles overlapping content for smooth transitions

### Emotion Processing
- Emotion tags are parsed and mapped to 8-dimensional vectors
- Per-tag emotion intensity using alpha values (e.g., `[happy:0.8]`)
- Default emotion intensity controlled by `--default-emo-alpha` parameter (0.0-1.0)
- Smooth transitions between different emotions
- Default emotion applied when no tags are present

### Audio Processing
- Generates individual audio segments for each text chunk
- Concatenates segments into final audio file
- Handles sample rate conversion automatically
- Preserves audio quality throughout processing

## Performance Tips

1. **GPU Acceleration**: Use `--cuda-kernel` for better performance on compatible hardware
2. **FP16 Inference**: Enable `--fp16` for faster processing (minimal quality impact)
3. **Segment Length**: Adjust `--segment-chars` based on your content (150-250 recommended)
4. **Emotion Intensity**: Start with `--default-emo-alpha 0.6` for more natural emotional delivery
5. **Memory Management**: Long texts may require substantial RAM for audio processing

## Error Handling

The script includes comprehensive error handling for:
- Missing or invalid audio files
- Model loading issues
- Text processing errors
- Audio generation failures
- Memory and resource constraints

## Examples Directory

Check the `examples/` folder for:
- `emotional_story_example.txt` - Story with multiple emotion changes
- `podcast_example.txt` - Podcast-style content demonstration
- `alpha_control_example.txt` - Demonstration of alpha intensity values

## Troubleshooting

### Common Issues

1. **Model Loading Errors**: Ensure model files are properly downloaded to `checkpoints/`
2. **Audio Generation Failures**: Check voice prompt format (WAV required) and file permissions
3. **Memory Issues**: Reduce segment length or close other memory-intensive applications
4. **Slow Processing**: Enable GPU acceleration options if available

### Debug Mode

Use `--verbose` flag for detailed processing information and error diagnostics.

## Integration

The script can be easily integrated into larger applications:
- Import `LongTextEmotionGenerator` class directly
- Use individual components (`EmotionTagParser`, `TextSegmenter`) separately
- Extend with custom emotion mappings or processing logic

## License

This tool is part of the IndexTTS2 project and follows the same license terms.