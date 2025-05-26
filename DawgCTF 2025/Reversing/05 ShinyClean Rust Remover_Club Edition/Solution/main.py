import hashlib
import struct
import sys
import time # To estimate time

# Initial 25 bytes from disassembly
initial_data = bytes.fromhex("cf091eb3c83c2fafbf24258bd93d5ce3d426598bc85c3bf5f6")

# Target SHA256 hash string
target_hash = "61cd3bdb1272953e049b0185b12703f8f6454c7df95c38cc042423c13e05ee51"

# Define the full u32 range
MAX_U32 = 2**32 # range goes up to MAX_U32 - 1
REPORT_INTERVAL = 1_000_000 # Report progress every 100 million checks

print(f"[*] Starting full u32 brute-force (0 to {MAX_U32 - 1})...")
print(f"[*] This may take a significant amount of time.")
print(f"[*] Target Hash: {target_hash}")
print(f"[*] Initial Data: {initial_data.hex()}")
print("-" * 50)

start_time = time.time()
last_report_time = start_time
last_report_i = 0

# Iterate through all possible u32 inputs
for i in range(MAX_U32):
    # Convert u32 integer to 4 little-endian bytes
    # Use '<I' for little-endian unsigned int
    input_bytes = struct.pack('<I', i)

    # Perform the XOR modification
    modified_data = bytearray(initial_data) # Make a mutable copy
    for j in range(25):
        xor_byte = input_bytes[j % 4]
        modified_data[j] = initial_data[j] ^ xor_byte

    # Calculate SHA256 of the modified data
    calculated_hash = hashlib.sha256(modified_data).hexdigest()

    # Check against the target
    if calculated_hash == target_hash:
        end_time = time.time()
        print(f"\n" + "="*50)
        print(f"[+] SUCCESS! Match found.")
        print(f"[*] Found matching input integer: {i}")
        print(f"[*] Corresponding input bytes (little-endian): {input_bytes.hex()}")
        print(f"[*] Final modified data (potential flag bytes): {modified_data.hex()}")
        try:
            # Try decoding the flag assuming it's UTF-8
            flag = modified_data.decode('utf-8')
            print(f"[*] Decoded Flag: {flag}")
        except UnicodeDecodeError:
            print("[!] Could not decode final data as UTF-8, but the bytes are above.")
        print(f"[*] Time taken: {end_time - start_time:.2f} seconds")
        print(f"\n>>> Enter the integer '{i}' into the program <<<")
        print("="*50)
        sys.exit(0) # Exit after finding the solution

    # Progress indicator - Check if it's time to report
    if (i + 1) % REPORT_INTERVAL == 0:
        current_time = time.time()
        elapsed_since_last = current_time - last_report_time
        # Avoid division by zero if the interval is processed extremely fast
        rate = (i - last_report_i + 1) / elapsed_since_last if elapsed_since_last > 0 else float('inf')
        total_elapsed = current_time - start_time
        # --- Calculate Percentage Completion ---
        progress_percent = ((i + 1) / MAX_U32) * 100
        # --- Estimate Remaining Time ---
        estimated_total_time = total_elapsed / (progress_percent / 100) if progress_percent > 0 else float('inf')
        estimated_remaining = estimated_total_time - total_elapsed if estimated_total_time != float('inf') else float('inf')

        # --- Print Progress Report ---
        print(f"[*] Checked up to {i} ({progress_percent:.4f}%) - Rate: {rate:,.0f} keys/sec - Elapsed: {total_elapsed:.1f}s - Est. Remaining: {estimated_remaining:.1f}s")

        # Update tracking variables for the next report
        last_report_time = current_time
        last_report_i = i # Use i here, it will be i+1 on the next iteration start


# Final check if the loop completes without finding the hash
end_time = time.time()
# Check if the last value (MAX_U32 - 1) was the key, otherwise it would have exited.
if i == MAX_U32 - 1:
    print("\n" + "-"*50)
    print(f"[-] Brute-force finished checking all {MAX_U32} possibilities without finding a match.")
    print(f"[*] Total time taken: {end_time - start_time:.2f} seconds")
    print("[-] There might be an issue with the assumptions (e.g., endianness, initial data interpretation) or the target hash.")
    print("-" * 50)
    
    
"""
    
    ==================================================
[+] SUCCESS! Match found.
[*] Found matching input integer: 3563677835
[*] Corresponding input bytes (little-endian): 8b6869d4
[*] Final modified data (potential flag bytes): 446177674354467b344c4c5f525535375f4e305f433452217d
[*] Decoded Flag: DawgCTF{4LL_RU57_N0_C4R!}
[*] Time taken: 10175.39 seconds

>>> Enter the integer '3563677835' into the program <<<
==================================================

"""