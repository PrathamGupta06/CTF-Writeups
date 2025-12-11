# DawgCTF - Invisible (Reversing)

This challenge involved a 64-bit Linux ELF binary named `invisible`. The goal, as usual, was to find the flag.

## Initial Analysis

First, let's check the file type:

```bash
$ file invisible
invisible: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=b4977636d7325a473516893f896d8fc1677af9a9, for GNU/Linux 3.2.0, not stripped
```

It's a standard dynamically linked 64-bit ELF, and importantly, *not stripped*, which makes reversing easier.

Let's run it to see what it does:

```bash
$ ./invisible
Oops I spilled my invisibility potion all over the flag!
Can you find the flag for me?
s���s� s�!s�'s� s� s�{s�us�_s�cs�as�ns�_s�ts�as�gs�_s�bs�us�ts�_s�us�_s�cs�as�ns�ts�_s�hs�is�ds�es�}s�
I hope you can find it!
```

Okay, it prints some introductory text, then a line of complete garbage (mostly non-printable characters, but with some 's' characters visible), and then a concluding message. The name "invisible" and the garbled output strongly suggest the flag is hidden within that mess.

## Static Analysis with Ghidra

Loading the binary into Ghidra and navigating to the `main` function (`0x00101169`), we can see the program's structure:

1.  Standard function setup (stack frame, stack canary).
2.  Uses `puts` to print the "Oops..." and "Can you find..." messages we saw.
3.  **Crucially**, there's a large block of code that initializes local variables on the stack. It repeatedly uses `MOV RAX, <immediate_64bit_value>` and `MOV RDX, <immediate_64bit_value>`, followed by storing these values onto the stack using `MOV [RBP + offset], REG`. This happens 18 times, loading 18 * 8 = 144 bytes of specific data.

    ```assembly
    // Example instructions loading data onto the stack
    00101187 48 b8 f3        MOV        RAX,-0x7b7e5f0c7e7f5f0d
             a0 80 81
             f3 a0 81 84
    00101191 48 ba f3        MOV        RDX,-0x487e5f0c5e7e5f0d
             a0 81 a1
             f3 a0 81 b7
    0010119b 48 89 85        MOV        qword ptr [RBP + local_a8],RAX // RBP-0xa0
             60 ff ff ff
    001011a2 48 89 95        MOV        qword ptr [RBP + local_a0],RDX // RBP-0x98
             68 ff ff ff
    // ... this pattern continues down to RBP-0x18 (local_20)
    ```

4.  Immediately after loading this data, it null-terminates it:
    ```assembly
    0010128f c6 45 f0 00     MOV        byte ptr [RBP + local_18],0x0 // RBP-0x10
    ```
5.  Then, it takes the address of the start of this data (`local_a8` at `RBP-0xA0`), puts it in `RDI`, and calls `puts`:
    ```assembly
    001012b1 48 8d 85        LEA        RAX=>local_a8,[RBP + -0xa0]
             60 ff ff ff
    001012b8 48 89 c7        MOV        RDI,RAX
    001012bb e8 a0 fd        CALL       <EXTERNAL>::puts
             ff ff
    ```
    This confirms that the garbled output we saw when running the program *is* this specific 144-byte chunk of data loaded onto the stack. The flag must be encoded within these bytes!

6.  Finally, it prints the "I hope..." message and exits.

## Extracting and Decoding the Flag

The core task is to decode the 144 bytes loaded onto the stack starting at `RBP-0xA0`. Let's extract the raw byte sequence (remembering x86 is little-endian):

