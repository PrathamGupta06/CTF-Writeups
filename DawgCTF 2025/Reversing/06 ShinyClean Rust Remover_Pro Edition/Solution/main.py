import sys

lut_hex = """
9f d2 d6 a8 99 76 b8 75 e2 0e 50 67 c9 3a a0 b5
15 ee 59 be 7d a3 fb 51 df 7c d9 0d e7 2d ad 28
ed dc 3d 14 13 79 af 27 d1 d5 a1 f9 37 c0 ef 25
38 77 ff 1b 40 60 8f 45 6f 08 6d d3 35 3f b4 2f
d7 34 5f 05 bb 11 3e 84 5b 00 f5 29 36 2c 63 2b
70 68 02 ae c4 95 10 89 b0 2e 55 cc bc 80 a6 f3
d8 5a 62 61 9a a5 fe 3c b2 7e bf a7 eb 41 7a fa
53 47 dd 6b 54 65 9d 0b 73 94 81 1d 4c ac 46 de
43 9c fd 7f 6a 7b 07 01 f7 e5 b3 cd 1f c7 58 e6
4d 31 4a d0 98 93 20 c5 1e 6c 8c 09 78 bd 03 23
82 db 12 16 96 c8 ce f4 e0 a4 04 ca 49 87 c2 32
6e f1 39 1c 85 5e 92 f8 ab ea 8d c1 86 17 8a b1
f2 4f fc e1 cb b6 42 ba a9 88 66 4e 18 f6 64 aa
2a 8b f0 a2 ec 97 5c e3 cf 91 0c 1a 30 5d 69 56
e4 9b 0f 90 c6 72 48 06 33 9e 0a 83 8e 52 19 e8
44 da 26 d4 3b 4b 74 24 22 b7 c3 93 e9 b9 96 71
57
"""
lut = bytes.fromhex(lut_hex.replace('\n', ''))

target = bytes([
    0xEA, 0xD9, 0x31, 0x22, 0xD3, 0xE6, 0x97, 0x70, 0x16, 0xA2,
    0xA8, 0x1B, 0x61, 0xFC, 0x76, 0x68, 0x7B, 0xAB, 0xB8, 0x27,
    0x96
])

# Build a reverse LUT for quick lookup: reverse_lut[target_byte] = accumulator_index
reverse_lut = {}
for i in range(len(lut)):
    if lut[i] in reverse_lut:
         # This would indicate a problem if multiple accumulators map to the same target
         print(f"Warning: Duplicate LUT value {lut[i]:02x} found at index {i:02x} (already seen at {reverse_lut[lut[i]]:02x})", file=sys.stderr)
    reverse_lut[lut[i]] = i

acc_values = []
prev_acc = 0x75

# Find the sequence of accumulator values
for i in range(len(target)):
    t_byte = target[i]
    if t_byte not in reverse_lut:
        print(f"Error: Target byte {t_byte:02x} at index {i} not found in LUT!", file=sys.stderr)
        exit(1)
    current_acc = reverse_lut[t_byte]
    acc_values.append(current_acc)

# Calculate the input bytes
input_bytes = []
prev_acc = 0x75
for current_acc in acc_values:
    # Calculate B_in = (current_acc - prev_acc) mod 256
    input_byte = (current_acc - prev_acc) & 0xFF # Using bitwise AND for % 256
    input_bytes.append(input_byte)
    prev_acc = current_acc # Update for the next iteration

# Print the result
flag = bytes(input_bytes)
print(f"Target Bytes: {target.hex()}")
print(f"Accumulator Sequence: {[hex(a) for a in acc_values]}")
print(f"Calculated Input Bytes: {flag.hex()}")
try:
    print(f"Resulting Flag: {flag.decode('ascii')}")
except UnicodeDecodeError:
    print("Resulting bytes are not valid ASCII.")