# utils/crypto.py
import os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend

KEY_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'keys')
PRIVATE_KEY_PATH = os.path.join(KEY_DIR, 'private_key.pem')
PUBLIC_KEY_PATH = os.path.join(KEY_DIR, 'public_key.pem')

def ensure_keys(key_dir=KEY_DIR, private_path=PRIVATE_KEY_PATH, public_path=PUBLIC_KEY_PATH, bits=2048):
    os.makedirs(key_dir, exist_ok=True)
    if not os.path.exists(private_path) or not os.path.exists(public_path):
        # generate new keypair
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=bits,
            backend=default_backend()
        )
        # serialize private
        with open(private_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
        # serialize public
        public_key = private_key.public_key()
        with open(public_path, "wb") as f:
            f.write(public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))
    return private_path, public_path

def load_private_key(path=PRIVATE_KEY_PATH):
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())

def load_public_key(path=PUBLIC_KEY_PATH):
    with open(path, "rb") as f:
        return serialization.load_pem_public_key(f.read(), backend=default_backend())

def sign_bytes(data: bytes, private_key=None):
    """
    Returns signature bytes for data using RSA-PSS + SHA256
    """
    if private_key is None:
        private_key = load_private_key()
    signature = private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

def verify_bytes(data: bytes, signature: bytes, public_key=None):
    """
    Returns True if signature verifies, False otherwise.
    """
    if public_key is None:
        public_key = load_public_key()
    try:
        public_key.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False
