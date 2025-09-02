import hashlib
import random

class BIP39MnemonicGenerator:
    def __init__(self, entropy_bits=256, wordlist_path='english.txt'):
        assert entropy_bits in [128, 256], "Entropy must be 128 or 256 bits"
        self.entropy_bits = entropy_bits
        self.wordlist = self.load_wordlist(wordlist_path)
    
    def load_wordlist(self, path):
        # Load BIP39 wordlist from a local text file
        with open(path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines()]
    
    def generate_entropy(self):
        # Generate random binary string for entropy
        entropy = ''.join(str(random.randint(0, 1)) for _ in range(self.entropy_bits))
        return entropy

    def get_checksum(self, entropy_bin):
        # Calculate checksum: first N bits of SHA-256 hash
        N = self.entropy_bits // 32
        entropy_bytes = int(entropy_bin, 2).to_bytes(self.entropy_bits // 8, byteorder='big')
        hash_bytes = hashlib.sha256(entropy_bytes).digest()
        hash_bin = ''.join(f'{byte:08b}' for byte in hash_bytes)
        return hash_bin[:N]

    def concat_entropy_and_checksum(self, entropy_bin, checksum_bin):
        # Concatenate entropy and checksum bits
        return entropy_bin + checksum_bin

    def split_into_chunks(self, full_bin):
        # Split bitstring into 11-bit chunks
        return [full_bin[i:i+11] for i in range(0, len(full_bin), 11)]

    def bits_to_words(self, chunks):
        # Convert each 11-bit chunk to its corresponding BIP39 word
        words = []
        for chunk in chunks:
            idx = int(chunk, 2)
            words.append(self.wordlist[idx])
        return words

    def mnemonic(self):
        # High-level function to generate mnemonic
        entropy_bin = self.generate_entropy()
        checksum_bin = self.get_checksum(entropy_bin)
        full_bin = self.concat_entropy_and_checksum(entropy_bin, checksum_bin)
        chunks = self.split_into_chunks(full_bin)
        words = self.bits_to_words(chunks)
        return {
            'entropy': entropy_bin,
            'checksum': checksum_bin,
            'mnemonic': words
        }

# --- usage example ---
def main():
    # Choose 128 or 256 for bits, and make sure 'english.txt' wordlist file is in your script folder
    print("Choose mnemonic length: [1] 12 words (128 bits)  [2] 24 words (256 bits)")
    choice = input("Enter 1 or 2: ").strip()
    if choice == "1":
        entropy_bits = 128
    elif choice == "2":
        entropy_bits = 256
    else:
        print("Invalid choice, defaulting to 24 words.")
        entropy_bits = 256

    # entropy_bits = 256
    generator = BIP39MnemonicGenerator(entropy_bits=entropy_bits, wordlist_path='english.txt')
    result = generator.mnemonic()

    print(f"\nRandom Entropy ({entropy_bits} bits):\n{result['entropy']}\n")
    print(f"Checksum bits: {result['checksum']}\n")
    print("Mnemonic Phrase:")
    print(" ".join(result['mnemonic']))

if __name__ == "__main__":
    main()
