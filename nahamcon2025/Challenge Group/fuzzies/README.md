Author: BuildHackSecure @ HackingHub

HackingHub has provided this CTF challenge!

This is the container control panel card for the Fuzzies challenge group. Use this same container for all five flags to be uncovered. For that reason, this challenge card intentionally has no points. You may submit flag{} to mark this as complete at your leisure.

Remember those cute toys from the 90s? I think there's something a bit more sinister going on!


```
ffuf -w wordlist.txt -u http://challenge.nahamcon.com:30505/api/FUZZ -e .php,.json,.txt,.html -mc all -fc 404
# Specifically check for v1, v2 as they are in your wordlist
ffuf -w wordlist.txt -u http://challenge.nahamcon.com:30505/api/v1/FUZZ -e .php,.json,.txt,.html -mc all -fc 404
ffuf -w wordlist.txt -u http://challenge.nahamcon.com:30505/api/v2/FUZZ -e .php,.json,.txt,.html -mc all -fc 404
```


```

 :: Method           : GET
 :: URL              : http://challenge.nahamcon.com:30505/api/FUZZ
 :: Wordlist         : FUZZ: /home/pg/CTF-Writeups/nahamcon2025/web/fuzzies/wordlist/wordlist.txt
 :: Extensions       : .php .json .txt .html 
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: all
 :: Filter           : Response status: 404
________________________________________________

users                   [Status: 401, Size: 48, Words: 2, Lines: 1, Duration: 271ms]
:: Progress: [520/520] :: Job [1/1] :: 151 req/sec :: Duration: [0:00:04] :: Errors: 0 ::
```
