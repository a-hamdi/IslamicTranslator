
import google.generativeai as genai
import json
import time
from typing import Dict, List
import os
import argparse
class HadithTranslator:
    def __init__(self, api_key: str, input_file: str, target_language: str):
        self.api_key = api_key
        self.input_file = input_file
        self.target_language = target_language
        self.output_dir = "batch_translations"
        self.gemini_model = self.setup_gemini()
        os.makedirs(self.output_dir, exist_ok=True)

    def setup_gemini(self):
        """Initialize Gemini API"""
        genai.configure(api_key=self.api_key)
        return genai.GenerativeModel(model_name="gemini-1.5-flash")

    def create_batch_prompt(self, hadiths: List[Dict]) -> List[Dict]:
        """Create a prompt for Gemini to translate multiple hadiths"""
        texts = []
        for hadith in hadiths:
            english_text = ""
            if isinstance(hadith.get('english'), dict):
                narrator = hadith['english'].get('narrator', '')
                text = hadith['english'].get('text', '')
                english_text = f"{narrator} {text}".strip()
            else:
                english_text = str(hadith.get('english', ''))

            arabic_text = hadith.get('arabic', '')
            
            texts.append(
                f"ID: {hadith['id']}\n"
                f"Arabic: {arabic_text}\n"
                f"English: {english_text}"
            )

        header = (
            f"Translate the following hadith texts to {self.target_language}.\n"
            "For each hadith, return only the ID and translation in this exact format:\n"
            f"[ID]: [{self.target_language} translation]\n\n"
            "Here are the hadiths:\n\n"
        )

        return [{"text": header + "\n\n".join(texts)}]

    def parse_gemini_response(self, response_text: str) -> List[Dict]:
        """Parse Gemini's response into a list of ID-translation pairs"""
        translations = []
        current_id = None
        current_translation = []

        for line in response_text.strip().split('\n'):
            line = line.strip()
            if not line:
                continue

            if ':' in line and line.split(':')[0].strip().isdigit():
                if current_id is not None and current_translation:
                    translations.append({
                        'id': current_id,
                        self.target_language.lower(): ' '.join(current_translation)
                    })
                
                parts = line.split(':', 1)
                current_id = int(parts[0].strip())
                current_translation = [parts[1].strip()] if len(parts) > 1 else []
            elif current_id is not None:
                current_translation.append(line)

        if current_id is not None and current_translation:
            translations.append({
                'id': current_id,
                self.target_language.lower(): ' '.join(current_translation)
            })

        return translations

    def save_batch(self, translations: List[Dict], batch_num: int):
        """Save a single batch of translations"""
        batch_file = os.path.join(self.output_dir, f"batch_{batch_num}.json")
        with open(batch_file, 'w', encoding='utf-8') as f:
            json.dump(translations, f, ensure_ascii=False, indent=2)
        print(f"Saved batch {batch_num} to {batch_file}")

    def combine_batches_except_last(self):
        """Combine all batch files, excluding last item of incomplete batches"""
        combined_hadiths = []
        batch_files = sorted([f for f in os.listdir(self.output_dir) if f.endswith('.json')],
                           key=lambda x: int(x.split('_')[1].split('.')[0]))
        
        for filename in batch_files:
            file_path = os.path.join(self.output_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                try:
                    batch_data = json.load(file)
                    if batch_data and isinstance(batch_data, list):
                        if len(batch_data) < 20:
                            combined_hadiths.extend(batch_data[:-1])
                        else:
                            combined_hadiths.extend(batch_data)
                except json.JSONDecodeError as e:
                    print(f"Error reading {filename}: {e}")
        
        return combined_hadiths

    def find_missing_hadiths(self, translated_hadiths: List[Dict]) -> List[Dict]:
        """Find hadiths that weren't translated"""
        with open(self.input_file, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
            original_hadiths = original_data['hadiths']

        translated_ids = set(hadith['id'] for hadith in translated_hadiths)
        missing_hadiths = [h for h in original_hadiths if h['id'] not in translated_ids]
        
        return missing_hadiths

    def translate_hadiths(self, hadiths: List[Dict], batch_size: int = 20):
        """Translate a list of hadiths in batches"""
        translations = []
        batch_num = 1

        for i in range(0, len(hadiths), batch_size):
            batch = hadiths[i:min(i + batch_size, len(hadiths))]
            try:
                contents = self.create_batch_prompt(batch)
                response = self.gemini_model.generate_content(
                    contents,
                    generation_config={},
                    safety_settings={},
                    stream=False
                )
                batch_translations = self.parse_gemini_response(response.text)
                self.save_batch(batch_translations, batch_num)
                translations.extend(batch_translations)
                print(f"Processed batch {batch_num}: {len(batch_translations)} translations")
                batch_num += 1
                time.sleep(3)
            except Exception as e:
                print(f"Error processing batch {batch_num}: {str(e)}")
                continue

        return translations

    def process_all(self):
        """Main processing function"""
        with open(self.input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            hadiths = data['hadiths']

        print("Starting initial translation...")
        self.translate_hadiths(hadiths, batch_size=20)

        print("\nCombining batches...")
        combined_translations = self.combine_batches_except_last()
        
        print("\nChecking for missing hadiths...")
        missing_hadiths = self.find_missing_hadiths(combined_translations)
        
        if missing_hadiths:
            print(f"\nFound {len(missing_hadiths)} missing hadiths")
            batch_size = 5 if len(missing_hadiths) < 20 else 20
            print(f"Processing missing hadiths in batches of {batch_size}...")
            additional_translations = self.translate_hadiths(missing_hadiths, batch_size=batch_size)
            combined_translations.extend(additional_translations)

        final_output = "final_translations.json"
        with open(final_output, 'w', encoding='utf-8') as f:
            json.dump(combined_translations, f, ensure_ascii=False, indent=2)
        
        print(f"\nTranslation complete. Final output saved to: {final_output}")



def main():
    parser = argparse.ArgumentParser(description='Translate hadiths using Google Gemini API')
    parser.add_argument('--api-key', '-k', required=True, help='Google Gemini API key')
    parser.add_argument('--input-file', '-i', required=True, help='Input JSON file containing hadiths')
    parser.add_argument('--target-language', '-t', required=True, 
                      help='Target language for translation (e.g., Japanese, French, Spanish)')
    
    args = parser.parse_args()
    
    translator = HadithTranslator(args.api_key, args.input_file, args.target_language)
    translator.process_all()

if __name__ == "__main__":
    main()