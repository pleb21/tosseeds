a python utility to create seed words from your tosses, i.e. To ensure absolute randomness, toss a coin 128/256 times and generate a 12/24 word random seed.

Toss a coin, each heads is a 0 and tails a 1. Do that 128 times (or 256 times). Get a 12 word (or 24 word) seed.

Clone the repo. It should have the english.txt in the same folder as the .py script. (or your choice of bip words at https://github.com/bitcoin/bips/tree/master/bip-0039 - if you do so, either rename that file to english.txt OR replace `english.txt` with your wordlist file name in .py file)

DO NOT EVER, FOR ANY REASON, NO MATTER HOW MUCH THE TEMPTATION, ENTER YOUR SEED OR THE RESULT OF COIN TOSSES IN AN ONLINE MACHINE. Yeah, even for this script, you should clone this, go offline, use the script, note the words, delete the cloned repo.
