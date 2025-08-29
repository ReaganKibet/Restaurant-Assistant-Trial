import json
import os
import re

def camel_to_snake(name):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

def normalize_category(value: str) -> str:
    mapping = {
        'appetizer': ['appetizer', 'starter', 'starters', 'appetizers'],
        'main_course': ['main course', 'main', 'entree', 'entrées', 'mains', 'main dishes'],
        'dessert': ['dessert', 'sweets', 'desserts'],
        'beverage': ['beverage', 'drink', 'drinks', 'beverages'],
        'side_dish': ['side', 'side dish', 'sides', 'side dishes']
    }
    value_lower = value.strip().lower()
    for key, variants in mapping.items():
        if value_lower in variants:
            return key
    print(f"⚠️ Unknown category: '{value}' → falling back to 'main_course'")
    return 'main_course'  # fallback

def normalize_cuisine_type(value: str) -> str:
    mapping = {
        'italian': ['italian', 'italia', 'pasta', 'pizza'],
        'mexican': ['mexican', 'mex'],
        'japanese': ['japanese', 'japan', 'sushi'],
        'chinese': ['chinese', 'china'],
        'indian': ['indian', 'india', 'curry'],
        'french': ['french', 'france'],
        'american': ['american', 'usa', 'classic american'],
        'mediterranean': ['mediterranean', 'med'],
        'thai': ['thai', 'thailand'],
        'korean': ['korean', 'korea'],
        'greek': ['greek', 'greece'],
        'spanish': ['spanish', 'spain', 'tapas'],
        'lebanese': ['lebanese', 'lebanon'],
        'turkish': ['turkish', 'turkey'],
        'swahili': ['swahili', 'kenyan', 'east african', 'african'],
        'other': ['fusion', 'international', 'other', 'misc', 'varies']
    }
    value_lower = value.strip().lower()
    for key, variants in mapping.items():
        if value_lower in variants:
            return key
    print(f"⚠️ Unknown cuisine: '{value}' → falling back to 'other'")
    return 'other'  # fallback

def rename_and_normalize(obj):
    if isinstance(obj, dict):
        new_dict = {}
        key_mapping = {
            'mealType': 'category',
            'cuisine': 'cuisine_type',
            'spiceLevel': 'spice_level',
            'preparationTime': 'preparation_time',
            'isVegetarian': 'is_vegetarian',
            'isVegan': 'is_vegan',
            'isGlutenFree': 'is_gluten_free',
            'isDairyFree': 'is_dairy_free',
            'nutritionalInfo': 'nutritional_info',
            'dietaryTags': 'dietary_tags'
        }
        for k, v in obj.items():
            new_key = key_mapping.get(k, camel_to_snake(k))
            new_value = rename_and_normalize(v)

            # Special normalization
            if new_key == "category" and isinstance(new_value, str):
                new_value = normalize_category(new_value)
            elif new_key == "cuisine_type" and isinstance(new_value, str):
                new_value = normalize_cuisine_type(new_value)

            new_dict[new_key] = new_value
        return new_dict
    elif isinstance(obj, list):
        return [rename_and_normalize(item) for item in obj]
    else:
        return obj

# 🔧 Path to your file
file_path = r'C:\Users\Elitebook\OneDrive\Documents\PROJECTS\Servio Trial 1\Restaurant Assistant Trial 4\data\menu_data.json'

if not os.path.exists(file_path):
    print(f"❌ File not found: {file_path}")
    exit(1)

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"✅ Loaded: {file_path}")

    # Convert and normalize
    converted_data = rename_and_normalize(data)

    # Overwrite same file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(converted_data, f, indent=2, ensure_ascii=False)

    print(f"🎉 Success! Updated and normalized keys/values in:\n   {file_path}")
    print("🔹 camelCase → snake_case")
    print("🔹 'Main Course' → 'main_course', 'Italian' → 'italian', etc.")
    print("✅ Your MenuItem model will now validate correctly.")

except Exception as e:
    print(f"💥 Error: {e}")