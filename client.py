#!/usr/bin/env python3

import argparse, socket, threading, sys, shutil
from datetime import datetime
from crypto import encrypt_message, decrypt_message

# --- ANSI color helpers (no extra deps) ---
RESET = "\x1b[0m"; BOLD = "\x1b[1m"; DIM = "\x1b[2m"
FG_GREEN = "\x1b[32m"; FG_CYAN = "\x1b[36m"; FG_BLUE = "\x1b[34m"
FG_MAGENTA = "\x1b[35m"; FG_GREY = "\x1b[90m"; FG_YELLOW = "\x1b[33m"

def term_width(default=80):
    try: return shutil.get_terminal_size().columns
    except Exception: return default

def ts():  # timestamp
    return f"{FG_GREY}{datetime.now().strftime('%H:%M:%S')}{RESET}"

def safe_print(s):
    sys.stdout.write("\r" + " " * term_width() + "\r")
    print(s)
    sys.stdout.write(f"{FG_YELLOW}You:{RESET} "); sys.stdout.flush()

def render(line, mynick):
    """Pretty print decrypted message."""
    if line.startswith("*** "):  # system message
        return f"{ts()} {FG_CYAN}{DIM}{line}{RESET}"
    if ": " in line:
        nick, text = line.split(": ", 1)
        if nick == mynick:
            return (
                f"{ts()}  {FG_GREEN}{text}{RESET}  "
                f"—{BOLD}{FG_GREEN}{nick}{RESET}".rjust(term_width())
            )
        else:
            return f"{BOLD}{FG_BLUE}{nick}{RESET}: {text}  {ts()}"
    return f"{ts()} {line}"

def recv_loop(sock, mynick):
    buf = ""
    while True:
        data = sock.recv(4096)
        if not data:
            safe_print(f"{FG_CYAN}{DIM}*** disconnected{RESET}")
            break
        buf += data.decode(errors="ignore")
        while "\n" in buf:
            line, buf = buf.split("\n", 1)
            line = line.strip()
            if not line: continue
            plain = decrypt_message(line)
            safe_print(render(plain, mynick))

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--host", required=True)
    p.add_argument("--port", type=int, required=True)
    p.add_argument("--nick", default="anon")
    args = p.parse_args()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((args.host, args.port))
    except Exception as e:
        print("Connection failed:", e); return

    threading.Thread(target=recv_loop, args=(s, args.nick), daemon=True).start()
    s.sendall((args.nick + "\n").encode())  # send nickname

    sys.stdout.write(f"{FG_YELLOW}You:{RESET} "); sys.stdout.flush()
    try:
        while True:
            line = sys.stdin.readline()
            if not line: break
            msg = line.strip()
            if not msg:
                sys.stdout.write(f"{FG_YELLOW}You:{RESET} "); sys.stdout.flush()
                continue
            ciphertext = encrypt_message(f"{args.nick}: {msg}")
            s.sendall((ciphertext + "\n").encode())
            safe_print(render(f"{args.nick}: {msg}", args.nick))
    except KeyboardInterrupt:
        pass
    finally:
        s.close()

if __name__ == "__main__":
    main()
