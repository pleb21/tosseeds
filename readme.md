
# Sovereign Seed Kit

A comprehensive, verifiable, and offline-capable tool for generating Bitcoin seed phrases (BIP39) and deriving receiving addresses.

This tool gives you complete control over your key generation process. It is designed for two distinct use cases:
1.  **Learning & Testing**: Quickly understand how seeds and addresses work. You toss coin, enter the results, get the seed words.
2.  **Cold Storage**: A "Paranoid" way to generate new seed through coin tosses OR getting new receiving addresses for your existing seed in a secure, air-gapped environment. The right way.

---

## 🚀 Quick Start (Learning Mode)

If you just want to test it out or see how it works (do NOT use for real funds on an online computer):

1.  Open **`seed_simulator.html`** in your browser.
2.  Choose **Create New Wallet** / **Existing Wallet**.
3.  Follow the steps to generate entropy (new seed words) or import an existing seed.
4.  View your seed, passphrase, and derived addresses.

Alternatively, run the Python CLI:
```bash
python3 toss_or_generate.py
```

---

## 🛡️ "The Paranoid Guide" (Cold Storage Mode)

For real wealth storage, you should never trust a pre-compiled file or an online machine. Follow this procedure:

### Prerequisites
-   **1x Online Computer**: To download the source code.
-   **1x Offline Computer (Air-Gapped)**: A machine with Python installed that will **NEVER** touch the internet again.
-   **1x USB Drive**: To transfer the code.

### Step 1: Audit & Transfer
1.  Download this repository on your *Online Computer*.
2.  Inspect the `src/` directory. The logic is simple and readable:
    -   `src/index.html`: The UI structure.
    -   `src/script.js`: The brain. Uses standard libraries (`bitcoinjs-lib`) for derivation.
    -   `build.py`: The factory script to combine them.
3.  **Vendor Dependencies**: Run the build script in download mode to save libraries locally:
    ```bash
    python3 build.py --download-only
    ```
    This creates a `libs/` folder containing the necessary JavaScript files.
4.  Copy the entire folder (including the new `libs/` folder) to your **USB Drive**.

### Step 2: The Factory (Offline Build)
1.  Plug the USB drive into your **Offline Computer**.
2.  Copy the files to the offline machine.
3.  Run the build script:
    ```bash
    python3 build.py
    ```
    *The script will detect the local `libs/` folder and use those files instead of trying to download them.*

### Step 3: Ceremony
1.  In the offline browser, open `seed_simulator.html`.
2.  Select **12/24 Words** (256 bits of entropy).
3.  **Flip a real coin 128/256 times**. Enter the results (Head=0, Tail=1).
    -   *Why?* Computers are bad at randomness. Physics is honest.
4.  Write down the **12/24 Seed Words**.
    -   *Optional*: Add a **Passphrase** (13th/25th word) if you wish to. You should wish to.
5.  Write down the **Master Fingerprint** (shown on Address screen) to identify this wallet later.
6.  Generate receiving addresses and photograph/copy/write them down to send funds to.
7.  **Wipe the machine** or destroy the HTML file.

---

## 🛠️ Developer / CLI Usage

You can also use the Python script for terminal-based generation.

```bash
# Install dependencies
pip install -r requirements.txt

# Run
python3 toss_or_generate.py
```

Features:
-   **Coin Toss Mode**: Manual entry of 128/256 bits.
-   **Dictionary Check**: Validates if user-supplied words are in the BIP39 list.
-   **Address Derivation**: Generates Legacy (1...) or SegWit (bc1...) addresses.

---

## 📁 File Structure

```
├── seed_simulator.html  <-- The Product (Single-file, runs in browser)
├── toss_or_generate.py  <-- Python CLI tool
├── build.py             <-- The Factory (Builds the HTML)
├── requirements.txt     <-- Python deps
├── english.txt          <-- Wordlist
└── src/                 <-- Source code for the HTML tool
    ├── index.html
    ├── script.js
    └── style.css
```

---

*Disclaimer: This tool is provided for educational purposes. You are responsible for your own security. Always backup your seed phrases on physical media (paper, metal).*
