from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes

from cipher.generate import KEYS_PATH


# Decrypting data by private key
def decrypt_data(private_pem: bytes, encrypted_data: bytes) -> str:
    private_key = serialization.load_pem_private_key(private_pem, password=None)

    # Decrypted data
    encrypted_data = private_key.decrypt(
        encrypted_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return encrypted_data.decode()

# Decrypt note
def decrypt_note(note: dict, username: str) -> dict:
    private_pem = get_private_key(username)

    note["header"] = decrypt_data(private_pem, note["header"])
    note["content"] = decrypt_data(private_pem, note["content"])
    note["tags"] = decrypt_data(private_pem, note["tags"])

    return note

# Read private key from file
def get_private_key(username: str) -> bytes:
    with open(f"{KEYS_PATH}/{username}_key.pem", "rb") as file:
        return file.read()
