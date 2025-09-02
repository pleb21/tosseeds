import hashlib
import random

def load_wordlist(path):
    # Load BIP39 wordlist from a local text file
    with open(path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f.readlines()]

def generate_entropy(entropy_bits):
    # Generate random binary string for entropy
    entropy = ''.join(str(random.randint(0, 1)) for _ in range(entropy_bits))
    return entropy

def get_checksum(entropy_bin, entropy_bits):
    # Calculate checksum: first N bits of SHA-256 hash
    N = entropy_bits // 32
    entropy_bytes = int(entropy_bin, 2).to_bytes(entropy_bits // 8, byteorder='big')
    hash_bytes = hashlib.sha256(entropy_bytes).digest()
    hash_bin = ''.join(f'{byte:08b}' for byte in hash_bytes)
    return hash_bin[:N]

def concat_entropy_and_checksum(entropy_bin, checksum_bin):
    # Concatenate entropy and checksum bits
    return entropy_bin + checksum_bin

def split_into_chunks(full_bin):
    # Split bitstring into 11-bit chunks
    return [full_bin[i:i+11] for i in range(0, len(full_bin), 11)]

def bits_to_words(chunks, wordlist):
    # Convert each 11-bit chunk to its corresponding BIP39 word
    words = []
    for chunk in chunks:
        idx = int(chunk, 2)
        words.append(wordlist[idx])
    return words

def get_entropy_digits(entropy_bits):
    print("\nChoose how you'd like to input your entropy:")
    print("[1] Type bits one by one (more secure, but slower)")
    print("[2] Paste entire bit string at once (faster, be careful!)")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "2":
        while True:
            bits = input(f"Paste your {entropy_bits}-bit binary string:\n").strip()
            if len(bits) == entropy_bits and all(c in '01' for c in bits):
                print("Bit string accepted.")
                return bits
            else:
                print(f"Invalid input. Please paste exactly {entropy_bits} characters of 0s and 1s.")
    else:
        # Default to typing one-by-one input
        print(f"Please enter your entropy by inputting {entropy_bits} bits (0s and 1s).")
        entropy = ""
        while len(entropy) < entropy_bits:
            next_digit = input(f"Digit {len(entropy)+1}/{entropy_bits}: Enter 0 or 1: ").strip()
            if next_digit not in ('0', '1'):
                print("Invalid input. Enter only 0 or 1.")
                continue
            entropy += next_digit
            print(f"Current length: {len(entropy)}/{entropy_bits}")
        print("Completed entry!")
        return entropy

# --- usage example ---
def main():
    print("Choose mnemonic length:")
    print("[1] 12 words (128 bits entropy)")
    print("[2] 24 words (256 bits entropy)")
    word_choice = input("Enter 1 or 2: ").strip()
    if word_choice == "1":
        entropy_bits = 128
    elif word_choice == "2":
        entropy_bits = 256
    else:
        print("Invalid choice, defaulting to 24 words (256 bits).")
        entropy_bits = 256

    print("\nChoose entropy input method:")
    print("[1] Enter your own entropy (binary string of length {})".format(entropy_bits))
    print("[2] Generate random entropy (WARNING: ONLY FOR EDUCATIONAL USE, DO NOT USE FOR STORING REAL FUNDS)")
    entropy_choice = input("Enter 1 or 2: ").strip()

    wordlist = load_wordlist('english.txt')

    if entropy_choice == "1":
        entropy_bin = get_entropy_digits(entropy_bits)
    elif entropy_choice == "2":
        entropy_bin = generate_entropy(entropy_bits)
        print("\nGenerated entropy (for learning purposes):")
        print(entropy_bin)
    else:
        print("Invalid choice.")
        return

    checksum_bin = get_checksum(entropy_bin, entropy_bits)
    full_bin = concat_entropy_and_checksum(entropy_bin, checksum_bin)
    chunks = split_into_chunks(full_bin)
    words = bits_to_words(chunks, wordlist)

    print(f"\nEntropy ({entropy_bits} bits):\n{entropy_bin}\n")
    print(f"Checksum bits:\n{checksum_bin}\n")
    print("Mnemonic Phrase:")
    print(" ".join(words))


if __name__ == "__main__":
    main()
