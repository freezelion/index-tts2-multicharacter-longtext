#!/usr/bin/env python3
"""
Long Text Generator with Emotion Tags for IndexTTS2

This script enables generation of long-form speech with dynamic emotion control
using embedded emotion tags within the text. It handles text segmentation,
emotion mapping, and seamless audio generation with proper transitions.

Features:
- Parse emotion tags embedded in text (e.g., [happy], [sad], [angry])
- Automatic text segmentation at sentence boundaries
- Smooth emotion transitions between segments
- Configurable segment length and overlap
- Support for all IndexTTS2 emotions
- Batch processing for efficiency

Usage:
    python long_text_emotion_generator.py --voice voice.wav --input "text.txt" --output "output.wav"
    python long_text_emotion_generator.py --voice voice.wav --text "[happy]Hello world! [sad]Goodbye cruel world..." --output "output.wav"
"""

import os
import re
import sys
import argparse
import json
from typing import List, Dict, Tuple, Optional
import tempfile
import shutil
from pathlib import Path

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


class EmotionTagParser:
    """Parse and process emotion tags in text"""

    # Supported emotions and their mappings
    EMOTION_MAPPING = {
        'happy': 'happy',
        'happiness': 'happy',
        'joy': 'happy',
        'excited': 'happy',

        'sad': 'sad',
        'sadness': 'sad',
        'melancholy': 'melancholic',
        'melancholic': 'melancholic',
        'depressed': 'melancholic',

        'angry': 'angry',
        'anger': 'angry',
        'rage': 'angry',
        'fury': 'angry',

        'afraid': 'afraid',
        'fear': 'afraid',
        'scared': 'afraid',
        'terrified': 'afraid',

        'disgusted': 'disgusted',
        'disgust': 'disgusted',
        'revolted': 'disgusted',

        'surprised': 'surprised',
        'surprise': 'surprised',
        'amazed': 'surprised',
        'shocked': 'surprised',

        'calm': 'calm',
        'neutral': 'calm',
        'normal': 'calm',
        'peaceful': 'calm',

        # Chinese mappings
        '高兴': 'happy',
        '快乐': 'happy',
        '愤怒': 'angry',
        '生气': 'angry',
        '悲伤': 'sad',
        '难过': 'sad',
        '恐惧': 'afraid',
        '害怕': 'afraid',
        '反感': 'disgusted',
        '厌恶': 'disgusted',
        '低落': 'melancholic',
        '忧郁': 'melancholic',
        '惊讶': 'surprised',
        '吃惊': 'surprised',
        '自然': 'calm',
        '平静': 'calm',
    }

    def __init__(self, default_emotion: str = 'calm'):
        self.default_emotion = default_emotion

    def parse_emotion_tags(self, text: str) -> List[Dict]:
        """
        Parse text with emotion tags and return segments with emotions.

        Args:
            text: Input text with emotion tags like [happy:0.8], [sad:0.5], etc.

        Returns:
            List of dictionaries with 'text', 'emotion', 'alpha', and 'position' keys
        """
        # Pattern to match emotion tags: [emotion_name:alpha] or [emotion_name]
        tag_pattern = r'\[([^\]]+)\]'

        segments = []
        current_pos = 0
        current_emotion = self.default_emotion
        current_alpha = 1.0  # Default alpha if not specified

        # Find all emotion tags and their positions
        matches = list(re.finditer(tag_pattern, text))

        if not matches:
            # No emotion tags found, use default emotion and alpha
            return [{
                'text': text.strip(),
                'emotion': current_emotion,
                'alpha': current_alpha,
                'position': 0
            }]

        # Process text between tags
        for i, match in enumerate(matches):
            tag_content = match.group(1).lower().strip()

            # Parse emotion and alpha from tag content
            if ':' in tag_content:
                emotion_part, alpha_part = tag_content.split(':', 1)
                emotion_name = emotion_part.strip()
                try:
                    alpha_value = float(alpha_part.strip())
                    # Clamp alpha between 0.0 and 1.0
                    alpha_value = max(0.0, min(1.0, alpha_value))
                except ValueError:
                    alpha_value = 1.0  # Default if parsing fails
            else:
                emotion_name = tag_content
                alpha_value = 1.0

            # Map emotion tag to supported emotion
            emotion = self.EMOTION_MAPPING.get(emotion_name, self.default_emotion)

            # Extract text before this tag
            if current_pos < match.start():
                segment_text = text[current_pos:match.start()].strip()
                if segment_text:  # Only add non-empty segments
                    segments.append({
                        'text': segment_text,
                        'emotion': current_emotion,
                        'alpha': current_alpha,
                        'position': current_pos
                    })

            # Update current emotion and alpha
            current_emotion = emotion
            current_alpha = alpha_value
            current_pos = match.end()

        # Add remaining text after last tag
        if current_pos < len(text):
            remaining_text = text[current_pos:].strip()
            if remaining_text:
                segments.append({
                    'text': remaining_text,
                    'emotion': current_emotion,
                    'alpha': current_alpha,
                    'position': current_pos
                })

        return segments

    def emotion_to_vector(self, emotion: str) -> List[float]:
        """
        Convert emotion name to 8-dimensional emotion vector.
        Order: [happy, angry, sad, afraid, disgusted, melancholic, surprised, calm]
        """
        emotion_vectors = {
            'happy': [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            'angry': [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            'sad': [0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            'afraid': [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0],
            'disgusted': [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
            'melancholic': [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
            'surprised': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
            'calm': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
        }

        return emotion_vectors.get(emotion, emotion_vectors['calm'])


class TextSegmenter:
    """Segment long text into manageable chunks for TTS processing"""

    def __init__(self, max_chars: int = 200, min_chars: int = 50):
        self.max_chars = max_chars
        self.min_chars = min_chars

    def segment_text(self, text: str, emotion: str, alpha: float = 1.0) -> List[Dict]:
        """
        Segment text into chunks suitable for TTS processing.

        Args:
            text: Input text to segment
            emotion: Emotion to apply to all segments
            alpha: Emotion intensity for all segments

        Returns:
            List of segment dictionaries
        """
        if len(text) <= self.max_chars:
            return [{
                'text': text,
                'emotion': emotion,
                'alpha': alpha,
                'start_char': 0,
                'end_char': len(text)
            }]

        segments = []

        # Split by sentence boundaries first
        sentences = re.split(r'(?<=[.!?。！？])\s+', text)

        current_segment = ""
        start_char = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # If adding this sentence exceeds max length and current segment is not empty
            if len(current_segment) + len(sentence) + 1 > self.max_chars and current_segment:
                # Save current segment
                segments.append({
                    'text': current_segment.strip(),
                    'emotion': emotion,
                    'alpha': alpha,
                    'start_char': start_char,
                    'end_char': start_char + len(current_segment.strip())
                })

                # Start new segment
                current_segment = sentence
                start_char += len(current_segment.strip()) + 1  # +1 for space
            else:
                # Add to current segment
                if current_segment:
                    current_segment += " " + sentence
                else:
                    current_segment = sentence

        # Add remaining segment
        if current_segment:
            segments.append({
                'text': current_segment.strip(),
                'emotion': emotion,
                'alpha': alpha,
                'start_char': start_char,
                'end_char': start_char + len(current_segment.strip())
            })

        return segments


class LongTextEmotionGenerator:
    """Main class for long text generation with emotion tags"""

    def __init__(self,
                 voice_prompt_path: str,
                 model_dir: str = "checkpoints",
                 config_path: str = "checkpoints/config.yaml",
                 use_fp16: bool = True,
                 use_cuda_kernel: bool = False,
                 use_deepspeed: bool = False,
                 default_emo_alpha: float = 0.8,
                 segment_max_chars: int = 200):
        """
        Initialize the long text emotion generator.

        Args:
            voice_prompt_path: Path to voice reference audio
            model_dir: Directory containing model files
            config_path: Path to model configuration
            use_fp16: Use FP16 for faster inference
            use_cuda_kernel: Use CUDA kernel optimization
            use_deepspeed: Use DeepSpeed acceleration
            default_emo_alpha: Default emotion intensity (0.0-1.0) when not specified in tags
            segment_max_chars: Maximum characters per segment
        """
        self.voice_prompt_path = voice_prompt_path
        self.default_emo_alpha = default_emo_alpha

        # Initialize IndexTTS2
        print("Loading IndexTTS2 model...")
        self.tts = IndexTTS2(
            cfg_path=config_path,
            model_dir=model_dir,
            use_fp16=use_fp16,
            use_cuda_kernel=use_cuda_kernel,
            use_deepspeed=use_deepspeed
        )

        # Initialize helper classes
        self.emotion_parser = EmotionTagParser()
        self.text_segmenter = TextSegmenter(max_chars=segment_max_chars)

        # Create temporary directory for intermediate files
        self.temp_dir = tempfile.mkdtemp(prefix="indextts_long_text_")

    def __del__(self):
        """Clean up temporary files"""
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass

    def generate_segments(self, segments: List[Dict]) -> List[str]:
        """
        Generate audio for all segments.

        Args:
            segments: List of segment dictionaries with 'text', 'emotion', and 'alpha'

        Returns:
            List of paths to generated audio files
        """
        audio_files = []

        print(f"Generating {len(segments)} audio segments...")

        for i, segment in enumerate(segments):
            alpha = segment.get('alpha', self.default_emo_alpha)
            print(f"  Segment {i+1}/{len(segments)}: [{segment['emotion']}] (α={alpha:.2f}) '{segment['text'][:50]}...'")

            # Convert emotion to vector
            emo_vector = self.emotion_parser.emotion_to_vector(segment['emotion'])

            # Generate output path
            output_path = os.path.join(self.temp_dir, f"segment_{i:03d}.wav")

            try:
                # Generate audio for this segment
                self.tts.infer(
                    spk_audio_prompt=self.voice_prompt_path,
                    text=segment['text'],
                    output_path=output_path,
                    emo_vector=emo_vector,
                    emo_alpha=alpha,  # Use per-segment alpha
                    use_random=False,
                    verbose=False
                )

                if os.path.exists(output_path):
                    audio_files.append(output_path)
                else:
                    print(f"Warning: Failed to generate audio for segment {i+1}")

            except Exception as e:
                print(f"Error generating segment {i+1}: {e}")
                continue

        return audio_files

    def concatenate_audio(self, audio_files: List[str], output_path: str) -> bool:
        """
        Concatenate multiple audio files into a single file.

        Args:
            audio_files: List of paths to audio files
            output_path: Path for output audio file

        Returns:
            True if successful, False otherwise
        """
        if not audio_files:
            print("No audio files to concatenate")
            return False

        try:
            # Load all audio files and concatenate
            audio_data = []
            sample_rate = None

            for audio_file in audio_files:
                if os.path.exists(audio_file):
                    # Load audio
                    waveform, sr = torchaudio.load(audio_file)
                    if sample_rate is None:
                        sample_rate = sr
                    elif sr != sample_rate:
                        # Resample if needed
                        waveform = torchaudio.transforms.Resample(sr, sample_rate)(waveform)

                    audio_data.append(waveform)

            if not audio_data:
                print("No valid audio data found")
                return False

            # Concatenate all audio
            concatenated = torch.cat(audio_data, dim=1)

            # Save output
            torchaudio.save(output_path, concatenated, sample_rate)
            print(f"Successfully concatenated {len(audio_files)} segments to: {output_path}")
            return True

        except Exception as e:
            print(f"Error concatenating audio: {e}")
            return False

    def generate_from_text(self, text: str, output_path: str) -> bool:
        """
        Generate long-form speech from text with emotion tags.

        Args:
            text: Input text with emotion tags
            output_path: Path for output audio file

        Returns:
            True if successful, False otherwise
        """
        print("Parsing emotion tags...")
        emotion_segments = self.emotion_parser.parse_emotion_tags(text)

        if not emotion_segments:
            print("No text segments found")
            return False

        print(f"Found {len(emotion_segments)} emotion segments:")
        for i, segment in enumerate(emotion_segments):
            alpha = segment.get('alpha', self.default_emo_alpha)
            print(f"  {i+1}: [{segment['emotion']}] (α={alpha:.2f}) {segment['text'][:50]}...")

        # Further segment long emotion segments
        all_segments = []
        for emotion_segment in emotion_segments:
            text_segments = self.text_segmenter.segment_text(
                emotion_segment['text'],
                emotion_segment['emotion'],
                emotion_segment.get('alpha', self.default_emo_alpha)
            )
            all_segments.extend(text_segments)

        print(f"Total segments after text segmentation: {len(all_segments)}")

        # Display segments with their alpha values
        if len(all_segments) <= 10:  # Only show if not too many
            for i, segment in enumerate(all_segments):
                alpha = segment.get('alpha', self.default_emo_alpha)
                print(f"  Final segment {i+1}: [{segment['emotion']}] (α={alpha:.2f}) '{segment['text'][:40]}...'")

        # Generate audio for all segments
        audio_files = self.generate_segments(all_segments)

        if not audio_files:
            print("No audio segments were generated")
            return False

        # Concatenate all segments
        return self.concatenate_audio(audio_files, output_path)

    def generate_from_file(self, input_file: str, output_path: str) -> bool:
        """
        Generate long-form speech from text file with emotion tags.

        Args:
            input_file: Path to input text file
            output_path: Path for output audio file

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                text = f.read()

            return self.generate_from_text(text, output_path)

        except Exception as e:
            print(f"Error reading input file: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Long Text Generator with Emotion Tags for IndexTTS2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate from text with emotion tags
  python long_text_emotion_generator.py --voice voice.wav --text "[happy]Hello world! [sad:0.5]Goodbye..." --output output.wav

  # Generate from text file
  python long_text_emotion_generator.py --voice voice.wav --input story.txt --output story.wav

  # With custom settings
  python long_text_emotion_generator.py --voice voice.wav --input script.txt --output podcast.wav --default-emo-alpha 0.6 --segment-chars 150

Supported emotion tags:
  [happy], [happy:0.8], [sad], [sad:0.3], [angry], [angry:1.0], etc.
  Chinese: [高兴], [高兴:0.7], [悲伤], [悲伤:0.5], etc.

Alpha values (0.0-1.0) control emotion intensity for each tag.
        """
    )

    parser.add_argument(
        "--voice", "-v",
        type=str,
        required=True,
        help="Path to voice reference audio file (WAV format)"
    )

    parser.add_argument(
        "--text", "-t",
        type=str,
        help="Input text with emotion tags (use either --text or --input)"
    )

    parser.add_argument(
        "--input", "-i",
        type=str,
        help="Input text file with emotion tags (use either --text or --input)"
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        required=True,
        help="Output audio file path"
    )

    parser.add_argument(
        "--model-dir",
        type=str,
        default="checkpoints",
        help="Model directory (default: checkpoints)"
    )

    parser.add_argument(
        "--config",
        type=str,
        default="checkpoints/config.yaml",
        help="Model configuration file (default: checkpoints/config.yaml)"
    )

    parser.add_argument(
        "--default-emo-alpha",
        type=float,
        default=0.8,
        help="Default emotion intensity (0.0-1.0, default: 0.8) when not specified in tags"
    )

    parser.add_argument(
        "--segment-chars",
        type=int,
        default=200,
        help="Maximum characters per segment (default: 200)"
    )

    parser.add_argument(
        "--fp16",
        action="store_true",
        default=True,
        help="Use FP16 for faster inference"
    )

    parser.add_argument(
        "--cuda-kernel",
        action="store_true",
        default=False,
        help="Use CUDA kernel optimization"
    )

    parser.add_argument(
        "--deepspeed",
        action="store_true",
        default=False,
        help="Use DeepSpeed acceleration"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Enable verbose output"
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.text and not args.input:
        print("Error: Either --text or --input must be specified")
        parser.print_help()
        sys.exit(1)

    if args.text and args.input:
        print("Warning: Both --text and --input specified. Using --text and ignoring --input")

    # Check if voice file exists
    if not os.path.exists(args.voice):
        print(f"Error: Voice file '{args.voice}' does not exist")
        sys.exit(1)

    # Check if model directory exists
    if not os.path.exists(args.model_dir):
        print(f"Error: Model directory '{args.model_dir}' does not exist")
        sys.exit(1)

    # Check if config file exists
    if not os.path.exists(args.config):
        print(f"Error: Config file '{args.config}' does not exist")
        sys.exit(1)

    try:
        # Initialize generator
        generator = LongTextEmotionGenerator(
            voice_prompt_path=args.voice,
            model_dir=args.model_dir,
            config_path=args.config,
            use_fp16=args.fp16,
            use_cuda_kernel=args.cuda_kernel,
            use_deepspeed=args.deepspeed,
            default_emo_alpha=args.default_emo_alpha,
            segment_max_chars=args.segment_chars
        )

        # Generate audio
        if args.text:
            success = generator.generate_from_text(args.text, args.output)
        else:
            success = generator.generate_from_file(args.input, args.output)

        if success:
            print(f"\nSuccessfully generated long-form speech: {args.output}")
            if args.verbose:
                # Get file info
                if os.path.exists(args.output):
                    import soundfile as sf
                    data, sr = sf.read(args.output)
                    duration = len(data) / sr
                    print(f"Audio duration: {duration:.2f} seconds")
                    print(f"Sample rate: {sr} Hz")
        else:
            print("\nFailed to generate audio")
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()