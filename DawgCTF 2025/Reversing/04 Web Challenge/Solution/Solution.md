# DawgCTF - """Web Challenge""" (Reversing)

We are given a single file, `webassembly.wasm`. The name "Web Challenge" seems a bit ironic given it's a WASM binary, but let's dive in.

## Initial Analysis

First things first, let's check the file type and look for any obvious clues:

```bash
$ file webassembly.wasm 
webassembly.wasm: WebAssembly (wasm) binary module version 0x1 (MVP)

$ strings webassembly.wasm 
wasi_snapshot_preview1
fd_write
_emscripten_memcpy_js
emscripten_resize_heap
memory
__wasm_call_ctors
main
# ... other emscripten/wasi functions ...
fflush
# ... more emscripten stack functions ...
dynCall_jiji
# ... lots of short, cryptic strings ...
jrg/!7%[3=F,|2uAmv5\Y)X~]S_wD'*E"GOehz>l@W8q`4cCV;fQ6&0^R+toB#(dp1K$bHN:<PLnUTyZi }?ka.9IJ-{Mxs
# ... hex formatting strings ...
(null)
SUFFAH WEBDEVS!!!!!!!!
0123456789ABCDEF
```

Okay, several things stand out:

1.  **It's definitely WebAssembly.**
2.  **Lots of `emscripten_` functions:** This heavily suggests the original code was C or C++ compiled to WASM using the Emscripten toolchain. This often means standard C library functions might be included.
3.  **`wasi_snapshot_preview1` and `fd_write`:** It uses the WebAssembly System Interface, likely to print output to the console.
4.  **`main` function:** The standard entry point.
5.  **`jrg/...` string:** This long, jumbled string looks highly suspicious. It could be a key, an alphabet, or data used in some transformation. This is probably important.
6.  **`SUFFAH WEBDEVS!!!!!!!!`:** A message, maybe printed on success or just flavor text.

## Static Analysis with Ghidra

Let's open `webassembly.wasm` in Ghidra and see what the code does.

Looking at the exported functions, we find `main`. Decompiling `main`:

```c
undefined4 export::main(undefined4 param1, undefined4 param2) {
  undefined4 uVar1;
  
  uVar1 = unnamed_function_4(); // Calls another function
  return uVar1; // Returns its result (likely 0 for success)
}
```

The `main` function is trivial; it just calls `unnamed_function_4`. Let's look at that one.

Decompiling `unnamed_function_4`:

```c
undefined4 unnamed_function_4(void) {
  int iVar1; // Pointer to allocated buffer
  int local_c; // Loop counter
  
  // Call unnamed_function_46 to allocate memory
  iVar1 = unnamed_function_46(0x29); // Request 41 bytes
  
  // Null-terminate the buffer at index 0x29 (41)
  *(undefined1 *)(iVar1 + 0x29) = 0; 
  
  // The core logic loop (runs 0x28 = 40 times)
  for (local_c = 0; local_c < 0x28; local_c = local_c + 1) {
    // Read a byte from address 0x10060 + loop_counter
    byte index_byte = *(byte *)(local_c + 0x10060); 
    
    // Use index_byte to lookup a value from address 0x10000 + index_byte
    byte value_byte = *(undefined1 *)(index_byte + 0x10000);
    
    // Write the looked-up value into the buffer
    *(undefined1 *)(iVar1 + local_c) = value_byte;
  }
  
  // Print the "SUFFAH WEBDEVS" message (likely using fd_write via unnamed_function_6)
  unnamed_function_6(s_SUFFAH_WEBDEVS!!!!!!!!_ram_000100be, 0); 
  
  return 0; // Return success
}
```

Okay, now we're getting somewhere!

*   `unnamed_function_46` looks incredibly complex when decompiled. Given its usage (taking a size and returning a pointer) and the intricate memory management patterns, it's almost certainly the `malloc` implementation bundled by Emscripten. It allocates 41 bytes.
*   The core of the function is the `for` loop. It iterates 40 times. In each iteration:
    1.  It reads an index byte from a fixed memory location (`0x10060 + i`). Let's call this the **Index Array (IDX)**.
    2.  It uses that index byte to read *another* byte from a different fixed memory location (`0x10000 + index_byte`). This looks like a **Lookup Table (LUT)**.
    3.  It writes the byte fetched from the LUT into the allocated buffer (`iVar1`).
*   After the loop finishes constructing the 40-byte result in the buffer, it prints the "SUFFAH WEBDEVS!!!!!!!!" message. Crucially, it *doesn't* print the buffer it just constructed! The flag must be the content of this buffer.

## Data Extraction

We need the data for the LUT and the IDX array. Let's find them in Ghidra's memory view:

1.  **LUT:** Starts at `0x10000`. Looking there, we find the suspicious string from `strings`:
    ```
    jrg/!7%[3=F,|2uAmv5\Y)X~]S_wD'*E"GOehz>l@W8q`4cCV;fQ6&0^R+toB#(dp1K$bHN:<PLnUTyZi }?ka.9IJ-{Mxs
    ```

2.  **IDX:** Starts at `0x10060`. We need the first `0x28` (40) bytes:
    ```
    Offset 0x10060: 1c 55 1b 02 2f 4d 0a 5b 46 22 1a 08 19 2f 2d 49 
    Offset 0x10070: 08 1a 0a 38 22 5c 1a 2d 19 19 08 5c 3c 4a 14 1a 
    Offset 0x10080: 29 08 3c 1c 08 30 19 52 
    ```

## Flag Recovery

Now we just need to perform the lookup operation described by the code: `result[i] = LUT[ IDX[i] ]`.

Let's map the first few bytes:
*   `IDX[0] = 0x1c` -> `LUT[0x1c]` (the character at offset 28 in the LUT string) = `'D'`
*   `IDX[1] = 0x55` -> `LUT[0x55]` (the character at offset 85) = `'a'`
*   `IDX[2] = 0x1b` -> `LUT[0x1b]` (the character at offset 27) = `'w'`
*   `IDX[3] = 0x02` -> `LUT[0x02]` (the character at offset 2) = `'g'`
*   ... and so on for all 40 bytes.

We can write a simple script or do this manually. Performing the lookup for all 40 index bytes yields:

```
DawgCTF{NO_3SC4P3_FROM_4SS3MBLY_W3BD3VS}
```

## Conclusion

The challenge involved reversing a C/C++ program compiled to WASM using Emscripten. The core logic was hidden inside an unnamed function and involved constructing the flag string character by character using a lookup table (LUT) indexed by values from another data array (IDX). Extracting these two data arrays and simulating the lookup process revealed the flag. The "SUFFAH WEBDEVS" message was just a distraction.
```
**Flag:** `DawgCTF{NO_3SC4P3_FROM_4SS3MBLY_W3BD3VS}`
``` 