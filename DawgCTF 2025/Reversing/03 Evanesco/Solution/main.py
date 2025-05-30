import struct

# Raw bytes loaded onto stack (little-endian qwords concatenated)
stack_data_raw = bytes([
    0xF3, 0xA0, 0x80, 0x81, 0xF3, 0xA0, 0x81, 0x84, # QWord 1
    0xF3, 0xA0, 0x81, 0xA1, 0xF3, 0xA0, 0x81, 0xB7, # QWord 2
    0xF3, 0xA0, 0x81, 0xA7, 0xF3, 0xA0, 0x81, 0x83, # QWord 3
    0xF3, 0xA0, 0x81, 0x94, 0xF3, 0xA0, 0x81, 0x86, # QWord 4
    0xF3, 0xA0, 0x81, 0xBB, 0xF3, 0xA0, 0x81, 0xB5, # QWord 5
    0xF3, 0xA0, 0x81, 0x9F, 0xF3, 0xA0, 0x81, 0xA3, # QWord 6
    0xF3, 0xA0, 0x81, 0xA1, 0xF3, 0xA0, 0x81, 0xAE, # QWord 7
    0xF3, 0xA0, 0x81, 0x9F, 0xF3, 0xA0, 0x81, 0xB4, # QWord 8
    0xF3, 0xA0, 0x81, 0xA1, 0xF3, 0xA0, 0x81, 0xA7, # QWord 9
    0xF3, 0xA0, 0x81, 0x9F, 0xF3, 0xA0, 0x81, 0xA2, # QWord 10
    0xF3, 0xA0, 0x81, 0xB5, 0xF3, 0xA0, 0x81, 0xB4, # QWord 11
    0xF3, 0xA0, 0x81, 0x9F, 0xF3, 0xA0, 0x81, 0xB5, # QWord 12
    0xF3, 0xA0, 0x81, 0x9F, 0xF3, 0xA0, 0x81, 0xA3, # QWord 13
    0xF3, 0xA0, 0x81, 0xA1, 0xF3, 0xA0, 0x81, 0xAE, # QWord 14
    0xF3, 0xA0, 0x81, 0xB4, 0xF3, 0xA0, 0x81, 0x9F, # QWord 15
    0xF3, 0xA0, 0x81, 0xA8, 0xF3, 0xA0, 0x81, 0xA9, # QWord 16
    0xF3, 0xA0, 0x81, 0xA4, 0xF3, 0xA0, 0x81, 0xA5, # QWord 17
    0xF3, 0xA0, 0x81, 0xBD, 0xF3, 0xA0, 0x81, 0xBF, # QWord 18
])

# Subtract 0x80 from each byte
subtracted_data = bytes([(b - 0x80) & 0xFF for b in stack_data_raw])

# Extract every 4th byte (starting from index 3, since indices are 0, 1, 2, 3, 4, ...)
derived_sequence = subtracted_data[3::4]

print(f"Raw stack data hex: {stack_data_raw.hex()}")
print(f"Subtracted data hex: {subtracted_data.hex()}")
print(f"Derived sequence hex: {derived_sequence.hex()}")

# Try the +0x40 transformation again
final_flag_guess = bytes([(b + 0x40) & 0xFF for b in derived_sequence])
print(f"Final flag guess (+0x40): {final_flag_guess.decode('ascii', errors='replace')}")