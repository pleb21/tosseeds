from bip_utils import Bip39SeedGenerator,Bip39MnemonicGenerator, Bip39MnemonicValidator, Bip44, Bip84, Bip44Coins, Bip44Changes, Bip39Languages, Bip84Coins
import hashlib
import random

lang = Bip39Languages.ENGLISH

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
    print("\nChoose how you'd like to enter the toss results:")
    print("[1] Type them one by one (more secure, but slower)")
    print(f"[2] Paste the result of {entropy_bits} tosses (faster, be careful!)")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "2":
        while True:
            bits = input(f"Paste your {entropy_bits} toss result:\n").strip()
            if len(bits) == entropy_bits and all(c in '01' for c in bits):
                print("Toss result accepted.")
                return bits
            else:
                print(f"Invalid input. Please paste ONLY {entropy_bits} 0s and 1s.")
    else:
        # Default to typing one-by-one input
        print(f"Please enter toss results, {entropy_bits} 0s and 1s).")
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

'''
 def generate_receive_addresses(mnemonic, count):
    """Generate `count` Bitcoin legacy receive addresses (P2PKH) from a BIP39 mnemonic."""
    # Validate mnemonic
    validator = Bip39MnemonicValidator(mnemonic)
    # validator.SetLanguages(lang)
    if not validator.IsValid():
        raise ValueError("Invalid BIP39 mnemonic.")

    # Generate seed with explicit language arg
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()

    bip44_mst_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)
    addresses = []
    for i in range(count):
        addr_ctx = bip44_mst_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(i)
        addresses.append(addr_ctx.PublicKey().ToAddress())
    return addresses
'''
def generate_receive_addresses(mnemonic, count, passphrase=""):
    """Generate `count` Bitcoin legacy receive addresses from a BIP39 mnemonic."""

    print("\nChoose address type:")
    print("[1] Native SegWit (Bech32) - starts with 'bc1'. If you're not sure, go with this")
    print("[2] Legacy (P2PKH) - starts with '1'")
    addr_choice = input("Enter 1 or 2: ").strip()

    if passphrase:
        # generate seed with passphrase
        seed_bytes = Bip39SeedGenerator(mnemonic).Generate(passphrase)
    else:
        seed_bytes = Bip39SeedGenerator(mnemonic).Generate(passphrase)

    if addr_choice == "2":
        bip_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)
    else:
        bip_ctx = Bip84.FromSeed(seed_bytes, Bip84Coins.BITCOIN)


    addresses = []
    for i in range(count):
        addr_ctx = bip_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(i)
        addresses.append(addr_ctx.PublicKey().ToAddress())
    return addresses
    
    # Generate seed directly without validation
    # seed_bytes = Bip39SeedGenerator(mnemonic).Generate()

    # bip44_mst_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)
    # addresses = []
    # for i in range(count):
    #     addr_ctx = bip44_mst_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(i)
    #     addresses.append(addr_ctx.PublicKey().ToAddress())
    # return addresses

def addresses_prompt(mnemonic):
    print("\nWould you like to generate a Bitcoin receiving address from these seed words?")
    print("[1] Yes, generate address(es)")
    print("[2] No, exit")
    choice = input("Enter 1 or 2: ").strip()
    if choice != '1':
        print("Ok, goodbye.")
        return

    # Ask for passphrase
    print("\nWould you like to add a passphrase (BIP39 25th word)?")
    print("[1] Yes")
    print("[2] No (empty passphrase)")
    pass_choice = input("Enter 1 or 2: ").strip()
    
    if pass_choice == "1":
        passphrase = input("Enter your passphrase (visible): ").strip()
    else:
        passphrase = ""


    while True:
        how_many = input("How many receiving addresses would you like to generate (1–100)? ").strip()
        if how_many.isdigit() and 1 <= int(how_many) <= 100:
            how_many = int(how_many)
            break
        else:
            print("Please enter a number from 1 to 100.")

    try:
        addresses = generate_receive_addresses(mnemonic, how_many, passphrase)
    except Exception as e:
        print(f"Error: {e}")
        return

    print("\nYour Bitcoin receiving address(es):")
    for idx, address in enumerate(addresses, 1):
        print(f"{idx}: {address}")


