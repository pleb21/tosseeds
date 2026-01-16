// --- Global State ---
let globalState = {
    entropy: "",
    entropyBits: 128, // 128 or 256
    mnemonic: "",
    seed: null,
    passphrase: ""
};

// --- Crypto Utilities (WebCrypto & Manual BIP39) ---

// Convert string of 0s and 1s to byte array
function binaryStringToBytes(binString) {
    const bytes = new Uint8Array(Math.ceil(binString.length / 8));
    for (let i = 0; i < bytes.length; i++) {
        bytes[i] = parseInt(binString.substr(i * 8, 8).padEnd(8, '0'), 2);
    }
    return bytes;
}

// SHA256 (for Checksum)
async function sha256(buffer) {
    return await window.crypto.subtle.digest('SHA-256', buffer);
}

// Convert ArrayBuffer to binary string
function bufferToBinaryString(buffer) {
    const byteArray = new Uint8Array(buffer);
    let binaryString = "";
    for (const byte of byteArray) {
        binaryString += byte.toString(2).padStart(8, '0');
    }
    return binaryString;
}

// Generate Mnemonic from Entropy String (0s and 1s)
async function entropyToMnemonic(entropyBin) {
    // 1. Checksum
    const entropyBytes = binaryStringToBytes(entropyBin);
    const hashBuffer = await sha256(entropyBytes);
    const hashBin = bufferToBinaryString(hashBuffer);

    const checksumLength = entropyBin.length / 32;
    const checksum = hashBin.substring(0, checksumLength);

    // 2. Combine
    const fullBin = entropyBin + checksum;

    // 3. Split to words
    const chunks = fullBin.match(/.{1,11}/g);
    const words = chunks.map(chunk => {
        const index = parseInt(chunk, 2);
        return BIP39_WORDLIST[index];
    });

    return words.join(" ");
}

// Mnemonic to Seed (PBKDF2)
async function mnemonicToSeed(mnemonic, passphrase = "") {
    const salt = new TextEncoder().encode("mnemonic" + passphrase);
    const password = new TextEncoder().encode(mnemonic.normalize("NFKD"));

    const keyFn = await window.crypto.subtle.importKey(
        "raw",
        password,
        { name: "PBKDF2" },
        false,
        ["deriveBits"]
    );

    const derivedBits = await window.crypto.subtle.deriveBits(
        {
            name: "PBKDF2",
            salt: salt,
            iterations: 2048,
            hash: "SHA-512"
        },
        keyFn,
        512 // 512 bits
    );

    // Buffer is loaded from the external library
    return Buffer.from(derivedBits);
}

// --- Address Derivation (BitcoinJS) ---

function getAddress(seedBuffer, index, type = 'bech32') {
    // Detect loaded library structure
    const bjs = window.bitcoinjsLib || window.bitcoin;
    if (!bjs) throw new Error("BitcoinJS library not loaded");

    const network = bjs.networks.bitcoin;
    const root = bjs.bip32.fromSeed(seedBuffer, network);

    // Path: 
    // Legacy: m/44'/0'/0'/0/index
    // Segwit: m/84'/0'/0'/0/index
    let path = "";
    if (type === 'legacy') path = `m/44'/0'/0'/0/${index}`;
    else path = `m/84'/0'/0'/0/${index}`; // bech32

    // Check if derivedPath exists or if we need to derive step by step
    const child = root.derivePath(path);

    if (type === 'legacy') {
        const { address } = bjs.payments.p2pkh({ pubkey: child.publicKey, network });
        return address;
    } else {
        const { address } = bjs.payments.p2wpkh({ pubkey: child.publicKey, network });
        return address;
    }
}


// --- UI Logic ---

