import os
import requests
import json

# Configuration
OUTPUT_FILE = "seed_simulator.html"
SRC_DIR = "src"
WORDLIST_PATH = "english.txt"

# Library candidates (Mirrors)
# We need bitcoinjs-lib. 
# BIP39 will be implemented manually with injected wordlist to avoid large dependency.
LIBS = [
    {
        "name": "buffer",
        "urls": [
            "https://bundle.run/buffer@6.0.3",
            "https://unpkg.com/buffer@6.0.3/index.js" # This might be CJS, risky
        ],
        "comment": "Buffer polyfill"
    },
    {
        "name": "bitcoinjs-lib",
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
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✓ Downloaded {name}")
                return response.text
        except Exception as e:
            print(f"✗ Failed {url}: {e}")
    
    print(f"!! COULD NOT DOWNLOAD {name} from any source.")
    return None

def main():
    print("Building single-file Seed Simulator...")
    
    # Read source files
    html = read_file(os.path.join(SRC_DIR, "index.html"))
    css = read_file(os.path.join(SRC_DIR, "style.css"))
    js = read_file(os.path.join(SRC_DIR, "script.js"))
    
    # Load Wordlist
    words = read_file(WORDLIST_PATH).splitlines()
    words_json = json.dumps(words)
    js_wordlist = f"const BIP39_WORDLIST = {words_json};\n"
    
    # Download libraries
    libs_content = ""
    for lib in LIBS:
        content = download_lib(lib)
        if content:
            libs_content += f"\n/* {lib['name']} */\n<script>\n{content}\n</script>\n"
            
            # SHIM: BitcoinJS requires global Buffer immediately
            if lib["name"] == "buffer":
                libs_content += "<script>if(window.buffer) { window.Buffer = window.buffer.Buffer; console.log('Buffer shim applied'); }</script>\n"
        else:
            print(f"WARNING: Missing library {lib['name']}")

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
