# DawgCTF - ShinyClean_Budget (Reversing)

### Initial Analysis

Loading the binary into Ghidra, we first examine the `main` function:

```c
void main(int param_1,undefined8 param_2)

{
  std::rt::lang_start(shinyclean::main,(long)param_1,param_2,0);
  return;
}
```

This is typical for a Rust binary. The C `main` function simply calls the Rust runtime entry point (`std::rt::lang_start`), which in turn eventually calls the actual Rust main function, identified here as `shinyclean::main`. Our primary target for analysis is therefore `shinyclean::main`.

### Analyzing `shinyclean::main`

The decompiled code for `shinyclean::main` reveals the core logic:

```c
/* shinyclean::main */

void __rustcall shinyclean::main(void)

{
  int iVar1;
  ulong uVar2;
  byte local_de [23]; // Buffer for decoded result (flag?)
  byte local_c7 [23]; // Buffer with hardcoded encoded data
  ulong local_b0;    // Loop counter/index
  // ... other local variables for printing ...

  // Initialize result buffer to zeros
  memset(local_de,0,0x17);

  // Hardcoded encoded data (23 bytes)
  local_c7[0] = 0x7b;
  local_c7[1] = 0x5e;
  local_c7[2] = 0x48;
  // ... (rest of the bytes omitted for brevity) ...
  local_c7[0x16] = 0x42;

  local_b0 = 0; // Initialize loop counter

  // Decoding loop
  while( true ) {
    if (0x16 < local_b0) { // Bounds check
      core::panicking::panic_bounds_check(local_b0,0x17,&PTR_DAT_00154578);
    }
    if (0x16 < local_b0) { // Bounds check
      core::panicking::panic_bounds_check(local_b0,0x17,&PTR_DAT_00154590);
    }

    // ---> The core decoding operation <---
    local_de[local_b0] = local_c7[local_b0] ^ 0x3f;

    uVar2 = local_b0 + 1;
    if (0xfffffffffffffffe < local_b0) break; // Check for overflow before increment (unlikely path)
    local_b0 = uVar2;
    if (uVar2 == 0x17) { // Loop finishes after 23 iterations (0 to 22)
LAB_00107c83:
      // Get Process ID
      iVar1 = std::process::id();

      // Check if PID matches a specific value
      if (iVar1 == 0x1c1e8b2) { // 0x1c1e8b2 = 29485746 decimal
        // If PID matches, print the decoded buffer 'local_de'
        // ... setup for printing local_de ...
        std::io::stdio::_print(local_a8);
      }
      else {
        // If PID doesn't match, print a constant string (error/failure message)
        // ... setup for printing constant message ...
        std::io::stdio::_print(local_58);
      }
      return;
    }
  }
  // Error handling for loop counter overflow
  core::panicking::panic_const::panic_const_add_overflow(&PTR_DAT_001545a8);
  goto LAB_00107c83;
}
```

**Key Observations:**

1.  **Encoded Data:** A 23-byte array (`local_c7`) is hardcoded with specific values.
2.  **Decoding Algorithm:** A loop iterates 23 times, taking each byte from `local_c7`, XORing it with the constant `0x3f`, and storing the result in `local_de`. This is a simple single-byte XOR cipher.
3.  **PID Check:** After decoding, the program checks if its Process ID (PID) is equal to `0x1c1e8b2`. The decoded flag is only printed if the PID matches. This is likely an anti-debugging measure or an environment check, but we don't need to bypass it since we can decode the flag statically.

## Decoding the Flag

We can replicate the XOR operation found in the code to recover the flag. The encoded bytes are in `local_c7`, and the key is `0x3f`.

We can use a simple script (e.g., Python) or manually XOR each byte:

```python
encoded_bytes = [
    0x7b, 0x5e, 0x48, 0x58, 0x7c, 0x6b, 0x79, 0x44, 0x79, 0x6d, 0x0c,
    0x0c, 0x60, 0x7c, 0x0b, 0x6d, 0x60, 0x68, 0x0b, 0x0a, 0x77, 0x1e,
    0x42
]

key = 0x3f
decoded_flag = ""

for byte in encoded_bytes:
  decoded_flag += chr(byte ^ key)

print(decoded_flag)
```

## Flag

```
DawgCTF{FR33_C4R_W45H!}
```

```