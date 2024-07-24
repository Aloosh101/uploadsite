from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from logging import basicConfig, INFO, info, error

basicConfig(level=INFO)

class AESCipher:
    def __init__(self, password: str):
        try:
            self.key = self._generate_key(password)
            info(f"Generated key done")
            return None
        except Exception as e:
            error(f"generate key error caused by: {e}")
            return None

    def _generate_key(self, password: str) -> bytes:
        return password.encode('utf-8').ljust(32, b'\0')[:32]
        
    def encrypt_string(self, text: str) -> str:
        try:
            plain_text = text.encode('utf-8')
            iv = get_random_bytes(AES.block_size)
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            cipher_text = cipher.encrypt(pad(plain_text, AES.block_size))
            return (iv + cipher_text).hex()
        except Exception as e:
            error(f"Failed to encrypt string caused by: {e}")
            return None
        
    def decrypt_string(self, cipher_text: str) -> str:
        try:
            cipher_text = bytes.fromhex(cipher_text)
            iv = cipher_text[:AES.block_size]
            cipher_text = cipher_text[AES.block_size:]
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            plain_text = unpad(cipher.decrypt(cipher_text), AES.block_size)
            return plain_text.decode('utf-8')
        except Exception as e:
            error(f"Failed to decrypt string caused by: {e}")
            return None

    def encrypt_file_content(self, data: bytes) -> None:
        try:
            plain_text = data
            iv = get_random_bytes(AES.block_size)
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            cipher_text = cipher.encrypt(pad(plain_text, AES.block_size))
            encrypted_data = iv + cipher_text
            return encrypted_data
            #with open(file_path + '.enc', 'wb') as file:
                #file.write(encrypted_data)
        except Exception as e:
            error(f"Failed to encrypt file content caused by: {e}")
            return None

    def decrypt_file_content(self, data: bytes) -> None:
        try:
            cipher_text = data
            iv = cipher_text[:AES.block_size]
            cipher_text = cipher_text[AES.block_size:]
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            plain_text = unpad(cipher.decrypt(cipher_text), AES.block_size)
            return plain_text
            #with open(file_path[:-4], 'wb') as file:
            #    file.write(plain_text)
        except Exception as e:
            error(f"Failed to decrypt file content caused by: {e}")
            return None
