#!/usr/bin/env python3
"""
Multi-Character Long Text Generator with Emotion Tags for IndexTTS2

This script enables generation of long-form speech with multiple characters,
dynamic emotion control, and advanced voice parameters. It supports:

Features:
- Multiple character voices with unique configurations
- Character-specific emotion tags and parameters
- Automatic dialogue detection and separation
- Different emotion intensity for dialogue vs narration
- Character voice profiles (pitch, speed, volume)
- Automatic text segmentation with character awareness
- Smooth emotion transitions between segments
- Configurable segment length and overlap
- Support for all IndexTTS2 emotions
- Batch processing for efficiency

Usage:
    python multi_character_emotion_generator.py --config character_config.json --input "story.txt" --output "output.wav"
    python multi_character_emotion_generator.py --config character_config.json --text "narrator: [calm]Once upon a time... \"ailin: [happy]Hello world!\"" --output "output.wav"
"""

import os
import re
import sys
import argparse
import json
from typing import List, Dict, Tuple, Optional, NamedTuple, Union
import tempfile
import shutil
from pathlib import Path
from dataclasses import dataclass
import copy

# Add current directory to path for IndexTTS imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, "indextts"))

try:
    from indextts.infer_v2 import IndexTTS2
    import torch
    import torchaudio
    import librosa
    import numpy as np
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please ensure IndexTTS2 is properly installed with 'uv sync --all-extras'")
    sys.exit(1)


@dataclass
class CharacterConfig:
    """Character configuration with voice and emotion parameters"""
    name: str
    voice_file: str
    default_emotion: str = "calm"
    emotion_intensity: float = 0.5
    speech_rate: float = 1.0
    pitch: float = 1.0
    volume: float = 1.0
    description: str = ""


@dataclass
class DialogueSegment:
    """Dialogue segment with character and emotion information"""
    text: str
    character: str
    emotion: str
    alpha: float
    is_dialogue: bool
    position: int
    emo_text: Optional[str] = None  # For descriptive emotion text


