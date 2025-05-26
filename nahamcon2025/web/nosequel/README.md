# NoSequel

Author: @HuskyHacks

It always struck me as odd that none of these movies ever got sequels! Absolute cinema.

Press the Start button on the top-right to begin this challenge.

![alt text](image.png)

This seems to be a challenge involving querying a nosequel db.

We can enter a search query and select a collection and it tells whether the pattern matched or not.
![alt text](image-1.png)

This can easily be bruteforced since we already know the flag format, we can bruteforce each character of the flag till it matched, once it has matched, we can move onto the next character.

Wrote a quick script for this bruteforcing and got the flag.

![alt text](image-2.png)