# input existing mnemonic and get its receiving addresses
def input_existing_mnemonic(wordlist):
    """Prompt user to input an existing BIP39 mnemonic word by word."""
    print("\nChoose seed length:")
    print("[1] 12 words")
    print("[2] 24 words")
    word_choice = input("Enter 1 or 2: ").strip()
    
    if word_choice == "1":
        word_count = 12
    elif word_choice == "2":
        word_count = 24
    else:
        print("Invalid choice, defaulting to 12 words.")
        word_count = 12
    
    words = []
    print(f"\nEnter your {word_count}-word mnemonic phrase:")
    
    for i in range(word_count):
        while True:
            word = input(f"Word {i+1}/{word_count}: ").strip().lower()
            if word in wordlist:
                words.append(word)
                break
            else:
                print(f"'{word}' is not in the BIP39 wordlist. Please try again.")
    
    mnemonic = " ".join(words)

    # Validate by attempting seed generation
    try:
        Bip39SeedGenerator(mnemonic).Generate()
        print("\n✓ Valid mnemonic!")
        return mnemonic
    except Exception:
        print("\n✗ Invalid mnemonic.")
        print("Would you like to try again? [y/n]")
        if input().strip().lower() == 'y':
            return input_existing_mnemonic(wordlist)
        return None

# --- usage example ---
def main():
    wordlist = load_wordlist('english.txt')

    print("=" * 60)
    print("BIP39 Mnemonic & Bitcoin Address Generator")
    print("=" * 60)
    print("This tool allows you to:")
    print("  • CREATE seed from coin tosses (manual entropy)")
    print("  • GENERATE a new seed using code (educational only)")
    print("  • ENTER an existing seed to get its addresses")
    print("  • Generate Bitcoin RECEIVING ADDRESSES for the seed(Legacy or SegWit)")
    print("\nALL code can be run on an offline computer")
    print()
    print("⚠️  WARNING: Only use random generation for learning purposes.")
    print("    For real funds, use proper entropy sources like coin flips.")
    print("=" * 60)
    print()

    print("Choose mode:")
    print("[1] Create NEW seed")
    print("[2] Enter EXISTING seed")
    mode_choice = input("Enter 1 or 2: ").strip()
    
    if mode_choice == "2":
        # New flow: input existing mnemonic
        mnemonic = input_existing_mnemonic(wordlist)
        if mnemonic is None:
            print("Exiting.")
            return
        print(f"\nYour seed:\n{mnemonic}")
        addresses_prompt(mnemonic)
        return

    print("\nChoose seed length:")
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

    print("\nChoose how the seed is created:")
    print("[1] Coin tosses\nYou would need to toss a coin, enter either 0 or 1 and do it {} times. This is the right way to ensure a truly random seed is generated.".format(entropy_bits))
    print("\n[2] Generate a random seed (WARNING: ONLY FOR EDUCATIONAL USE, DO NOT USE FOR STORING REAL FUNDS)")
    entropy_choice = input("Enter 1 or 2: ").strip()

    

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
    mnemonic = (" ".join(words))
    print(f"\nEntropy ({entropy_bits} bits):\n{entropy_bin}\n")
    print(f"Checksum bits:\n{checksum_bin}\n")
    print(f"Seed words:\n{mnemonic}")
    print("\n PLEASE WRITE & STORE THESE WORDS CAREFULLY IN THE EXACT ORDER. These words will NEVER be displayed again.")
    # print(" ".join(words))

    addresses_prompt(mnemonic)



if __name__ == "__main__":
    main()
