import string
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

url = "http://challenge.nahamcon.com:31384/api/update.php"
headers = {"Content-Type": "application/json"}


def test_char(ch, session):
    payload = {"control": f"test-{ch}", "value": 1}
    try:
        r = session.post(url, json=payload, headers=headers, timeout=3)
        if r.status_code == 200 and "error" not in r.json():
            return ch
    except Exception:
        pass
    return None


def main():
    allowed = []
    # Use a single Session for connection pooling
    with requests.Session() as session:
        with ThreadPoolExecutor(max_workers=20) as pool:
            # submit all printable chars
            future_to_char = {
                pool.submit(test_char, ch, session): ch for ch in string.printable
            }
            for future in as_completed(future_to_char):
                res = future.result()
                if res is not None:
                    allowed.append(res)

    print("Allowed characters in `control`:", "".join(sorted(allowed)))


if __name__ == "__main__":
    main()
