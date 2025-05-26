# The Martian

Author: @John Hammond

Wow, this file looks like it's from outta this world!

challenge.martian was attached

```
└─$ binwalk -e challenge.martian 

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
52            0x34            bzip2 compressed data, block size = 900k
12511         0x30DF          bzip2 compressed data, block size = 900k
32896         0x8080          bzip2 compressed data, block size = 900k
38269         0x957D          bzip2 compressed data, block size = 900k
50728         0xC628          bzip2 compressed data, block size = 900k
```

Then checking out the extracted files and running:
```
└─$ file *
30DF: bzip2 compressed data, block size = 900k
34:   JPEG image data, JFIF standard 1.01, aspect ratio, density 1x1, segment length 16, baseline, precision 8, 968x118, components 3
8080: bzip2 compressed data, block size = 900k
957D: JPEG image data, JFIF standard 1.01, aspect ratio, density 1x1, segment length 16, baseline, precision 8, 968x118, components 3
C628: bzip2 compressed data, block size = 900k
```

Revealed to jpeg files.

Opening the jpeg files showed the flag.