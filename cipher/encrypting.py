from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes

from models.notes import NoteInternalModel, NoteUpdateInternalModel


# Encrypting data by public key
def encrypt_data(public_pem: bytes, data: str) -> bytes:
    public_key = serialization.load_pem_public_key(public_pem)  # Load pub_key

    # Encrypted data
    encrypted_data = public_key.encrypt(
        data.encode(),  # To bytes
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return encrypted_data

# Encrypting note
def encrypt_note(public_pem: bytes, note: NoteInternalModel | NoteUpdateInternalModel) -> NoteInternalModel | NoteUpdateInternalModel:

    note.header = encrypt_data(public_pem, note.header)
    note.text = encrypt_data(public_pem, note.text)
    note.tags = encrypt_data(public_pem, note.tags)

    return note
