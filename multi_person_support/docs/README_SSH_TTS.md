# SSH/N8N TTS Processor for IndexTTS2

This solution allows you to execute TTS commands via SSH using n8n node output data. It supports multi-character scripts with emotion tags and generates high-quality audio files.

## Features

- **Multi-character support**: Process scripts with multiple voice characters
- **Emotion control**: Parse and apply emotion tags with intensity levels
- **SSH integration**: Secure remote execution via SSH
- **Error handling**: Comprehensive error handling and retry logic
- **Logging**: Detailed logging for debugging and monitoring
- **Flexible input**: Support for both JSON files and direct JSON strings

## Files Created

1. **`ssh_n8n_processor.py`** - Main Python processor for TTS generation
2. **`ssh_indextts2_generate.sh`** - Bash wrapper script for SSH execution
3. **`examples/ssh_n8n_data.json`** - Sample n8n data for testing

## Usage

### Method 1: Using JSON File (Recommended)

```bash
# From local system
bash ssh_indextts2_generate.sh --input examples/ssh_n8n_data.json --output output.wav

# Via SSH
ssh user@server "cd /path/to/index-tts2 && bash ssh_indextts2_generate.sh --input examples/ssh_n8n_data.json --output output.wav"
```

### Method 2: Using Direct JSON String

```bash
# From local system
bash ssh_indextts2_generate.sh --input '{"output": {"character_config": {...}, "script_content": "..."}}' --output output.wav

# Via SSH
ssh user@server "cd /path/to/index-tts2 && bash ssh_indextts2_generate.sh --input '$(cat n8n_data.json)' --output output.wav"
```

### Method 3: Direct Python Script

```bash
# Using the Python processor directly
uv run ssh_n8n_processor.py --config character_config.json --input-json examples/ssh_n8n_data.json --output output.wav

# Using direct script input with new strict format
uv run ssh_n8n_processor.py --config character_config.json --script "{[narrator]:[calm:0.3]}Hello world" --output output.wav
```

## Input Format

The system expects n8n output data in this format:

```json
{
  "output": {
    "character_config": {
      "characters": {
        "character_id": {
          "name": "Character Name",
          "voice_file": "path/to/voice.wav",
          "pitch": 0.0,
          "speech_rate": 1.0,
          "volume": 1.0,
          "emotion_intensity": 0.8
        }
      }
    },
    "script_content": "{[character]:[emotion:intensity]}Text content\n{[character2]:[emotion:intensity]}More text"
  }
}
```

## Script Format

The script content uses a strict format:

- **Strict character format**: `{[character]:[emotion:intensity]}` (required)
- **Character names**: narrator, sarah, tom, etc. (defined in config)
- **Emotion tags**: calm, excited, sad, angry, afraid, disgusted, surprised, melancholic
- **Intensity levels**: 0.0 to 1.0 (float values supported)

Example with new strict format:
```
{[narrator]:[calm:0.3]}Once upon a time...
{[sarah]:[excited:0.8]}Hello world!
{[tom]:[calm:0.7]}Welcome to our story.
```

**Important**: Only the strict format `{[character]:[emotion:intensity]}` is supported. Other formats will be treated as regular text.

## Configuration

### Environment Variables

- `SSH_TTS_CONFIG` - Alternative character config file path
- `SSH_TTS_MODEL` - Alternative model directory path
- `SSH_TTS_LOG` - Alternative log file path

### Voice Files

Ensure all voice files referenced in the character configuration exist in the specified paths:

- `2.语速比较快的讲解女声Haa.wav`
- `口播男声.wav`
- `audiobook_prompt.wav`

## SSH Integration

### Setup SSH Access

1. **SSH Key Authentication** (recommended):
```bash
ssh-keygen -t rsa -b 4096
ssh-copy-id user@server
```

2. **Test SSH Connection**:
```bash
ssh user@server "cd /path/to/index-tts2 && ls -la"
```

### Execute TTS via SSH

```bash
# Single command execution
ssh user@server "cd /path/to/index-tts2 && ./ssh_tts_executor.sh --input examples/ssh_n8n_data.json --output remote_output.wav"

# Copy result back
scp user@server:/path/to/index-tts2/remote_output.wav ./local_output.wav
```

### n8n SSH Node Configuration

1. **SSH Connection**:
   - Host: your server IP/hostname
   - Port: 22 (default)
   - Authentication: SSH key or password

2. **Command**:
   ```bash
   cd /path/to/index-tts2 && ./ssh_tts_executor.sh --input /tmp/n8n_data.json --output /tmp/output.wav
   ```

3. **File Transfer**:
   - Upload JSON data to `/tmp/n8n_data.json`
   - Execute TTS command
   - Download resulting audio file

## Error Handling

The system includes comprehensive error handling:

- **Retry Logic**: Automatically retries failed operations (configurable)
- **Validation**: Validates input data and required files
- **Logging**: Detailed logging to `/path/to/index-tts2/ssh_tts.log`
- **Graceful Degradation**: Continues with default configuration if issues occur

## Performance Optimization

- **FP16 Inference**: Uses half-precision for faster generation
- **Memory Management**: Efficient memory usage with proper cleanup
- **Batch Processing**: Processes text in segments for better performance
- **Parallel Execution**: Supports parallel processing of multiple segments

## Security Considerations

- **Input Validation**: All input data is validated before processing
- **File Path Security**: Prevents directory traversal attacks
- **Resource Limits**: Configurable limits on processing time and memory
- **Logging**: Secure logging without sensitive information

## Troubleshooting

### Common Issues

1. **Permission Errors**: Ensure the SSH user has read/write permissions
2. **Missing Dependencies**: Check that `uv` and all Python packages are installed
3. **Model Files**: Verify all model files exist in the checkpoints directory
4. **Voice Files**: Ensure referenced voice files exist

### Debug Mode

Enable verbose logging:
```bash
./ssh_tts_executor.sh --input examples/ssh_n8n_data.json --output debug.wav --verbose
```

Check log file:
```bash
tail -f /path/to/index-tts2/ssh_tts.log
```

## Examples

### Simple Two-Character Dialogue

```bash
./ssh_tts_executor.sh --input '{
  "output": {
    "character_config": {
      "characters": {
        "alice": {
          "name": "Alice",
          "voice_file": "examples/voice_01.wav",
          "pitch": 0.0,
          "speech_rate": 1.0,
          "volume": 1.0,
          "emotion_intensity": 0.8
        },
        "bob": {
          "name": "Bob",
          "voice_file": "examples/voice_02.wav",
          "pitch": 0.0,
          "speech_rate": 1.0,
          "volume": 1.0,
          "emotion_intensity": 0.8
        }
      }
    },
    "script_content": "alice: [happy:0.8]Hello Bob, how are you today?\nbob: [calm:0.7]I'\''m doing well, Alice! How about you?"
  }
}' --output simple_dialogue.wav
```

### Complex Multi-Character Story

```bash
./ssh_tts_executor.sh --input examples/ssh_n8n_data.json --output story.wav
```

## Support

For issues and questions, check the log file and ensure all dependencies are properly installed.