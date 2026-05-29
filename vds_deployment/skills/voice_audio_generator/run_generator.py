import os
import sys
import json
import urllib.request
import urllib.parse
import argparse

# Define directories relative to this script
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
OPENCLAW_DIR = os.path.dirname(os.path.dirname(SKILL_DIR))
MARKETPLACE_DIR = os.path.join(os.path.dirname(OPENCLAW_DIR), "ielts-marketplace")

# JSON databases
OPENCLAW_VOCAB_FILE = os.path.join(OPENCLAW_DIR, "vocab_pack_preview.json")
MARKETPLACE_VOCAB_FILE = os.path.join(MARKETPLACE_DIR, "vocab_pack_preview.json")

# Audio Vault output folders
OPENCLAW_AUDIO_DIR = os.path.join(OPENCLAW_DIR, "audio_vault")
MARKETPLACE_AUDIO_DIR = os.path.join(MARKETPLACE_DIR, "audio_vault")

def download_pronunciation_audio(word, target_dirs):
    """
    Downloads correct pronunciation audio (.mp3) for a word from a free public TTS engine.
    Saves it to all provided target directories.
    """
    encoded_word = urllib.parse.quote(word.lower())
    # Free, pristine, high-fidelity public TTS endpoint stream
    tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&tl=en&client=tw-ob&q={encoded_word}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    }
    
    filename = f"{word.lower()}.mp3"
    req = urllib.request.Request(tts_url, headers=headers)
    
    try:
        print(f"[+] Downloading high-fidelity pronunciation audio stream for: '{word}'...")
        with urllib.request.urlopen(req) as response:
            audio_data = response.read()
            
        for directory in target_dirs:
            if not os.path.exists(directory):
                os.makedirs(directory)
            out_path = os.path.join(directory, filename)
            with open(out_path, "wb") as f:
                f.write(audio_data)
            print(f"[SUCCESS] Saved pronunciation audio guide to: {out_path}")
            
        return f"audio_vault/{filename}"
    except Exception as e:
        print(f"[-] Failed to generate local pronunciation audio for '{word}': {str(e)}")
        return None

def update_json_database(word, audio_path, file_path):
    if not os.path.exists(file_path):
        print(f"[!] Warning: Database file '{file_path}' not found, skipping.")
        return
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            vocab_list = json.load(f)
            
        updated = False
        for item in vocab_list:
            if item["word"].lower() == word.lower():
                item["audio_guide"] = audio_path
                updated = True
                break
                
        if updated:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(vocab_list, f, indent=2, ensure_ascii=False)
            print(f"[+] Successfully updated database: {file_path}")
        else:
            print(f"[!] Word '{word}' not found in database '{file_path}' to update.")
    except Exception as e:
        print(f"[-] Failed to update database '{file_path}': {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="IELTS Vocabulary Local Audio Pronunciation Compiler")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--word", type=str, help="Generate pronunciation for a single word")
    group.add_argument("--all", action="store_true", help="Pre-compile pronunciation for all words in the databases")
    args = parser.parse_args()
    
    target_dirs = [OPENCLAW_AUDIO_DIR, MARKETPLACE_AUDIO_DIR]
    
    if args.word:
        word = args.word.strip()
        print(f"[*] Processing single word pronunciation generator: '{word}'")
        audio_path = download_pronunciation_audio(word, target_dirs)
        if audio_path:
            update_json_database(word, audio_path, OPENCLAW_VOCAB_FILE)
            update_json_database(word, audio_path, MARKETPLACE_VOCAB_FILE)
            
    elif args.all:
        print("=" * 60)
        print("OPENCLAW COMPILER: PRE-COMPILING ALL WORD PRONUNCIATIONS")
        print("=" * 60)
        
        # Load vocab preview file to retrieve list of words
        if not os.path.exists(OPENCLAW_VOCAB_FILE):
            print(f"[-] Error: Source vocabulary database not found at {OPENCLAW_VOCAB_FILE}")
            sys.exit(1)
            
        with open(OPENCLAW_VOCAB_FILE, "r", encoding="utf-8") as f:
            vocab_list = json.load(f)
            
        compiled_count = 0
        for item in vocab_list:
            word = item["word"]
            audio_path = download_pronunciation_audio(word, target_dirs)
            if audio_path:
                item["audio_guide"] = audio_path
                compiled_count += 1
                
        # Save updated databases
        with open(OPENCLAW_VOCAB_FILE, "w", encoding="utf-8") as f:
            json.dump(vocab_list, f, indent=2, ensure_ascii=False)
            
        if os.path.exists(MARKETPLACE_VOCAB_FILE):
            with open(MARKETPLACE_VOCAB_FILE, "w", encoding="utf-8") as f:
                json.dump(vocab_list, f, indent=2, ensure_ascii=False)
                
        print("=" * 60)
        print(f"[SUCCESS] Compile finished! Pre-generated pronunciation for {compiled_count} words.")
        print("=" * 60)

if __name__ == "__main__":
    main()
