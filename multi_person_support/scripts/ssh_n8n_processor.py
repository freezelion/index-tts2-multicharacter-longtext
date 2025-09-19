#!/usr/bin/env python3
"""
SSH/N8N TTS Processor for IndexTTS2

This script processes TTS commands from n8n nodes via SSH connections.
It handles multi-character scripts with emotion tags and generates audio files.

Usage:
    python ssh_n8n_processor.py --config character_config.json --input-json "n8n_data.json" --output "output.wav"
    python ssh_n8n_processor.py --config character_config.json --script "{[narrator]:[calm:0.3]}Hello world" --output "output.wav"
"""

import os
import sys
import json
import argparse
import tempfile
import traceback
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add current directory to path for IndexTTS imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, "indextts"))

try:
    from multi_character_emotion_generator import MultiCharacterEmotionGenerator
except ImportError as e:
    logger.error(f"Error importing multi_character_emotion_generator: {e}")
    sys.exit(1)


class SSHN8NProcessor:
    """Process TTS commands from SSH/n8n inputs"""

    def __init__(self, config_path: Optional[str] = None, model_dir: str = "./checkpoints",
                 config_file: str = "./checkpoints/config.yaml"):
        """
        Initialize the IndexTTS2 processor

        Args:
            config_path: Path to character configuration JSON file (optional)
            model_dir: Directory containing model files
            config_file: Model configuration file
        """
        self.config_path = config_path
        self.model_dir = model_dir
        self.config_file = config_file
        self.generator = None

        # Initialize the generator if config is provided, otherwise defer initialization
        if config_path:
            self._initialize_generator()
        else:
            logger.info("No initial config provided - will initialize when embedded config is available")

    def _initialize_generator(self, config_path: Optional[str] = None):
        """Initialize the multi-character emotion generator"""
        try:
            use_config_path = config_path or self.config_path
            if not use_config_path:
                raise ValueError("No configuration path provided for generator initialization")

            self.generator = MultiCharacterEmotionGenerator(
                config_path=use_config_path,
                model_dir=self.model_dir,
                config_file=self.config_file,
                cuda_kernel=False  # Default to False for SSH safety
            )
            logger.info("Successfully initialized IndexTTS2 generator")
        except Exception as e:
            logger.error(f"Failed to initialize IndexTTS2 generator: {e}")
            raise

    def process_n8n_output(self, n8n_data: Dict[str, Any], output_file: str,
                          verbose: bool = False) -> bool:
        """
        Process n8n node output data

        Args:
            n8n_data: Dictionary containing character_config and script_content
            output_file: Path for output audio file
            verbose: Enable verbose output

        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract script content from n8n data
            script_content = n8n_data.get('output', {}).get('script_content', '')
            if not script_content:
                logger.error("No script_content found in n8n output")
                return False

            # Update character configuration if provided
            char_config = n8n_data.get('output', {}).get('character_config')
            if char_config:
                self._update_character_config(char_config)

            # Generate audio
            self.generator.generate_audio(
                input_text=script_content,
                output_file=output_file,
                segment_chars=200,
                fp16=True,
                cuda_kernel=False,
                deepspeed=False,
                verbose=verbose
            )

            logger.info(f"Successfully generated audio: {output_file}")
            return True

        except Exception as e:
            logger.error(f"Error processing n8n output: {e}")
            logger.error(traceback.format_exc())
            return False

    def process_direct_script(self, script_text: str, output_file: str,
                            verbose: bool = False) -> bool:
        """
        Process direct script input

        Args:
            script_text: Multi-character script with emotion tags
            output_file: Path for output audio file
            verbose: Enable verbose output

        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate audio directly from script
            self.generator.generate_audio(
                input_text=script_text,
                output_file=output_file,
                segment_chars=200,
                fp16=True,
                cuda_kernel=False,
                deepspeed=False,
                verbose=verbose
            )

            logger.info(f"Successfully generated audio: {output_file}")
            return True

        except Exception as e:
            logger.error(f"Error processing direct script: {e}")
            logger.error(traceback.format_exc())
            return False

    def _update_character_config(self, char_config: Dict[str, Any]):
        """
        Update character configuration with new data from n8n

        Args:
            char_config: Character configuration dictionary
        """
        try:
            # Create a temporary config file with the new configuration
            temp_config = self._create_temp_config(char_config)

            # Reinitialize generator with new config
            self._initialize_generator(temp_config)

            # Clean up temp file
            os.remove(temp_config)
            logger.info("Successfully updated character configuration")

        except Exception as e:
            logger.error(f"Error updating character configuration: {e}")
            # Continue with existing configuration

    def _create_temp_config(self, char_config: Dict[str, Any]) -> str:
        """
        Create a temporary configuration file with updated character data

        Args:
            char_config: Character configuration dictionary

        Returns:
            Path to temporary configuration file
        """
        # Load existing config as base
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                base_config = json.load(f)
        except:
            # If base config doesn't exist, create minimal structure
            base_config = {
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

        # Update with new character configuration
        if 'characters' in char_config:
            # Convert n8n format to expected format
            for char_id, char_data in char_config['characters'].items():
                converted_char = {
                    "name": char_data.get("name", char_id),
                    "voice_file": char_data.get("voice_file", "examples/voice_01.wav"),
                    "default_emotion": "calm",
                    "emotion_intensity": char_data.get("emotion_intensity", 0.5),
                    "speech_rate": char_data.get("speech_rate", 1.0),
                    "pitch": char_data.get("pitch", 1.0),
                    "volume": char_data.get("volume", 1.0),
                    "description": f"Character {char_data.get('name', char_id)}"
                }
                base_config['characters'][char_id] = converted_char

        # Write to temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8')
        json.dump(base_config, temp_file, ensure_ascii=False, indent=2)
        temp_file.close()

        return temp_file.name


def create_sample_n8n_data():
    """Create sample n8n data for testing"""
    return {
        "output": {
            "character_config": {
                "characters": {
                    "sarah": {
                        "name": "Science Reporter",
                        "voice_file": "2.语速比较快的讲解女声Haa.wav",
                        "pitch": -0.2,
                        "speech_rate": 1.1,
                        "volume": 1,
                        "emotion_intensity": 0.8
                    },
                    "tom": {
                        "name": "AI Expert",
                        "voice_file": "口播男声.wav",
                        "pitch": 0.1,
                        "speech_rate": 1,
                        "volume": 1,
                        "emotion_intensity": 0.8
                    },
                    "narrator": {
                        "name": "Narrator",
                        "voice_file": "audiobook_prompt.wav",
                        "pitch": 0,
                        "speech_rate": 0.9,
                        "volume": 0.9,
                        "emotion_intensity": 0.6
                    }
                }
            },
            "script_content": """{[narrator]:[calm:0.3]}Nature封面上的中国AI少年：DeepSeek-R1如何用200万撬动全球科技圈？
{[narrator]:[calm:0.3]}预计阅读时间: 8分钟
{[sarah]:[excited:0.8]}核心科学概念：强化学习(RLHF): 通过奖励和惩罚机制训练AI系统的方法
{[narrator]:[calm:0.5]}2025年2月14日，北京中关村的一间实验室里，梁文锋团队按下了论文投稿按钮。
{[tom]:[calm:0.8]}可以将RLHF理解为'AI驯兽师'——通过奖励期望行为、惩罚不期望行为，逐步塑造模型的推理能力。
{[sarah]:[inspired:0.8]}这种"极致性价比"模式证明了科学突破未必需要天价投入，为资源有限的研究团队开辟了新可能性。"""
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description="SSH/N8N TTS Processor for IndexTTS2",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Configuration and output arguments
    parser.add_argument("--config", "-c",
                       help="Character configuration JSON file (optional if JSON input contains character_config)")
    parser.add_argument("--output", "-o", required=True,
                       help="Output audio file path")

    # Input source (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--input-json", "-j",
                            help="Input JSON file with n8n output data")
    input_group.add_argument("--script", "-s",
                            help="Direct script input with character dialogue and emotion tags")
    input_group.add_argument("--create-sample", action="store_true",
                            help="Create sample n8n data for testing")

    # Optional parameters
    parser.add_argument("--model-dir", default="./checkpoints",
                       help="Model directory")
    parser.add_argument("--config-file", default="./checkpoints/config.yaml",
                       help="Model config file")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose output")
    parser.add_argument("--log-file",
                       help="Log file path (default: console only)")

    args = parser.parse_args()

    # Set up logging
    if args.log_file:
        file_handler = logging.FileHandler(args.log_file)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Determine configuration source
    config_to_use = args.config

    # For JSON input, check if it contains embedded character config
    if args.input_json:
        try:
            with open(args.input_json, 'r', encoding='utf-8') as f:
                n8n_data = json.load(f)

            # Check if JSON contains embedded character config
            embedded_config = n8n_data.get('output', {}).get('character_config')
            if embedded_config:
                if args.config:
                    logger.warning("Both --config and embedded character_config provided. Using embedded config.")
                # Use embedded config - we'll pass None as config_path and let processor handle it
                config_to_use = None
                logger.info("Using embedded character configuration from JSON input")
        except Exception as e:
            logger.warning(f"Could not check JSON input for embedded config: {e}")

    # If no config determined, use default
    if not config_to_use:
        default_config = os.path.join(os.path.dirname(__file__), '../config/character_config.json')
        if os.path.exists(default_config):
            config_to_use = default_config
            logger.info(f"Using default character configuration: {default_config}")
        else:
            # For SSH processor, we can proceed without initial config if JSON input will provide it
            logger.info("No initial character config provided - will use embedded config from JSON input")
            config_to_use = None

    # Check if config file exists (if specified)
    if config_to_use and not os.path.exists(config_to_use):
        logger.error(f"Configuration file {config_to_use} not found")
        sys.exit(1)

    try:
        # Initialize processor (config_path can be None if JSON input will provide embedded config)
        processor = SSHN8NProcessor(
            config_path=config_to_use,
            model_dir=args.model_dir,
            config_file=args.config_file
        )

        success = False

        if args.create_sample:
            # Create sample data
            sample_data = create_sample_n8n_data()
            sample_file = "sample_n8n_data.json"
            with open(sample_file, 'w', encoding='utf-8') as f:
                json.dump(sample_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Created sample n8n data: {sample_file}")
            return

        elif args.input_json:
            # Process from JSON file
            if not os.path.exists(args.input_json):
                logger.error(f"Input JSON file {args.input_json} not found")
                sys.exit(1)

            with open(args.input_json, 'r', encoding='utf-8') as f:
                n8n_data = json.load(f)

            success = processor.process_n8n_output(n8n_data, args.output, args.verbose)

        elif args.script:
            # Process direct script
            success = processor.process_direct_script(args.script, args.output, args.verbose)

        if success:
            logger.info("TTS processing completed successfully")
            sys.exit(0)
        else:
            logger.error("TTS processing failed")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()