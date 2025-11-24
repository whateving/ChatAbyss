#What is ChatAbyss

ChatAbyss is Tor-based, terminal-only, anonymous, end-to-end encrypted, and disposable messaging app. The messages do not get saved, so once you are done, you can just delete the server, crypto, and client files and that is it.

# How to setup ChatAbyss

## Upload crypto.py on both the server and the client

Run the following command to generate an encryption/decryption key that you can share through other secure means, it could be through a signal app, or temp mail:

`
python3 -c "from nacl.utils import random import base64; print(base64.b64encode(random(32)).decode())"
`

Paste the encryption/decryption key into the crypto.py on both the server and client sides.

## Server Configs

Add the following configuration to the ```/etc/tor/torrc``` file.

<img width="465" height="338" alt="image" src="https://github.com/user-attachments/assets/b07d93da-0a6a-4d62-b8a5-f07c2d39cdae" />



Then start tor service by running the following command:

`
sudo systemctl start tor
`

Run the following command to get your onion link:

`
sudo cat /var/lib/tor/chatabyss/hostname
`

Then start the server file on any server you want your clients to connect to:

Example:
`
python3 server.py --host 127.0.0.1 --port 8000
`

## Client Config

You do not need to do much configuration on the client except for starting tor and running the client file as so:

Example:
`
python3 client.py --host site.onion --port 80 --nick john
`

Now your messages are end-to-end encrypted, anonymous, and running through Tor, you can verify this by running tcpdump and checking if the messages are encrypted.
