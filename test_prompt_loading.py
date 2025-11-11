"""
Test if the prompt is loading correctly
"""

from agent.prompt_manager_v6 import get_system_prompt

prompt = get_system_prompt("v6")

print("="*70)
print("CHECKING PROMPT V6")
print("="*70)

# Check for key phrases
checks = [
    ("CANNOT BOOK WITHOUT CALLING THE TOOL", "Critical rule about tools"),
    ("book_reservation", "Tool name mentioned"),
    ("WRONG vs RIGHT", "Examples section"),
    ("NEVER say \"booked\"", "Warning about pretending"),
]

print("\nKey phrases check:")
for phrase, description in checks:
    if phrase in prompt:
        print(f"✅ Found: {description}")
    else:
        print(f"❌ Missing: {description}")

print(f"\nPrompt length: {len(prompt)} characters")
print(f"\nFirst 500 characters:")
print(prompt[:500])

print("\n" + "="*70)
