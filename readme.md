# Bitcoin Mnemonic & Address Generator

A simple, offline Python tool for generating Bitcoin mnemonics (seed phrases) and receiving addresses. Built for educational purposes and personal use with security and transparency in mind.

---

## What Can You Do?

### Generate a New Mnemonic from Coin Flips
The most secure way to create a Bitcoin wallet. Flip a coin 128 times (for 12 words) or 256 times (for 24 words), and this tool converts your random flips into a valid BIP39 mnemonic phrase.

**Why coin flips?** True randomness is critical for Bitcoin security. Coin flips provide verifiable, physical randomness that you control completely.

### Import an Existing Mnemonic
Already have a seed phrase? Enter your 12 or 24-word mnemonic to generate receiving addresses from it. The tool validates each word against the official BIP39 wordlist.

### Add a Passphrase (Optional)
Enhance your security with an optional BIP39 passphrase (sometimes called the "25th word"). This creates an entirely different set of addresses from the same mnemonic.

### Generate Receiving Addresses
Create Bitcoin addresses to receive funds:
- **Native SegWit (Bech32)** - Modern format starting with `bc1` (recommended)
- **Legacy (P2PKH)** - Classic format starting with `1`

Generate up to 10 addresses at once from your mnemonic.

---

## Security Features

### Completely Offline
This tool runs entirely on your computer. No internet connection required, no data sent anywhere.

### Open Source & Auditable
All code is visible and can be reviewed. You can read every line to understand exactly what it does.

### No Data Storage
The script doesn't save your mnemonics, passphrases, or addresses anywhere. Everything exists only in your terminal session.

### Industry-Standard Libraries
Uses `bip_utils`, a well-maintained Python library implementing official Bitcoin Improvement Proposals (BIP39, BIP44, BIP84).

---

## Security Warnings

### NEVER Use Random Generation for Real Funds
The script includes a "random generation" option for **educational purposes only**. Computer-generated randomness is NOT suitable for securing real Bitcoin. Always use coin flips for actual wallets.

### Verify Your Addresses
After generating addresses, verify them with another trusted wallet (like Electrum or Bitcoin Core) before receiving real funds. Cross-reference that the same mnemonic produces the same addresses.

### Protect Your Mnemonic
- Write it down on paper (never store digitally)
- Keep it in a secure location
- Never share it with anyone
- Never enter it on websites or untrusted software

### Don't Trust, Verify
While I've built this tool with care, you should:
- Review the source code yourself
- Test with small amounts first
- Understand what each function does
- Use air-gapped computers for maximum security

---

## Getting Started

### Requirements
- Python 3.7+
- `bip_utils` library

### Installation

1. **Clone or download this repository**
   ```bash
   git clone git@github.com:pleb21/tosseeds.git
   cd tosseeds
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download BIP39 wordlist**
   
   Save the official English BIP39 wordlist as `english.txt` in the same directory. You can find it at:
   https://github.com/bitcoin/bips/blob/master/bip-0039/english.txt

### Single-File HTML Version (Offline UI)

To use the graphical interface in an air-gapped environment:

1. **Build the HTML file** (Requires Internet once):
   ```bash
   python3 build.py
   ```
   This downloads necessary JS libraries and bundles them into `seed_simulator.html`.

2. **Go Offline**: Transfer `seed_simulator.html` to your air-gapped machine via USB.

3. **Run**: Open the file in any modern web browser. 

### Usage

Run the script:
```bash
python toss_or_generate.py
```

Follow the interactive prompts to:
1. Choose between generating a new mnemonic or using an existing one
2. Select 12 or 24 words
3. Input coin flips or enter your mnemonic
4. Optionally add a passphrase
5. Generate receiving addresses

---

## How It Works

This tool follows Bitcoin's official standards:

- **BIP39**: Converts entropy (randomness) into human-readable mnemonic phrases
- **BIP44**: Hierarchical Deterministic wallet structure for Legacy addresses
- **BIP84**: Hierarchical Deterministic wallet structure for Native SegWit addresses

Your coin flips → Binary entropy → Checksum added → Converted to words → Valid mnemonic phrase → Derivation path → Bitcoin addresses

---

## Contributing

Found a bug? Have a suggestion? Open an issue or submit a pull request. Security-related issues should be reported privately.

---

## ⚖️ Disclaimer

**This tool is provided "as-is" without any warranty.** You are solely responsible for the security of your Bitcoin. The author assumes no liability for any loss of funds. Always practice good operational security and test thoroughly before using with real funds.

**Educational Use**: This project is primarily for learning about Bitcoin's technical standards. For production use, consider established wallet software with extensive security audits.

---

## Acknowledgments

Built with:
- [bip_utils](https://github.com/ebellocchia/bip_utils) - Python BIP implementation
- Bitcoin community's BIP standards
- The spirit of open-source and financial sovereignty

---

**Remember: Not your keys, not your coins.**
