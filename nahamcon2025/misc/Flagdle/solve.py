import requests
import sys

# Define the emoji feedback symbols
EMOJI_GREEN = "\U0001f7e9"  # 🟩

# Allowed characters (hexadecimal digits)
alphabet = "0123456789abcdef"

# Configuration
target_url = "http://challenge.nahamcon.com:31170/guess"


def make_guess(guess_str):
    """Send a guess and return the emoji feedback string."""
    payload = {"guess": f"flag{{{guess_str}}}"}
    resp = requests.post(target_url, json=payload)
    if resp.status_code != 200:
        print(f"Error: HTTP {resp.status_code} - {resp.text}")
        sys.exit(1)
    # Parse JSON response and extract the 'result' field containing emojis
    try:
        data = resp.json()
        feedback = data.get("result", "")
    except ValueError:
        print(f"Unexpected response format: {resp.text}")
        sys.exit(1)
    return feedback


def increment_char(c):
    """Return the next character in the alphabet (no wrap-around)."""
    idx = alphabet.index(c)
    if idx + 1 < len(alphabet):
        return alphabet[idx + 1]
    else:
        # Already at 'f', stay
        return c


def brute_force_flag():
    # Initialize guess characters (32 zeros)
    guess_chars = ["0"] * 32
    round_num = 1

    while True:
        guess_str = "".join(guess_chars)
        feedback = make_guess(guess_str)
        print(f"Round {round_num}: flag{{{guess_str}}} -> {feedback}")

        # Check if fully solved
        if feedback == EMOJI_GREEN * 32:
            print(f"Solved flag: flag{{{guess_str}}}")
            break

        # Increment non-green positions
        for i, fb in enumerate(feedback):
            if fb != EMOJI_GREEN:
                guess_chars[i] = increment_char(guess_chars[i])
        round_num += 1


if __name__ == "__main__":
    brute_force_flag()