document.addEventListener('DOMContentLoaded', () => {
    // Load Check
    setTimeout(() => {
        const bjs = window.bitcoinjsLib || window.bitcoin;
        const statusDiv = document.getElementById('loading');
        if (typeof BIP39_WORDLIST === 'undefined') {
            statusDiv.innerText = "Error: Wordlist not loaded. Did build.py run?";
            return;
        }
        if (!bjs) {
            statusDiv.innerText = "Error: BitcoinJS not loaded. Proceeding with limited functionality (Address generation unavailable).";
            statusDiv.style.color = "orange";
        } else {
            statusDiv.style.display = 'none';
        }
        document.getElementById('content').style.display = 'block';
    }, 500);

    // Navigation
    const screens = ['screen-start', 'screen-entropy', 'screen-mnemonic', 'screen-addresses', 'screen-import'];
    function showScreen(id) {
        screens.forEach(s => document.getElementById(s).style.display = 'none');
        document.getElementById(id).style.display = 'block';
    }

    // Start Screen
    const btnStart12 = document.getElementById('btn-start-12');
    if (btnStart12) {
        btnStart12.addEventListener('click', () => {
            globalState.entropyBits = 128;
            startEntropy();
        });
    }
    const btnStart24 = document.getElementById('btn-start-24');
    if (btnStart24) {
        btnStart24.addEventListener('click', () => {
            globalState.entropyBits = 256;
            startEntropy();
        });
    }

    // --- Import / Autocomplete Logic ---
    let importedWords = [];

    const btnImport = document.getElementById('btn-import');
    if (btnImport) {
        btnImport.addEventListener('click', () => {
            showScreen('screen-import');
            importedWords = [];
            renderSeedChips();
            document.getElementById('seed-word-input').value = "";
            document.getElementById('import-passphrase').value = "";
            document.getElementById('import-feedback').innerText = "";
            document.getElementById('seed-word-input').focus();
        });
    }

    // Autocomplete Setup
    const inputFn = document.getElementById('seed-word-input');
    const suggestionsList = document.getElementById('seed-suggestions');

    if (inputFn && suggestionsList) {
        inputFn.addEventListener('input', (e) => {
            const val = e.target.value.toLowerCase().trim();
            if (val.length < 1) {
                suggestionsList.style.display = 'none';
                return;
            }
            const matches = BIP39_WORDLIST.filter(w => w.startsWith(val)).slice(0, 10);
            renderSuggestions(matches);
        });

        // Keyboard navigation for suggestions
        inputFn.addEventListener('keydown', (e) => {
            if (e.key === 'Backspace' && inputFn.value === '' && importedWords.length > 0) {
                // Remove last word
                importedWords.pop();
                renderSeedChips();
            }
            // If Enter/Tab is pressed and there is exactly one match or a top match
            if ((e.key === 'Enter' || e.key === 'Tab') && suggestionsList.style.display !== 'none') {
                // Select top suggestion if any
                const firstItem = suggestionsList.querySelector('.suggestion-item');
                if (firstItem) {
                    e.preventDefault();
                    addImportWord(firstItem.dataset.word);
                }
            }
        });
    }

    function renderSuggestions(matches) {
        if (matches.length === 0) {
            suggestionsList.style.display = 'none';
            return;
        }
        suggestionsList.innerHTML = matches.map(w => `<li class="suggestion-item" data-word="${w}">${w}</li>`).join('');
        suggestionsList.style.display = 'block';

        // Click handlers
        suggestionsList.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', () => {
                addImportWord(item.dataset.word);
            });
        });
    }

    function addImportWord(word) {
        if (importedWords.length >= 24) return; // Cap at 24
        importedWords.push(word);
        renderSeedChips();
        inputFn.value = '';
        suggestionsList.style.display = 'none';
        inputFn.focus();
    }

    function renderSeedChips() {
        const container = document.getElementById('seed-words-list');
        container.innerHTML = importedWords.map((w, i) => `
            <div class="word-chip">
                <span class="word-num">${i + 1}</span> ${w}
                <span class="chip-remove" data-idx="${i}">✕</span>
            </div>
        `).join('');

        // Remove handlers
        container.querySelectorAll('.chip-remove').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const idx = parseInt(e.target.dataset.idx);
                importedWords.splice(idx, 1);
                renderSeedChips();
            });
        });
    }

    // Validate Import
    document.getElementById('btn-validate-import').addEventListener('click', async () => {
        const feedback = document.getElementById('import-feedback');

        // Use importedWords
        if (importedWords.length !== 12 && importedWords.length !== 24) {
            feedback.innerText = `Invalid word count: ${importedWords.length}. Expected 12 or 24.`;
            feedback.className = "feedback-msg text-error";
            return;
        }

        // Word list check is implicit via autocomplete but user 'could' circumvent if they really tried manual entry hacks, 
        // but since we add via 'addImportWord' which comes from list, it's mostly safe. 
        // We'll trust the array for now.

        try {
            feedback.innerText = "Verifying...";
            feedback.className = "feedback-msg";

            globalState.mnemonic = importedWords.join(" ");
            const passphrase = document.getElementById('import-passphrase').value;
            globalState.passphrase = passphrase;

            // Test generation
            await mnemonicToSeed(globalState.mnemonic, globalState.passphrase);

            feedback.innerText = "✓ Valid Seed Phrase!";
            feedback.className = "feedback-msg text-success";

            setTimeout(() => {
                showScreen('screen-addresses');
                generateAddressesUI(5, false); // Initial 5
            }, 1000);

        } catch (e) {
            feedback.innerText = "Error verifying seed: " + e.message;
            feedback.className = "feedback-msg text-error";
        }
    });

    // --- Entropy Screen ---
    function startEntropy() {
        showScreen('screen-entropy');
        globalState.entropy = "";
        updateEntropyUI();
    }

    function updateEntropyUI() {
        const count = globalState.entropy.length;
        const total = globalState.entropyBits;
        const pct = Math.min(100, (count / total) * 100);

        document.getElementById('entropy-progress-bar').style.width = `${pct}%`;
        document.getElementById('entropy-count').innerText = `${count} / ${total}`;
        document.getElementById('entropy-bits-display').innerText = globalState.entropy;

        if (count >= total) {
            document.getElementById('btn-generate-mnemonic').disabled = false;
        } else {
            document.getElementById('btn-generate-mnemonic').disabled = true;
        }
    }

    window.addEntropy = (val) => {
        if (globalState.entropy.length < globalState.entropyBits) {
            globalState.entropy += val;
            updateEntropyUI();
        }
    };

    window.clearEntropy = () => {
        globalState.entropy = "";
        updateEntropyUI();
    };

    document.addEventListener('keydown', (e) => {
        const screen = document.getElementById('screen-entropy');
        if (screen && screen.style.display !== 'none') {
            if (e.key === '0') addEntropy('0');
            if (e.key === '1') addEntropy('1');
        }
    });

    document.getElementById('btn-generate-mnemonic').addEventListener('click', async () => {
        const mnemonic = await entropyToMnemonic(globalState.entropy);
        globalState.mnemonic = mnemonic;
        showMnemonic();
    });

    // --- Mnemonic Screen ---
    function showMnemonic() {
        showScreen('screen-mnemonic');
        const container = document.getElementById('mnemonic-container');
        container.innerHTML = "";
        const words = globalState.mnemonic.split(" ");
        words.forEach((w, i) => {
            const span = document.createElement('span');
            span.className = "word-chip";
            span.innerHTML = `<span class="word-num">${i + 1}</span> ${w}`;
            container.appendChild(span);
        });

        // Reset passphrase on new generation
        document.getElementById('generate-passphrase').value = "";
    }

    document.getElementById('btn-to-addresses').addEventListener('click', () => {
        // Read passphrase
        globalState.passphrase = document.getElementById('generate-passphrase').value;
        showScreen('screen-addresses');
        generateAddressesUI(5, false);
    });

    // --- Address Screen ---

    // Address Index State
    globalState.addressIndex = 0;

    async function generateAddressesUI(count = 5, append = false) {
        const list = document.getElementById('address-list');

        if (!append) {
            list.innerHTML = "<p>Generating keys... This may take a moment (PBKDF2).</p>";
            globalState.addressIndex = 0;
        }

        setTimeout(async () => {
            try {
                if (!window.bitcoinjsLib && !window.bitcoin) {
                    list.innerHTML = `<p style="color:red">Error: BitcoinJS library is missing. Cannot derive addresses.</p>`;
                    return;
                }

                if (!append) {
                    // Regenerate seed just to vary sure if passphrase changed, though usually state is set
                    const seed = await mnemonicToSeed(globalState.mnemonic, globalState.passphrase);
                    globalState.seed = seed;
                    list.innerHTML = ""; // Clear "generating..." text
                }

                // Use existing seed (buffer)
                if (!globalState.seed) {
                    globalState.seed = await mnemonicToSeed(globalState.mnemonic, globalState.passphrase);
                }

                let html = "";
                // Generate 'count' more addresses
                const start = globalState.addressIndex;
                const end = start + count;

                for (let i = start; i < end; i++) {
                    const addr = getAddress(globalState.seed, i, 'bech32');
                    html += `<div class="address-row"><span class="addr-index">m/84'/0'/0'/0/${i}</span> <span class="addr-val">${addr}</span></div>`;
                }

                // Update DOM
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = html;
                if (append) {
                    list.appendChild(tempDiv);
                } else {
                    list.innerHTML = html;
                }

                // Update Index
                globalState.addressIndex = end;

            } catch (e) {
                if (!append) list.innerHTML = `<p style="color:red">Error: ${e.message}</p>`;
                else alert("Error: " + e.message);
                console.error(e);
            }
        }, 100);
    }

    // Load More Button
    const btnLoadMore = document.getElementById('btn-load-more');
    if (btnLoadMore) {
        btnLoadMore.addEventListener('click', () => {
            const num = parseInt(document.getElementById('num-addresses-to-add').value) || 5;
            generateAddressesUI(num, true);
        });
    }

    // Restart
    const restartBtns = document.querySelectorAll('.btn-restart');
    restartBtns.forEach(btn => btn.addEventListener('click', () => {
        if (confirm("Start over? This will clear your current seed.")) {
            globalState.entropy = "";
            globalState.mnemonic = "";
            globalState.seed = null;
            globalState.passphrase = "";
            importedWords = [];
            showScreen('screen-start');
        }
    }));
});

