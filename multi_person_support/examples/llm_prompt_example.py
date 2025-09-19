#!/usr/bin/env python3
"""
Example of how to use the LLM prompt to generate unified JSON output
for IndexTTS2 multi-character content creation.
"""

import json
from pathlib import Path

# Example input story
sample_story = """
In a cozy coffee shop, Emma was working on her laptop when her friend Jake burst in.
"Emma! You won't believe what just happened!" Jake exclaimed, breathless with excitement.
Emma looked up, surprised. "Jake? What's wrong? You look like you've seen a ghost."
"Nothing's wrong! Something's amazing!" Jake grinned, pulling up a chair. "I got the job!"
"The job at the tech company?" Emma asked, her eyes widening.
"Yes! They called me five minutes ago," Jake said, his voice trembling with joy.
Emma jumped up and hugged him. "That's fantastic! I'm so happy for you!"
"Thanks to you for helping me prepare," Jake said sincerely. "Those mock interviews made all the difference."
"""

# Expected unified JSON output format
expected_output = {
    "character_config": {
        "characters": {
            "emma": {
                "name": "Emma",
                "voice_file": "1.旅游VLOG女2Haa.wav",
                "pitch": -0.2,
                "speech_rate": 1.0,
                "volume": 0.9,
                "emotion_intensity": 0.8
            },
            "jake": {
                "name": "Jake",
                "voice_file": "Alan024_青年男.wav",
                "pitch": 0.1,
                "speech_rate": 1.1,
                "volume": 1.0,
                "emotion_intensity": 0.8
            },
            "narrator": {
                "name": "Narrator",
                "voice_file": "audiobook_prompt.wav",
                "pitch": 0.0,
                "speech_rate": 0.9,
                "volume": 0.9,
                "emotion_intensity": 0.6
            }
        }
    },
    "script_content": "{[narrator]:[calm:0.3]}In a cozy coffee shop, Emma was working on her laptop when her friend Jake burst in.
{[jake]:[excited:0.9]}Emma! You won't believe what just happened!
{[emma]:[surprised:0.8]}Jake? What's wrong? You look like you've seen a ghost.
{[jake]:[happy:0.8]}Nothing's wrong! Something's amazing!
{[jake]:[calm:0.6]}pulling up a chair. I got the job!
{[emma]:[surprised:0.7]}The job at the tech company?
{[emma]:[happy:0.7]}her eyes widening.
{[jake]:[joy:0.9]}Yes! They called me five minutes ago,
{[jake]:[happy:0.8]}his voice trembling with joy.
{[emma]:[happy:0.9]}That's fantastic! I'm so happy for you!
{[jake]:[grateful:0.8]}Thanks to you for helping me prepare,
{[jake]:[sincere:0.7]}Those mock interviews made all the difference."
}

def save_unified_output(config_and_script, output_path):
    """Save the unified JSON output to file"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(config_and_script, f, indent=2, ensure_ascii=False)
    print(f"✅ Unified output saved to: {output_path}")

def split_unified_output(unified_data, output_dir):
    """Split unified output into separate config and script files for IndexTTS2"""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    # Save character config
    config_path = output_dir / "character_config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(unified_data["character_config"], f, indent=2, ensure_ascii=False)
    print(f"📋 Character config saved to: {config_path}")

    # Save script content
    script_path = output_dir / "script.txt"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(unified_data["script_content"])
    print(f"📝 Script content saved to: {script_path}")

    return config_path, script_path

def main():
    """Demonstrate the unified JSON output format"""
    print("🎭 IndexTTS2 Multi-Character LLM Prompt Example")
    print("=" * 50)

    print("\n📖 Sample Input Story:")
    print("-" * 30)
    print(sample_story)

    print("\n🎯 Expected Unified JSON Output:")
    print("-" * 40)
    print(json.dumps(expected_output, indent=2, ensure_ascii=False))

    # Save unified output
    unified_path = "unified_output.json"
    save_unified_output(expected_output, unified_path)

    # Split into separate files for IndexTTS2
    print(f"\n🔀 Splitting into IndexTTS2 format...")
    config_path, script_path = split_unified_output(expected_output, "llm_generated_content")

    print(f"\n✅ Complete! The unified JSON output contains:")
    print(f"   - Character configuration for {len(expected_output['character_config']['characters'])} characters")
    print(f"   - Formatted script with strict format character prefixes: {{[character]:[emotion:intensity]}}")
    print(f"   - Ready for use with multi_character_emotion_generator.py")

    print(f"\n🚀 Usage:")
    print(f"   uv run multi_character_emotion_generator.py \\")
    print(f"     --config {config_path} \\")
    print(f"     --input {script_path} \\")
    print(f"     --output generated_story.wav")

if __name__ == "__main__":
    main()