StegaCrypt-Vault

Itis a dual-layer security tool written in Python that combines **AES-256 Symmetric Encryption** with **LSB (Least Significant Bit) Steganography**. It allows you to hide sensitive information inside ordinary image files without altering their visual appearance.

Features
* **Dual-Layer Protection:** Messages are first encrypted using a password-derived key (PBKDF2) before being injected into pixels.
* **Visual Integrity:** Uses LSB encoding to ensure the resulting `.png` is indistinguishable from the original to the human eye.
* **Zero-Knowledge:** The server never stores your password or your unencrypted message.
* **Web Interface:** Built with Streamlit for a seamless drag-and-drop user experience.

Tech Stack
* **Language:** Python 3.x
* **Encryption:** `cryptography` (Fernet/AES-256)
* **Image Processing:** `Pillow` (PIL)
* **Frontend/Deployment:** `Streamlit`

How It Works
1.  **Encryption:** Your plaintext message is encrypted into a ciphertext string using a key derived from your password.
2.  **Bit Manipulation:** The binary representation of that ciphertext is spread across the least significant bits of the image's RGB channels.
3.  **Extraction:** The decoder reads the LSBs, reconstructs the ciphertext, and prompts for the password to return the original message.
