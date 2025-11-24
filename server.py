#!/usr/bin/env python3

import asyncio
import argparse
from crypto import encrypt_message

clients = set()

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    clients.add(writer)
    nick = "anon"
    try:
        # Expect the first line from the client to be the nickname (plaintext to server only)
        nick_line = await reader.readline()
        if not nick_line:
            writer.close(); await writer.wait_closed(); return
        nick = nick_line.decode(errors="ignore").strip() or "anon"

        # Announce join (encrypted system notice)
        broadcast("SYS:" + encrypt_message(f"*** {nick} joined"))

        # Relay loop: clients send already-encrypted lines (e.g., 'MSG:<b64>')
        while True:
            data = await reader.readline()
            if not data:
                break
            line = data.decode(errors="ignore").strip()
            if not line:
                continue
            # IMPORTANT: do NOT re-encrypt; forward exactly as received
            broadcast(line)

    except Exception as e:
        print(f"[!] Client error {addr}: {e}")
    finally:
        clients.discard(writer)
        broadcast("SYS:" + encrypt_message(f"*** {nick} left"))
        try:
            writer.close(); await writer.wait_closed()
        except:
            pass

def broadcast(message: str):
    dead = []
    for w in clients:
        try:
            w.write((message + "\n").encode())
        except Exception:
            dead.append(w)
    for d in dead:
        clients.discard(d)
    asyncio.create_task(_drain_all())

async def _drain_all():
    tasks = []
    for w in list(clients):
        try:
            tasks.append(w.drain())
        except:
            clients.discard(w)
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)

async def main(host, port):
    server = await asyncio.start_server(handle_client, host, port)
    print(f"[+] Server listening on {host}:{port}")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()
    try:
        asyncio.run(main(args.host, args.port))
    except KeyboardInterrupt:
        print("\n[!] Server stopped")
