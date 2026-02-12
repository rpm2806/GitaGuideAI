
import csv
import json
import os

CSV_PATH = r"d:\GitaGuideAI\Bhagwad_Gita.csv"
JSON_PATH = r"d:\GitaGuideAI\backend\data\gita.json"

def convert_csv_to_json():
    print(f"Reading CSV from {CSV_PATH}...")
    
    if not os.path.exists(CSV_PATH):
        print(f"Error: File not found at {CSV_PATH}")
        return

    gita_data = []
    
    try:
        with open(CSV_PATH, 'r', encoding='utf-8') as csvfile:
            # The CSV seems to have headers: ID,Chapter,Verse,Shloka,Transliteration,HinMeaning,EngMeaning,WordMeaning
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                # Clean up and map fields
                entry = {
                    "chapter": int(row['Chapter']),
                    "verse": int(row['Verse']),
                    "shloka": row['Shloka'].strip(),
                    "transliteration": row['Transliteration'].strip(),
                    "hindi_translation": row['HinMeaning'].strip(),
                    "translation": row['EngMeaning'].strip(),
                    "word_meaning": row['WordMeaning'].strip(),
                    "source_ref": "Bhagwad_Gita.csv"
                }
                gita_data.append(entry)
                
        print(f"Processed {len(gita_data)} verses.")
        
        # Write to JSON
        os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)
        with open(JSON_PATH, 'w', encoding='utf-8') as jsonfile:
            json.dump(gita_data, jsonfile, indent=4, ensure_ascii=False)
            
        print(f"Successfully created {JSON_PATH}")
        
    except Exception as e:
        print(f"Error converting CSV: {e}")

if __name__ == "__main__":
    convert_csv_to_json()
