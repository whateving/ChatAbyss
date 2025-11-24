from nacl.secret import SecretBox           # symmetric authenticated encryption
from nacl.utils import random               # secure random for nonces
import base64

# <<< REPLACE with your own 32-byte Base64 key (same on all peers) >>>
KEY_B64 = "PASTE_KEY"
KEY = base64.b64decode(KEY_B64)
box = SecretBox(KEY)

def encrypt_message(msg: str) -> str:
    """Plaintext -> Base64 ciphertext (nonce included)."""
    nonce = random(SecretBox.NONCE_SIZE)
    ct = box.encrypt(msg.encode(), nonce)       # includes nonce + ciphertext + MAC
    return base64.b64encode(ct).decode()

def decrypt_message(b64_ct: str) -> str:
    """Base64 ciphertext (optionally 'MSG:'/'SYS:' prefixed) -> plaintext."""
    if b64_ct.startswith(("MSG:", "SYS:")):
        b64_ct = b64_ct[4:]                     # strip protocol prefix
    try:
        ct = base64.b64decode(b64_ct)
        pt = box.decrypt(ct)
        return pt.decode()
    except Exception:
        return "[cannot decrypt]"