class CharacterDialogueParser:
    """Parse character dialogue and emotions from text"""

    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)
        self.characters = self._parse_characters()
        self.dialogue_patterns = self.config.get('dialogue_patterns', {})
        self.narration_settings = self.config.get('narration_settings', {})
        self.dialogue_settings = self.config.get('dialogue_settings', {})

    def load_config(self, config_path: str) -> Dict:
        """Load character configuration from JSON file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Configuration file {config_path} not found")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error parsing configuration file: {e}")
            sys.exit(1)

    def _parse_characters(self) -> Dict[str, CharacterConfig]:
        """Parse character configurations"""
        characters = {}
        for char_id, char_data in self.config.get('characters', {}).items():
            characters[char_id] = CharacterConfig(**char_data)
        return characters

    def parse_text_with_characters(self, text: str) -> List[DialogueSegment]:
        """Parse text and identify dialogue segments with characters"""
        segments = []
        lines = text.split('\n')
        position = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Pattern to find all character tags and their positions: {[character]:[emotion:value]}
            char_pattern = r'(\{\[\w+\]:\[\w+:[^\]]+\]\})'

            # Find all matches with their positions
            matches = list(re.finditer(char_pattern, line))

            # If no character tags found, treat as narration
            if not matches:
                segments.append(DialogueSegment(
                    text=line,
                    character='narrator',  # Default to narrator
                    emotion='calm',
                    alpha=0.0,  # Use no emotion for plain text to avoid affecting speech rate
                    is_dialogue=False,
                    position=position
                ))
                position += 1
                continue

            # Process text before first tag as narration
            first_match = matches[0]
            if first_match.start() > 0:
                pre_text = line[:first_match.start()].strip()
                if pre_text:
                    segments.append(DialogueSegment(
                        text=pre_text,
                        character='narrator',
                        emotion='calm',
                        alpha=0.0,  # Use no emotion for plain text to avoid affecting speech rate
                        is_dialogue=False,
                        position=position
                    ))
                    position += 1

            # Process each character tag and its following text
            for i, match in enumerate(matches):
                # Extract character info from tag
                tag_text = match.group(1)
                char_id, emotion, value, tag_content = self._extract_character_content(tag_text)

                # Find the text after this tag until next tag or end of line
                start_pos = match.end()
                if i + 1 < len(matches):
                    end_pos = matches[i + 1].start()
                    following_text = line[start_pos:end_pos].strip()
                else:
                    following_text = line[start_pos:].strip()

                if char_id in self.characters and following_text:
                    # Check if value is numeric (intensity) or descriptive text
                    if isinstance(value, str):
                        # Descriptive emotion text
                        segments.append(DialogueSegment(
                            text=following_text,
                            character=char_id,
                            emotion=emotion,
                            alpha=0.8,  # Default alpha for descriptive emotions
                            is_dialogue=True,
                            position=position,
                            emo_text=f"{emotion}: {value}"  # Combine emotion type with description
                        ))
                    else:
                        # Numeric intensity
                        segments.append(DialogueSegment(
                            text=following_text,
                            character=char_id,
                            emotion=emotion,
                            alpha=value,
                            is_dialogue=True,
                            position=position
                        ))
                    position += 1
                else:
                    # Treat as narration if character not found or no following text
                    if isinstance(value, str):
                        segments.append(DialogueSegment(
                            text=following_text,
                            character='narrator',
                            emotion=emotion,
                            alpha=0.8,
                            is_dialogue=False,
                            position=position,
                            emo_text=f"{emotion}: {value}"
                        ))
                    else:
                        segments.append(DialogueSegment(
                            text=following_text,
                            character='narrator',
                            emotion=emotion,
                            alpha=value,
                            is_dialogue=False,
                            position=position
                        ))
                    position += 1

        return segments

    def _has_character_prefix(self, line: str) -> bool:
        """Check if line has the required strict character prefix format"""
        # Accept both formats: {[character]:[emotion:intensity]} and {[character]:[emotion:description]}
        pattern = r'^\{\[(\w+)\]:\[(\w+):([^\]]+)\]\}'
        return bool(re.match(pattern, line))

    def _extract_character_content(self, line: str) -> Tuple[str, str, str, Union[float, str]]:
        """Extract character ID, emotion, intensity/description, and content from strict format line"""
        # Format: {[character]:[emotion:intensity]}content or {[character]:[emotion:description]}content
        pattern = r'^\{\[(\w+)\]:\[(\w+):([^\]]+)\]\}(.*)'
        match = re.match(pattern, line)
        if match:
            character = match.group(1)
            emotion = match.group(2)
            value = match.group(3)
            content = match.group(4).strip()

            # Check if value is numeric (intensity) or descriptive text
            try:
                intensity = float(value)
                intensity = max(0.0, min(1.0, intensity))
                return character, emotion, intensity, content
            except ValueError:
                # Value is descriptive text
                return character, emotion, value, content
        else:
            # Return default values if line doesn't match required format
            # Use alpha 0.0 for plain text to avoid emotion processing affecting speech rate
            return 'narrator', 'calm', 0.0, line

    def _extract_dialogue_from_text(self, line: str) -> List[Dict]:
        """Extract dialogue parts from mixed text"""
        parts = []
        # Support both Chinese and English quotation marks
        dialogue_pattern = r'([^\"]*)(\"[^\"]*\")([^\"]*)'
        chinese_pattern = r'([^\「]*)(\「[^\」]*\」)([^\「]*)'

        # Try Chinese quotes first
        matches = re.findall(chinese_pattern, line)
        if matches:
            for match in matches:
                if match[0].strip():
                    parts.append({'text': match[0].strip(), 'is_dialogue': False})
                if match[1].strip():
                    parts.append({'text': match[1].strip('「」'), 'is_dialogue': True})
                if match[2].strip():
                    parts.append({'text': match[2].strip(), 'is_dialogue': False})
        else:
            # Try English quotes
            matches = re.findall(dialogue_pattern, line)
            for match in matches:
                if match[0].strip():
                    parts.append({'text': match[0].strip(), 'is_dialogue': False})
                if match[1].strip():
                    parts.append({'text': match[1].strip('"'), 'is_dialogue': True})
                if match[2].strip():
                    parts.append({'text': match[2].strip(), 'is_dialogue': False})

        return parts if parts else [{'text': line, 'is_dialogue': False}]

    def _identify_dialogue_character(self, dialogue_text: str) -> str:
        """Identify character based on dialogue content and context"""
        # Simple heuristics - can be enhanced with NLP
        text_lower = dialogue_text.lower()

        if any(word in text_lower for word in ['艾琳', '我', '我们']):
            return 'ailin'
        elif any(word in text_lower for word in ['指挥官', '母舰', '基地']):
            return 'commander'
        elif any(word in text_lower for word in ['守护者', '保护', '平衡']):
            return 'guardian'
        elif any(word in text_lower for word in ['公司', '矿业', '商业']):
            return 'company'
        else:
            return 'ailin'  # Default to main character

    def _parse_emotion_tags(self, text: str) -> Tuple[str, float, str]:
        """Parse emotion tags and return emotion, alpha, and cleaned text"""
        # Support multiple tag formats: [emotion:alpha], {emotion:alpha}, <emotion:alpha>
        tag_patterns = [
            r'\[([^\]]+):([0-9.]+)\]',
            r'\{([^\}]+):([0-9.]+)\}',
            r'<([^>]+):([0-9.]+)>',
            r'\[([^\]]+)\]',
            r'\{([^\}]+)\}',
            r'<([^>]+)>'
        ]

        for pattern in tag_patterns:
            matches = re.findall(pattern, text)
            if matches:
                last_match = matches[-1]  # Use last emotion tag
                if len(last_match) == 2:
                    emotion_part, alpha_part = last_match
                    try:
                        alpha = float(alpha_part)
                        alpha = max(0.0, min(1.0, alpha))
                    except ValueError:
                        alpha = 0.8
                else:
                    emotion_part = last_match[0]
                    alpha = 0.8

                # Map emotion to supported values
                emotion = self._map_emotion(emotion_part.strip())
                # Remove tags from text
                clean_text = re.sub(pattern, '', text).strip()
                return emotion, alpha, clean_text

        # No emotion tags found, use defaults
        return 'calm', 0.5, text

    def _map_emotion(self, emotion_name: str) -> str:
        """Map emotion name to supported IndexTTS2 emotions"""
        emotion_mapping = {
            'happy': 'happy', 'happiness': 'happy', 'joy': 'happy', 'excited': 'happy',
            'sad': 'sad', 'sadness': 'sad', 'melancholy': 'melancholic', 'melancholic': 'melancholic', 'depressed': 'melancholic',
            'angry': 'angry', 'anger': 'angry', 'rage': 'angry', 'fury': 'angry',
            'afraid': 'afraid', 'fear': 'afraid', 'scared': 'afraid', 'terrified': 'afraid',
            'disgusted': 'disgusted', 'disgust': 'disgusted', 'revolted': 'disgusted',
            'surprised': 'surprised', 'surprise': 'surprised', 'amazed': 'surprised', 'shocked': 'surprised',
            'calm': 'calm', 'neutral': 'calm', 'normal': 'calm', 'peaceful': 'calm',
            # Chinese
            '高兴': 'happy', '快乐': 'happy', '愤怒': 'angry', '生气': 'angry',
            '悲伤': 'sad', '难过': 'sad', '恐惧': 'afraid', '害怕': 'afraid',
            '反感': 'disgusted', '厌恶': 'disgusted', '惊讶': 'surprised', '吃惊': 'surprised',
            '低落': 'melancholic', '忧郁': 'melancholic', '自然': 'calm', '平静': 'calm',
            # Additional complex emotions
            'determined': 'angry', 'resolved': 'angry', 'courageous': 'angry',
            'thoughtful': 'calm', 'wise': 'calm', 'serene': 'calm',
            'alarmed': 'afraid', 'shocked': 'surprised', 'amazed': 'surprised',
            'outraged': 'angry', 'furious': 'angry', 'disgusted': 'disgusted',
            'reverent': 'calm', 'respectful': 'calm', 'content': 'happy',
            'nostalgic': 'melancholic', 'longing': 'sad', 'yearning': 'sad'
        }

        return emotion_mapping.get(emotion_name.lower(), 'calm')


class TextSegmenter:
    """Segment text into manageable chunks for TTS processing"""

    def __init__(self, max_chars: int = 200, overlap_chars: int = 30):
        self.max_chars = max_chars
        self.overlap_chars = overlap_chars

    def segment_dialogue(self, segments: List[DialogueSegment]) -> List[DialogueSegment]:
        """Segment dialogue while preserving character and emotion information"""
        segmented = []

        for segment in segments:
            if len(segment.text) <= self.max_chars:
                segmented.append(segment)
            else:
                # Split long segments
                sub_segments = self._split_long_segment(segment)
                segmented.extend(sub_segments)

        return segmented

    def _split_long_segment(self, segment: DialogueSegment) -> List[DialogueSegment]:
        """Split a long segment while preserving context"""
        text = segment.text
        segments = []

        # Split at sentence boundaries when possible
        sentences = re.split(r'([。！？.!?])', text)
        current_text = ""

        for i in range(0, len(sentences), 2):
            if i + 1 < len(sentences):
                sentence = sentences[i] + sentences[i + 1]
            else:
                sentence = sentences[i]

            if len(current_text + sentence) > self.max_chars and current_text:
                segments.append(DialogueSegment(
                    text=current_text,
                    character=segment.character,
                    emotion=segment.emotion,
                    alpha=segment.alpha,
                    is_dialogue=segment.is_dialogue,
                    position=segment.position
                ))
                # Add overlap for smooth transition
                if self.overlap_chars > 0:
                    overlap_start = max(0, len(current_text) - self.overlap_chars)
                    current_text = current_text[overlap_start:]
                else:
                    current_text = ""

            current_text += sentence

        if current_text:
            segments.append(DialogueSegment(
                text=current_text,
                character=segment.character,
                emotion=segment.emotion,
                alpha=segment.alpha,
                is_dialogue=segment.is_dialogue,
                position=segment.position
            ))

        return segments


class MultiCharacterEmotionGenerator:
    """Generate long-form audio with multiple characters and emotions"""

    def __init__(self, config_path: str, model_dir: str = "./checkpoints",
                 config_file: str = "./checkpoints/config.yaml", cuda_kernel: bool = False):
        self.dialogue_parser = CharacterDialogueParser(config_path)
        self.segmenter = TextSegmenter()
        self.model_dir = model_dir
        self.config_file = config_file
        self.cuda_kernel = cuda_kernel
        self.tts_model = None  # Single TTS model for all characters

        # Initialize TTS models
        self._initialize_tts_models()

    def _initialize_tts_models(self):
        """Initialize a single TTS model to be reused for all characters"""
        try:
            print("Loading TTS model...")
            self.tts_model = IndexTTS2(
                model_dir=self.model_dir,
                cfg_path=self.config_file,
                use_cuda_kernel=self.cuda_kernel
            )
            print("Successfully loaded TTS model")
        except Exception as e:
            print(f"Warning: Failed to load TTS model: {e}")
            self.tts_model = None

    def generate_audio(self, input_text: str, output_file: str,
                      segment_chars: int = 200, fp16: bool = True,
                      cuda_kernel: bool = False, deepspeed: bool = False,
                      verbose: bool = False) -> None:
        """Generate audio file from input text with multiple characters"""

        if verbose:
            print("Parsing text and identifying characters...")

        # Parse dialogue segments
        dialogue_segments = self.dialogue_parser.parse_text_with_characters(input_text)

        if verbose:
            print(f"Found {len(dialogue_segments)} dialogue segments")
            for i, segment in enumerate(dialogue_segments):
                char_config = self.dialogue_parser.characters.get(segment.character)
                char_name = char_config.name if char_config else segment.character
                segment_type = "Dialogue" if segment.is_dialogue else "Narration"
                if segment.emo_text:
                    print(f"  {i+1}. {char_name} ({segment_type}): [{segment.emo_text}] {segment.text[:50]}...")
                else:
                    print(f"  {i+1}. {char_name} ({segment_type}): [{segment.emotion}:{segment.alpha}] {segment.text[:50]}...")

        # Segment long text
        self.segmenter.max_chars = segment_chars
        segmented_dialogue = self.segmenter.segment_dialogue(dialogue_segments)

        if verbose:
            print(f"Segmented into {len(segmented_dialogue)} audio segments")

        # Generate audio segments
        audio_segments = []
        temp_dir = tempfile.mkdtemp()

        try:
            for i, segment in enumerate(segmented_dialogue):
                if verbose:
                    print(f"Generating segment {i+1}/{len(segmented_dialogue)}...")

                audio_segment = self._generate_segment_audio(segment, temp_dir, i, fp16, cuda_kernel)
                if audio_segment is not None:
                    audio_segments.append(audio_segment)

            # Concatenate all segments
            if audio_segments:
                self._concatenate_audio_segments(audio_segments, output_file, verbose)
                print(f"Successfully generated audio: {output_file}")
            else:
                print("Warning: No audio segments were generated")

        finally:
            # Clean up temporary files
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _generate_segment_audio(self, segment: DialogueSegment, temp_dir: str,
                               segment_index: int, fp16: bool, cuda_kernel: bool) -> Optional[str]:
        """Generate audio for a single segment"""

        if self.tts_model is None:
            print(f"Warning: TTS model not available")
            return None

        tts = self.tts_model
        character = self.dialogue_parser.characters[segment.character]

        # Adjust emotion alpha based on dialogue vs narration
        # For very low alpha values (<= 0.1), use no emotion to avoid affecting speech rate
        if segment.alpha <= 0.1:
            # Use no emotion processing for normal speech rate
            adjusted_alpha = 0.0
        elif segment.is_dialogue:
            # Dialogue has stronger emotion expression
            adjusted_alpha = min(1.0, segment.alpha * 1.2)
        else:
            # Narration has more subtle emotion
            adjusted_alpha = segment.alpha * 0.8

        # Generate audio
        try:
            output_path = os.path.join(temp_dir, f"segment_{segment_index:04d}.wav")

            # Use original audio file (IndexTTS2 will handle stereo/mono conversion)
            voice_file = character.voice_file

            # Determine speech speed: 0 = normal, 1 = fast
            # More granular speech speed mapping
            if character.speech_rate >= 1.3:
                use_speed = 1  # Fast speech for excited/angry emotions
            elif character.speech_rate <= 0.8:
                use_speed = 0  # Normal speed for sad/calm emotions
            else:
                # For medium speeds (0.8-1.3), use normal speed but adjust via emotion
                use_speed = 0

            # Check if we should use emotion processing (alpha > 0)
            if adjusted_alpha > 0.0:
                # Check if we have descriptive emotion text
                if segment.emo_text:
                    # Use descriptive emotion text with Qwen emotion model
                    tts.infer(
                        spk_audio_prompt=voice_file,
                        text=segment.text,
                        output_path=output_path,
                        use_emo_text=True,
                        emo_text=segment.emo_text,
                        emo_alpha=adjusted_alpha,
                        use_random=False,
                        verbose=False,
                        use_speed=use_speed
                    )
                else:
                    # Use traditional emotion vector approach
                    emotion_vector = self._create_emotion_vector(segment.emotion, adjusted_alpha)
                    tts.infer(
                        spk_audio_prompt=voice_file,
                        text=segment.text,
                        output_path=output_path,
                        emo_vector=emotion_vector,
                        emo_alpha=adjusted_alpha,
                        use_random=False,
                        verbose=False,
                        use_speed=use_speed
                    )
            else:
                # No emotion processing - use pure voice cloning for original sample sound
                tts.infer(
                    spk_audio_prompt=voice_file,
                    text=segment.text,
                    output_path=output_path,
                    use_random=False,
                    verbose=False,
                    use_speed=use_speed
                )
            return output_path

        except Exception as e:
            print(f"Error generating segment {segment_index}: {e}")
            return None

    def _create_emotion_vector(self, emotion: str, alpha: float) -> torch.Tensor:
        """Create 8-dimensional emotion vector in IndexTTS2 format: [happy, angry, sad, afraid, disgusted, melancholic, surprised, calm]"""
        emotions = ['happy', 'angry', 'sad', 'afraid', 'disgusted', 'melancholic', 'surprised', 'calm']
        emotion_vector = torch.zeros(8)

        if emotion in emotions:
            emotion_vector[emotions.index(emotion)] = alpha
        else:
            emotion_vector[7] = alpha  # Default to calm

        return emotion_vector

    def _concatenate_audio_segments(self, audio_segments: List[str], output_file: str, verbose: bool = False):
        """Concatenate multiple audio segments into final output"""

        if not audio_segments:
            return

        # Load all audio segments
        audio_data = []
        sample_rate = 24000

        for segment_file in audio_segments:
            try:
                audio, sr = torchaudio.load(segment_file)
                if sr != sample_rate:
                    audio = torchaudio.functional.resample(audio, sr, sample_rate)
                audio_data.append(audio)
            except Exception as e:
                print(f"Warning: Failed to load audio segment {segment_file}: {e}")

        if not audio_data:
            print("Error: No valid audio segments to concatenate")
            return

        # Concatenate all segments
        final_audio = torch.cat(audio_data, dim=1)

        # Add small pauses between segments for natural flow
        pause_samples = int(0.1 * sample_rate)  # 0.1 second pause
        pause = torch.zeros(1, pause_samples)

        final_with_pauses = []
        for i, audio in enumerate(audio_data):
            final_with_pauses.append(audio)
            if i < len(audio_data) - 1:
                final_with_pauses.append(pause)

        final_audio = torch.cat(final_with_pauses, dim=1)

        # Save final audio
        torchaudio.save(output_file, final_audio, sample_rate)

        if verbose:
            duration = final_audio.shape[1] / sample_rate
            print(f"Final audio duration: {duration:.2f} seconds")


def main():
    parser = argparse.ArgumentParser(
        description="Multi-Character Long Text Generator with Emotion Tags for IndexTTS2",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Configuration and output arguments
    parser.add_argument("--config", "-c",
                       help="Character configuration JSON file (optional if JSON input contains character_config)")
    parser.add_argument("--output", "-o", required=True,
                       help="Output audio file path")

    # Input source (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--text", "-t",
                            help="Input text with character dialogue and emotion tags")
    input_group.add_argument("--input", "-i",
                            help="Input text file with character dialogue and emotion tags")

    # Optional parameters
    parser.add_argument("--model-dir", default="./checkpoints",
                       help="Model directory")
    parser.add_argument("--config-file", default="./checkpoints/config.yaml",
                       help="Model config file")
    parser.add_argument("--segment-chars", type=int, default=200,
                       help="Maximum characters per segment")
    parser.add_argument("--fp16", action="store_true", default=True,
                       help="Use FP16 inference")
    parser.add_argument("--cuda-kernel", action="store_true",
                       help="Use CUDA kernel optimization")
    parser.add_argument("--deepspeed", action="store_true",
                       help="Use DeepSpeed acceleration")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose output")

    args = parser.parse_args()

    # Load input text and check for embedded character config
    embedded_config = None
    if args.input:
        if not os.path.exists(args.input):
            print(f"Error: Input file {args.input} not found")
            sys.exit(1)
        with open(args.input, 'r', encoding='utf-8') as f:
            file_content = f.read()

        # Check if file is JSON and extract both script_content and character_config
        if args.input.endswith('.json'):
            try:
                import json
                data = json.loads(file_content)
                if 'output' in data:
                    if 'script_content' not in data['output']:
                        print("Error: JSON file must contain 'output.script_content' field")
                        sys.exit(1)
                    input_text = data['output']['script_content']
                    # Extract embedded character config if present
                    if 'character_config' in data['output']:
                        embedded_config = data['output']['character_config']
                else:
                    print("Error: JSON file must contain 'output' field")
                    sys.exit(1)
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON file - {e}")
                sys.exit(1)
        else:
            input_text = file_content
    else:
        input_text = args.text

    # Determine configuration source
    config_to_use = args.config
    if embedded_config:
        # Use embedded config from JSON
        if args.config:
            print("Warning: Both --config and embedded character_config provided. Using embedded config.")
        # Create temporary config file with embedded config
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as temp_file:
            json.dump(embedded_config, temp_file, ensure_ascii=False, indent=2)
            config_to_use = temp_file.name
        print(f"Using embedded character configuration from JSON input")
    elif not args.config:
        # No config provided, use default
        default_config = os.path.join(os.path.dirname(__file__), '../config/character_config.json')
        if os.path.exists(default_config):
            config_to_use = default_config
            print(f"Using default character configuration: {default_config}")
        else:
            print("Error: No character configuration provided and default config not found")
            print("Please either:")
            print("  1. Include character_config in your JSON input")
            print("  2. Use --config parameter")
            print("  3. Create default config at multi_person_support/config/character_config.json")
            sys.exit(1)

    # Check if required files exist
    if not os.path.exists(config_to_use):
        print(f"Error: Configuration file {config_to_use} not found")
        sys.exit(1)

    if not os.path.exists(args.model_dir):
        print(f"Error: Model directory {args.model_dir} not found")
        sys.exit(1)

    # Initialize generator
    generator = MultiCharacterEmotionGenerator(
        config_path=config_to_use,
        model_dir=args.model_dir,
        config_file=args.config_file,
        cuda_kernel=args.cuda_kernel
    )

    # Clean up temporary config file if created
    if embedded_config and config_to_use != args.config:
        try:
            os.unlink(config_to_use)
        except:
            pass

    # Generate audio
    generator.generate_audio(
        input_text=input_text,
        output_file=args.output,
        segment_chars=args.segment_chars,
        fp16=args.fp16,
        cuda_kernel=args.cuda_kernel,
        deepspeed=args.deepspeed,
        verbose=args.verbose
    )


if __name__ == "__main__":
    main()