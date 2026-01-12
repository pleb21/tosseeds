# TODO: Future Improvements

## UX Enhancements

### 1. Consistent Terminology
- [ done ] Replace all "entropy/bits" language with "coin flips/tosses" in mode 1
- [ done ] Use beginner-friendly terms throughout (avoid jargon where possible)

### 2. Visual Feedback for Long Inputs
- [ done ] Add progress bar for coin flip entry (e.g., `████████░░░░░░░░ 50/128 tosses`)
- [ done ] Show milestone messages every 10-20 tosses ("50 tosses done... keep going!")
- [ done ] Consider adding estimated time remaining

### 3. Clearer Warnings
- [ ] Make random generation warning more prominent with ASCII borders
- [ ] Add explicit "⚠️ CRITICAL WARNING ⚠️" header
- [ ] Emphasize: "Use ONLY for testing/learning. For real funds: Use coin flips"

### 4. Word Input Confirmation
- [ ] Show complete mnemonic back to user before validation
- [ ] Add "Proceed? [y/n]" confirmation prompt
- [ ] Allow user to go back and fix mistakes

### 5. Better Success Messages
- [ ] After mnemonic generation: "✓ Mnemonic created! Write this down on paper (never store digitally)"
- [ ] After address generation: "✓ Addresses generated! You can receive Bitcoin at these addresses"
- [ ] Add security reminders at key moments

### 6. Input Flexibility
- [ ] Allow "H/T" or "h/t" for heads/tails (not just 0/1)
- [ ] Allow typing "heads/tails" in full
- [ ] Add input aliases for better accessibility

### 7. Exit Options
- [ ] Add "[q] Quit" option at every prompt
- [ ] Allow Ctrl+C graceful exit with goodbye message
- [ ] Confirm exit if in middle of sensitive operation

## Features (Future Consideration)
- [ ] Multi-signature address support
- [ ] Taproot (P2TR) address generation
- [ ] QR code generation for addresses
- [ ] Export addresses to file (with user consent)
- [ ] BIP85 child mnemonic derivation
- [ ] Testnet address generation option
- [ ] Dice roll entropy (base-6 instead of binary)

## Security & Code Quality
- [ ] Add comprehensive error handling
- [ ] Add unit tests for core functions
- [ ] Code cleanup and documentation
- [ ] Security audit checklist
- [ ] Add rate limiting for brute force protection (if networked)