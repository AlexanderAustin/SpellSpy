from pynput import keyboard
from spellchecker import SpellChecker
import json
import os
import nltk
from nltk.util import bigrams

# Initialize spellchecker
spell = SpellChecker()

# File paths
raw_file = "misspelled_words_raw.json"
corrected_file = "misspelled_words_corrected.json"

# Load or create storage files
def load_data(file_path):
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            json.dump({}, f)  # Create an empty JSON file
    with open(file_path, 'r') as f:
        return json.load(f)

def save_data(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f)

# Logging misspelled and corrected words
def log_misspelled_word(raw, corrected):
    # Load existing data or initialize empty dictionaries
    raw_data = load_data(raw_file)
    corrected_data = load_data(corrected_file)
    
    # Log raw misspelling
    if raw in raw_data:
        raw_data[raw] += 1
    else:
        raw_data[raw] = 1

    # Log corrected version
    if raw not in corrected_data:
        corrected_data[raw] = corrected  # Only add if not already present
    
    # Save both files
    save_data(raw_file, raw_data)
    save_data(corrected_file, corrected_data)

# Buffer for word capturing
buffer = []
context_window = []  # Stores the context of previous words

def get_context_correction(word, context_window):
    # Use trigrams for context
    context_window.append(word)  # Include the current word
    if len(context_window) > 2:
        # Use previous, current, and next words (trigram)
        trigram_context = list(nltk.trigrams(context_window))
        for trigram in trigram_context:
            prev_word, current_word, next_word = trigram
            if current_word == word and word not in spell:
                # Use suggestions for the current word
                suggestions = spell.candidates(word)
                if suggestions:
                    # Return the most likely suggestion for now
                    return list(suggestions)[0]
    # If no suggestions or insufficient context, return as is
    return word

def on_press(key):
    global buffer, context_window
    try:
        if key == keyboard.Key.space or key == keyboard.Key.enter:
            # Join buffer to form the current word
            word = ''.join(buffer).strip()
            buffer = []  # Clear buffer for the next word

            if word and not word.isnumeric():
                # Add word to the context window
                context_window.append(word)
                if len(context_window) > 5:  # Maintain the last 5 words
                    context_window.pop(0)

                # Check for misspellings
                if word not in spell:
                    # Predict the intended word using trigram context
                    corrected = get_context_correction(word, context_window)
                    log_misspelled_word(word, corrected)
        elif key == keyboard.Key.backspace:
            if buffer:
                buffer.pop()
        elif hasattr(key, 'char') and key.char is not None:
            buffer.append(key.char)
    except Exception as e:
        print(f"Error: {e}")


# Start the keylogger
def start_keylogger():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

if __name__ == "__main__":
    # Ensure NLTK punkt data is available
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        print("Downloading NLTK 'punkt' data...")
        nltk.download('punkt')
    start_keylogger()


def formatCorrectedWords():
    # Load the misspelled words from the JSON file
    with open('misspelled_words.json', 'r') as f:
        misspelled_data = json.load(f)

    # Extract the corrected words
    corrected_words = [entry["corrected_word"] for entry in misspelled_data]

    # Write the corrected words to a text file, one per line
    with open('corrected_words.txt', 'w') as f:
        for word in corrected_words:
            f.write(word + '\n')

    print("Corrected words saved to 'corrected_words.txt'.")