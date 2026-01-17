import os
import urllib.request
import urllib.error
import json
import sys

# Configuration
OUTPUT_FILE = "seed_simulator.html"
SRC_DIR = "src"
WORDLIST_PATH = "english.txt"
LIBS_DIR = "libs"

# Library candidates (Mirrors)
# We need bitcoinjs-lib. 
# BIP39 will be implemented manually with injected wordlist to avoid large dependency.
LIBS = [
    {
        "name": "buffer",
        "filename": "buffer.js",
        "urls": [
            "https://bundle.run/buffer@6.0.3",
            "https://unpkg.com/buffer@6.0.3/index.js" # This might be CJS, risky
        ],
        "comment": "Buffer polyfill"
    },
    {
        "name": "bitcoinjs-lib",
        "filename": "bitcoinjs-lib.js",
        "urls": [
            "https://bundle.run/bitcoinjs-lib@5.2.0",
            "https://wzrd.in/standalone/bitcoinjs-lib@5.2.0",
            "https://unpkg.com/bitcoinjs-lib@5.2.0/dist/bitcoinjs-lib.min.js",
            "https://cdn.jsdelivr.net/npm/bitcoinjs-lib@5.2.0/dist/bitcoinjs-lib.min.js",
            "https://raw.githubusercontent.com/bitcoinjs/bitcoinjs-lib/master/dist/bitcoinjs-lib.min.js",
            "https://coinb.in/js/bitcoinjs-lib.js", # fallback
        ],
        "comment": "BitcoinJS: Address derivation"
    }
]

def read_file(path):
    if not os.path.exists(path):
        return ""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def download_lib(lib_entry):
    name = lib_entry["name"]
    for url in lib_entry["urls"]:
        try:
            print(f"Attempting to download {name} from {url}...")
            # Use urllib instead of requests
            with urllib.request.urlopen(url, timeout=10) as response:
                if response.status == 200:
                    print(f"✓ Downloaded {name}")
                    return response.read().decode('utf-8')
        except Exception as e:
            print(f"✗ Failed {url}: {e}")
    
    print(f"!! COULD NOT DOWNLOAD {name} from any source.")
    return None

def main():
    download_only = "--download-only" in sys.argv
    
    if download_only:
        print("Running in DOWNLOAD ONLY mode...")
        if not os.path.exists(LIBS_DIR):
            os.makedirs(LIBS_DIR)

    # 1. Prepare Libraries (Local vs Remote)
    libs_content = ""
    
    for lib in LIBS:
        content = None
        local_path = os.path.join(LIBS_DIR, lib["filename"])
        
        # A. Check Local
        if os.path.exists(local_path):
            print(f"✓ Using local library: {lib['name']} ({local_path})")
            content = read_file(local_path)
            
        # B. Download if missing
        if not content:
            if download_only:
                print(f"Downloading {lib['name']} for offline use...")
            content = download_lib(lib)
            
            # Save if in download mode or if we just want to cache it? 
            # Let's clean: if download_only, we MUST save. 
            if content and download_only:
                with open(local_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  Saved to {local_path}")
                
        if content:
            if not download_only:
                libs_content += f"\n/* {lib['name']} */\n<script>\n{content}\n</script>\n"
                
                # SHIM: BitcoinJS requires global Buffer immediately
                if lib["name"] == "buffer":
                    libs_content += "<script>if(window.buffer) { window.Buffer = window.buffer.Buffer; console.log('Buffer shim applied'); }</script>\n"
        else:
            print(f"WARNING: Missing library {lib['name']}")

    if download_only:
        print("\n✓ Libraries downloaded. You can now transfer this folder to an offline machine.")
        print(f"  Run 'python3 build.py' on the offline machine to build.")
        return

    print("Building single-file Seed Simulator...")

    # Read source files
    html = read_file(os.path.join(SRC_DIR, "index.html"))
    css = read_file(os.path.join(SRC_DIR, "style.css"))
    js = read_file(os.path.join(SRC_DIR, "script.js"))
    
    # Load Wordlist
    words = read_file(WORDLIST_PATH).splitlines()
    words_json = json.dumps(words)
    js_wordlist = f"const BIP39_WORDLIST = {words_json};\n"
    
    # Inject CSS
    html = html.replace("<!-- STYLE_INJECTION -->", f"<style>\n{css}\n</style>")
    
    # Inject Libraries
    html = html.replace("<!-- LIBRARY_INJECTION -->", libs_content)
    
    # Inject Main Script (Prepend wordlist)
    full_js = js_wordlist + js
    html = html.replace("<!-- SCRIPT_INJECTION -->", f"<script>\n{full_js}\n</script>")
    
    # Write output
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
        
    print(f"✓ Created {OUTPUT_FILE} ({os.path.getsize(OUTPUT_FILE)} bytes)")


if __name__ == "__main__":
    main()
