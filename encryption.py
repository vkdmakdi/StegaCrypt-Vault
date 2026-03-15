import streamlit as st
from PIL import Image
import io
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

# --- CRYPTOGRAPHY UTILS ---
def derive_key(password: str, salt: bytes) -> bytes:
    """Derives a 32-byte key from a password and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_data(data: str, password: str):
    salt = b'\x00' * 16 
    key = derive_key(password, salt)
    f = Fernet(key)
    return f.encrypt(data.encode()).decode()

def decrypt_data(token: str, password: str):
    salt = b'\x00' * 16
    key = derive_key(password, salt)
    f = Fernet(key)
    try:
        return f.decrypt(token.encode()).decode()
    except Exception:
        return None

# --- STEGANOGRAPHY LOGIC ---
def msg_to_bin(msg):
    if type(msg) == str:
        return ''.join([format(ord(i), "08b") for i in msg])
    elif type(msg) == bytes or type(msg) == list:
        return ''.join([format(i, "08b") for i in msg])
    elif type(msg) == int or type(msg) == float:
        return format(msg, "08b")

def encode_lsb(image, secret_msg):
    # Add a unique delimiter to identify the end of the message
    secret_msg += "#####" 
    binary_secret = msg_to_bin(secret_msg)
    
    data_len = len(binary_secret)
    img_data = iter(image.getdata())
    
    new_pixels = []
    
    for i in range(0, data_len, 3):
        # Extract 3 pixels (9 channels) at a time
        pixel = [list(next(img_data)) for _ in range(3)]
        
        for j in range(3): # RGB
            for k in range(3): # Each channel
                if i < data_len:
                    # Update the LSB
                    pixel[j][k] = pixel[j][k] & ~1 | int(binary_secret[i])
                    i += 1
        
        for p in pixel:
            new_pixels.append(tuple(p))
            
    # Add remaining original pixels
    while True:
        try:
            new_pixels.append(next(img_data))
        except StopIteration:
            break
            
    new_img = Image.new(image.mode, image.size)
    new_img.putdata(new_pixels)
    return new_img

def decode_lsb(image):
    binary_data = ""
    img_data = iter(image.getdata())
    
    while True:
        pixel = [list(next(img_data)) for _ in range(3)]
        for j in range(3):
            for k in range(3):
                binary_data += str(pixel[j][k] & 1)
        
        # Convert bits to bytes
        all_bytes = [binary_data[i: i+8] for i in range(0, len(binary_data), 8)]
        
        # Decode bytes to characters
        decoded_data = ""
        for byte in all_bytes:
            decoded_data += chr(int(byte, 2))
            if decoded_data[-5:] == "#####": # Check for delimiter
                return decoded_data[:-5]

# --- STREAMLIT UI ---
st.set_page_config(page_title="Ghost-In-The-Pixel", page_icon="👻")

st.title("Ghost-In-The-Pixel")
st.markdown("Encrypt and hide secret messages inside images using **AES-256** and **LSB Steganography**.")

tab1, tab2 = st.tabs(["🔒 Encode", "🔓 Decode"])

with tab1:
    st.header("Hide a Message")
    uploaded_file = st.file_uploader("Choose an image...", type=["png", "jpg", "jpeg"], key="enc_upload")
    message = st.text_area("Secret Message")
    password = st.text_input("Encryption Password", type="password", key="enc_pass")
    
    if st.button("Generate Encoded Image"):
        if uploaded_file and message and password:
            with st.spinner("Encrypting and hiding..."):
                img = Image.open(uploaded_file).convert("RGB")
                encrypted_msg = encrypt_data(message, password)
                encoded_img = encode_lsb(img, encrypted_msg)
                
                # Save to buffer
                buf = io.BytesIO()
                encoded_img.save(buf, format="PNG")
                byte_im = buf.getvalue()
                
                st.image(encoded_img, caption="Encoded Image (Looks identical!)", use_container_width=True)
                st.download_button("Download Encoded Image", byte_im, "secret_image.png", "image/png")
        else:
            st.error("Please provide an image, message, and password.")

with tab2:
    st.header("Extract a Message")
    decode_file = st.file_uploader("Upload the encoded image", type=["png"], key="dec_upload")
    dec_password = st.text_input("Decryption Password", type="password", key="dec_pass")
    
    if st.button("Extract Message"):
        if decode_file and dec_password:
            with st.spinner("Searching pixels..."):
                img = Image.open(decode_file).convert("RGB")
                extracted_encrypted = decode_lsb(img)
                final_msg = decrypt_data(extracted_encrypted, dec_password)
                
                if final_msg:
                    st.success("Message Found!")
                    st.code(final_msg)
                else:
                    st.error("Failed to decrypt. Wrong password or no hidden message.")