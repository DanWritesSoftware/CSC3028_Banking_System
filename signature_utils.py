import os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.exceptions import InvalidSignature

PRIVATE_KEY_FILE = "signature_private_key.pem"
PUBLIC_KEY_FILE = "signature_public_key.pem"

def generate_keys():
    """Generates an rsa key pair and saves them to pem files"""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Save Private Key
    with open(PRIVATE_KEY_FILE, "wb") as priv_file:
        priv_file.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    # Save Public Key
    public_key = private_key.public_key()

    with open(PUBLIC_KEY_FILE, "wb") as pub_file:
        pub_file.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )

    print ("[INFO] Digital Signature Keys Generated")

def load_private_key():
    """Loads private key from file, generates one if missing"""
    
    if not os.path.exists(PRIVATE_KEY_FILE):
        generate_keys()

    with open(PRIVATE_KEY_FILE, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)
    
def load_public_key():
    """Loads public key from file, generates one if missing"""
    if not os.path.exists(PUBLIC_KEY_FILE):
        generate_keys()

    with open(PUBLIC_KEY_FILE, "rb") as f:
        return serialization.load_pem_public_key(f.read())
    
def sign_message(message: str) -> bytes:
    """Signs a string message using a private key"""

    private_key = load_private_key()
    signature = private_key.sign(
        message.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    return signature

def verify_signature(message: str, signature: bytes) -> bool:
    """Verifies the signature of a string message using the public key"""

    public_key = load_public_key()

    try:
        public_key.verify(
            signature,
            message.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False

