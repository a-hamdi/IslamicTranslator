# IslamicTranslator

**IslamicTranslator** is an automated solution for translating Hadiths into multiple languages using Google Large Language Models (LLM) like Gemini. This tool breaks the translation process into manageable steps, ensuring accuracy by handling incomplete translations and aggregating results properly.

---




## Features

- **Batch Processing**: Iteratively translates Hadiths in batches, allowing for efficient management of large datasets.
- **Translation Validation**: Handles cases where translations are incomplete by identifying and excluding corrupted data.
- **Automated Error Handling**: Automatically reprocesses missing or improperly translated Hadiths.
- **Aggregation**: Combines all successfully translated Hadiths into a single output file.
- **Customizable**: Configure batch sizes and translation steps to adapt to your needs.

---
<img src="https://github.com/user-attachments/assets/07eee75a-73c6-4b41-9add-ad1c7bdb5f63" alt="Flowchart" width="1000" height="auto">


## How the Process Works

1. Load input Hadiths from a JSON file.
2. **Batch Translation**:
   - Translate Hadiths in batches (default = 20 Hadiths per batch).
   - Save each batch separately.
   - Exclude the last element of any batch if it appears incomplete (e.g., translation was cut off).
3. Combine translated batches, excluding incomplete entries.
4. Compare combined translations with the original file to identify untranslated Hadiths.
5. Retranslate missing Hadiths:
   - If less than 20 are missing, translate in batches of 5.
   - Otherwise, process in batches of 20.
6. Aggregate all translations into a single file.

---

## Requirements

### Dependencies

To use IslamicTranslator, you need to install the following Python dependencies:

- `google.generativeai` 
- `json`
- `argparse`

Install dependencies via pip:

```bash
pip install google-generativeai
```

---

## Usage

### Command Line Arguments

| Argument               | Short Flag | Description                           |
|------------------------|------------|---------------------------------------|
| `--api-key`            | `-k`       | Your Google Gemini API key.          |
| `--input-file`        |  `-i`       | Path to the input JSON file of Hadiths.|
| `--target-language` | `-t` | Target language for translation (e.g., Japanese, French, Spanish) |

### Example Input JSON File Format

The format of the input file should look like the following:

```json
{
  "hadiths": [
    {
      "id": 1,
      "arabic": "عربي النص.",
      "english": {
        "narrator": "Narrated by Abu Huraira:",
        "text": "The Messenger of Allah said..."
      }
    },
    {
      "id": 2,
      "arabic": "عربي النص ٢.",
      "english": "Another hadith text in English..."
    }
  ]
}
```

If you have a json file with a different format, change the code to make it compatible.
### Running the Script

Once your input file is ready, you can run the script as follows:

```bash
python hadith_translator.py --api-key "<YOUR_GEMINI_API_KEY>" --input-file "<YOUR_INPUT_JSON_FILE>" --target-language "language"
```

Example:

```bash
python hadith_translator.py --api-key "Api_key" --input-file "muslim.json" -t "japanese"
```

---

## Output Files

1. **Batch Translations Directory**:
   Translations are saved as individual JSON files in the `batch_translations` directory. Example:

   ```
   batch_translations/
   ├── batch_1.json
   ├── batch_2.json
   └── batch_3.json
   ```

2. **Final Aggregated Translation File**:
   The final translated Hadiths are stored in `final_translations.json`. Example:

   ```json
   [
     {
       "id": 1,
       "japanese": "日本語への翻訳: ..."
     },
     {
       "id": 2,
       "japanese": "別のハディース日本語翻訳..."
     }
   ]
   ```

---

## Highlights of the Code

### Key Methods

- `create_batch_prompt`: Generates prompts for the translation batches in a model-compatible format.
- `parse_gemini_response`: Parses the translation responses from the Gemini API.
- `combine_batches_except_last`: Combines the translated batches while ignoring the problematic last items in incomplete batches.
- `find_missing_hadiths`: Identifies untranslated Hadiths by comparing the combined translations with the original input.
- `process_all`: Orchestrates the entire workflow, from initial translation to final output.

### Example Debugging and Issue Handling

- **Error Handling**: Automatically skips errors, prevents crashes, and continues with subsequent batches.
- **Timeouts**: Includes a `time.sleep(3)` to handle API rate limits.

---

## Folder Structure

```plaintext
.
├── hadith_translator.py   # Main script for translating Hadiths.
├── input_file.json        # An example input JSON file.
├── batch_translations/    # Folder where batch outputs are stored.
├── final_translations.json  # Aggregated final output file.
└── README.md              # Instructions and documentation.
```

---

## Next Steps and Improvements

- **Support Additional Languages**: Configure multiple target languages with user input.
- **Enhanced Error Recovery**: Improve handling of corrupted API responses.
- **Custom Models**: Allow users to choose from different Google LLM variants.
- **Integration with Cloud Storage**: Save and retrieve input/output files directly from cloud storage solutions like Google Drive or AWS S3.

---

## License

This project is open-sourced under the MIT License. See the [LICENSE](https://opensource.org/licenses/MIT) file for details.

---

## Acknowledgements

- Special thanks to the AhmedBaset : https://github.com/AhmedBaset/hadith-json for providing the json files!
- Built using the [Google Gemini API](https://developers.generativeai.google/).

---

## Contributing

Contributions are welcome! If you find any bugs or have suggestions for improvement, feel free to open an issue or submit a pull request.


