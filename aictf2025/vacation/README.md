# Vacation
Author: Timur Kasimov, PT ML Team
ML: 15%CTF: 85%llmweb
I’m so burnt out from playing AI CTF!

Just when I thought I can finally relax, I’ve faced the ultimate obstacle: a stubborn AI-driven vacation request system.

Can you help me circumvent the automated bureaucracy?

![alt text](image.png)

The website is a streamlit app for vacation assistant. The main challenge lies in probing it for answers. First, I tried to figure out what all tools etc. it has access to.

![alt text](image-1.png)

![alt text](image-2.png)

![alt text](image-3.png)

It seems that the schema is on /openapi.json

![alt text](image-4.png)

The schema shows these routes:
![alt text](image-5.png)

After creating a user and getting the token, I created a vacation:
![alt text](image-6.png)

After some prompt injection, I got the admin creds and used that and some more prompt injection I got them to approve the vacation and got the flag:

![alt text](image-7.png)

![alt text](image-8.png)