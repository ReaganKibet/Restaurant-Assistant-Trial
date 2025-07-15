import json
import os

# Path to your menu_data.json file
menu_data_path = os.path.join(os.path.dirname(__file__), '../data/menu_data.json')

# Load the menu data
with open(menu_data_path, 'r', encoding='utf-8') as f:
    menu_data = json.load(f)

# List of valid cuisine types (lowercase, matching your Enum)
valid_cuisines = [
    "italian", "mexican", "japanese", "chinese", "swahili", "indian", "french", "american",
    "mediterranean", "thai", "korean", "greek", "spanish", "lebanese", "turkish", "other"
]

def fix_cuisine_type(item):
    cuisine = item.get("cuisine_type", "other")
    cuisine_lower = cuisine.lower()
    if cuisine_lower in valid_cuisines:
        item["cuisine_type"] = cuisine_lower
    else:
        item["cuisine_type"] = "other"
    return item

# Fix all items
for item in menu_data.get("items", []):
    fix_cuisine_type(item)

# Save the fixed menu data
with open(menu_data_path, 'w', encoding='utf-8') as f:
    json.dump(menu_data, f, indent=2, ensure_ascii=False)

print("Cuisine types have been fixed to match the Enum values.")
