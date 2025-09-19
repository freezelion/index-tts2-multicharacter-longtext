#!/usr/bin/env python3
"""
Test script to verify voice assignment and character detection
"""

import sys
import os
import json
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
sys.path.append(os.path.join(parent_dir, "scripts"))

def test_voice_assignment():
    """Test that characters are assigned correct voice files"""

    print("🧪 Testing Voice Assignment Logic")
    print("=" * 50)

    # Load test configuration
    with open('narrator_voice_test.json', 'r', encoding='utf-8') as f:
        test_data = json.load(f)

    # Import and initialize parser
    from multi_character_emotion_generator import CharacterDialogueParser

    config_path = os.path.join(parent_dir, "config/character_config.json")
    parser = CharacterDialogueParser(config_path)

    # Extract script content
    script_content = test_data['output']['script_content']
    print(f"Script content: {script_content}")
    print()

    # Parse dialogue segments
    segments = parser.parse_text_with_characters(script_content)

    print(f"📋 Found {len(segments)} segments:")
    print()

    for i, segment in enumerate(segments, 1):
        char_config = parser.characters.get(segment.character)
        char_name = char_config.name if char_config else segment.character
        voice_file = char_config.voice_file if char_config else "NOT FOUND"

        print(f"Segment {i}:")
        print(f"  Character: {segment.character}")
        print(f"  Name: {char_name}")
        print(f"  Voice File: {voice_file}")
        print(f"  Emotion: {segment.emotion}")
        print(f"  Alpha: {segment.alpha}")
        if segment.emo_text:
            print(f"  Descriptive: {segment.emo_text}")
        print(f"  Text: {segment.text}")
        print()

    # Check character configuration
    print("📋 Character Configuration:")
    print("=" * 30)
    for char_id, char_config in parser.characters.items():
        print(f"{char_id}:")
        print(f"  Name: {char_config.name}")
        print(f"  Voice: {char_config.voice_file}")
        print(f"  Speech Rate: {char_config.speech_rate}")
        print(f"  Pitch: {char_config.pitch}")
        print(f"  Volume: {char_config.volume}")
        print()

    # Verify voice files exist
    print("🔍 Voice File Verification:")
    print("=" * 30)
    for char_id, char_config in parser.characters.items():
        voice_file = char_config.voice_file
        if os.path.exists(voice_file):
            print(f"✅ {char_id}: {voice_file} (EXISTS)")
        else:
            print(f"❌ {char_id}: {voice_file} (NOT FOUND)")

    print()
    print("🎯 Test completed! Please check the output above to verify:")
    print("1. Narrator segments use the correct voice file")
    print("2. Sarah segments use the correct voice file")
    print("3. Voice files actually exist on the filesystem")

if __name__ == "__main__":
    test_voice_assignment()