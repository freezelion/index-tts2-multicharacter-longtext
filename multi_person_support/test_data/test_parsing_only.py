#!/usr/bin/env python3
"""
Test script to validate descriptive emotion parsing without generating audio
"""

import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, "scripts"))

from multi_character_emotion_generator import CharacterDialogueParser

def test_descriptive_emotion_parsing():
    """Test that descriptive emotion text is parsed correctly"""

    # Initialize parser with config
    config_path = "config/character_config.json"
    parser = CharacterDialogueParser(config_path)

    # Test both formats
    test_cases = [
        # Intensity format (existing)
        "{[narrator]:[calm:0.9]}Hello world",
        # Descriptive format (new)
        "{[sarah]:[excited:very excited and enthusiastic]}This is amazing!",
        # Mixed format
        "{[tom]:[calm:calm and professional]}Let me explain this clearly",
        # Another descriptive format
        "{[narrator]:[sad:melancholy and nostalgic}]Those were the days"
    ]

    print("Testing emotion parsing...")
    print("=" * 50)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case}")

        # Test character prefix detection
        has_prefix = parser._has_character_prefix(test_case)
        print(f"  Has character prefix: {has_prefix}")

        if has_prefix:
            # Test content extraction
            char_id, emotion, value, content = parser._extract_character_content(test_case)
            print(f"  Character: {char_id}")
            print(f"  Emotion: {emotion}")
            print(f"  Value: {value} ({type(value).__name__})")
            print(f"  Content: {content}")

            # Check if value is descriptive
            if isinstance(value, str):
                print(f"  → Descriptive emotion detected!")
                emo_text = f"{emotion}: {value}"
                print(f"  → Emo text: {emo_text}")
            else:
                print(f"  → Numeric intensity detected!")
                print(f"  → Intensity: {value}")

        print("-" * 30)

    # Test with full dialogue parsing
    print("\nTesting full dialogue parsing...")
    print("=" * 50)

    sample_script = """{[narrator]:[calm:very peaceful and calm]}Welcome to our show.
{[sarah]:[excited:extremely excited and energetic]}Today we have amazing news!
{[tom]:[calm:calm and professional]}Let me analyze this situation."""

    segments = parser.parse_text_with_characters(sample_script)

    print(f"\nParsed {len(segments)} segments:")
    for i, segment in enumerate(segments, 1):
        print(f"  {i}. {segment.character}: [{segment.emotion}:{segment.alpha}] {segment.text}")
        if segment.emo_text:
            print(f"     → Descriptive: {segment.emo_text}")

    print("\n" + "=" * 50)
    print("✅ All tests completed successfully!")

if __name__ == "__main__":
    test_descriptive_emotion_parsing()