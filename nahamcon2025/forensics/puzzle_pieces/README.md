# Puzzle Pieces

Author: Nordgaren

Well, I accidentally put the important data into a bunch of executables.

It was fine, until my cat stepped on my keyboard and renamed them all!

Can you help me recover the important data?

Attachment: ctf_challenge_files.7z
unzip command didn't work. Used 7z to test it.

```
└─$ 7z x ctf_challenge_files.7z -pnahamcon-2025-ctf -oextracted_files

7-Zip 24.09 (x64) : Copyright (c) 1999-2024 Igor Pavlov : 2024-11-29
 64-bit locale=en_US.UTF-8 Threads:8 OPEN_MAX:1048576, ASM

Scanning the drive for archives:
1 file, 95102 bytes (93 KiB)

Extracting archive: ctf_challenge_files.7z
--
Path = ctf_challenge_files.7z
Type = 7z
Physical Size = 95102
Headers Size = 430
Method = LZMA2:1536k BCJ 7zAES
Solid = +
Blocks = 1

Everything is Ok

Files: 10
Size:       1392720
Compressed: 95102
```

Using exiftool, I inspected metadata of all .exe files.

All executables had the same timestamp in the PE header, but different file modification times at the filesystem level.

Each .exe printed a small string when executed which was a piece of the final flag.

Wrote the following ps script to reconstruct by sorting with the date of modification time.

```
$files = Get-ChildItem *.exe | Sort-Object LastWriteTime

foreach ($file in $files) {
    $output = & $file.FullName
    Write-Host -NoNewline $output
}
```

And got the flag.