```
f3 a0 80 81 f3 a0 81 84 f3 a0 81 a1 f3 a0 81 b7
f3 a0 81 a7 f3 a0 81 83 f3 a0 81 94 f3 a0 81 86
f3 a0 81 bb f3 a0 81 b5 f3 a0 81 9f f3 a0 81 a3
f3 a0 81 a1 f3 a0 81 ae f3 a0 81 9f f3 a0 81 b4
f3 a0 81 a1 f3 a0 81 a7 f3 a0 81 9f f3 a0 81 a2
f3 a0 81 b5 f3 a0 81 b4 f3 a0 81 9f f3 a0 81 b5
f3 a0 81 9f f3 a0 81 a3 f3 a0 81 a1 f3 a0 81 ae
f3 a0 81 b4 f3 a0 81 9f f3 a0 81 a8 f3 a0 81 a9
f3 a0 81 a4 f3 a0 81 a5 f3 a0 81 bd f3 a0 81 bf
```

This doesn't look like ASCII. Let's try some simple transformations. Observing the repeated `f3 a0 81 ...` pattern, maybe a simple arithmetic operation will reveal something. Let's try subtracting `0x80` from each byte:

```
73 20 00 01 73 20 01 04 73 20 01 21 73 20 01 37
73 20 01 27 73 20 01 03 73 20 01 14 73 20 01 06
73 20 01 3b 73 20 01 35 73 20 01 1f 73 20 01 23
73 20 01 21 73 20 01 2e 73 20 01 1f 73 20 01 34
73 20 01 21 73 20 01 27 73 20 01 1f 73 20 01 22
73 20 01 35 73 20 01 34 73 20 01 1f 73 20 01 35
73 20 01 1f 73 20 01 23 73 20 01 21 73 20 01 2e
73 20 01 34 73 20 01 1f 73 20 01 28 73 20 01 29
73 20 01 24 73 20 01 25 73 20 01 3d 73 20 01 3f
```

Aha! This looks much more structured. We see a repeating pattern: `73 20 <byte1> <byte2>`, which translates to `s <space> <byte1> <byte2>`. The 's' characters we glimpsed in the garbled output make sense now. It seems the actual flag characters might be the `<byte2>` values, interleaved with this other data.

Let's extract every 4th byte from this transformed sequence (starting at index 3):

```
01 04 21 37 27 03 14 06 3b 35 1f 23 21 2e 1f 34
21 27 1f 22 35 34 1f 35 1f 23 21 2e 34 1f 28 29
24 25 3d 3f
```
This gives us a 36-byte sequence. This must be the final encoded flag. Let's try another simple transformation. Adding `0x40` to each byte often comes up in CTFs:

```python
raw_bytes = bytes.fromhex(
    "f3a08081f3a08184f3a081a1f3a081b7"
    "f3a081a7f3a08183f3a08194f3a08186"
    "f3a081bbf3a081b5f3a0819ff3a081a3"
    "f3a081a1f3a081aef3a0819ff3a081b4"
    "f3a081a1f3a081a7f3a0819ff3a081a2"
    "f3a081b5f3a081b4f3a0819ff3a081b5"
    "f3a0819ff3a081a3f3a081a1f3a081ae"
    "f3a081b4f3a0819ff3a081a8f3a081a9"
    "f3a081a4f3a081a5f3a081bdf3a081bf"
)

subtracted_bytes = bytes([(b - 0x80) & 0xFF for b in raw_bytes])
derived_sequence = subtracted_bytes[3::4] # Extract every 4th byte

# Add 0x40 to each byte in the derived sequence
final_flag_bytes = bytes([(b + 0x40) & 0xFF for b in derived_sequence])

print(final_flag_bytes.decode('ascii', errors='ignore'))
```

Running this script yields:

```
ADawgCTF{u_can_tag_but_u_cant_hide}
```

(The script ignores the very last byte `0x3f + 0x40 = 0x7f`, which is DEL and not part of the flag string).

This looks like a valid flag format!

## The Flag

The flag is obtained by extracting the 144 bytes loaded onto the stack in `main`, subtracting `0x80` from each byte, taking every 4th byte of the result, and finally adding `0x40` to each of those bytes.

```
ADawgCTF{u_can_tag_but_u_cant_hide}
```