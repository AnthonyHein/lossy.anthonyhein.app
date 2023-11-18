from printable_string import PrintableString


class Encoder:
    @staticmethod
    def encode(plaintext: str):
        try:
            plaintext = PrintableString(plaintext)
        except ValueError:
            return None, None

        key = PrintableString.generate_key(len(plaintext))
        ciphertext = plaintext + key

        return key, ciphertext

    @staticmethod
    def decode(key: str, ciphertext: str) -> str:
        return str(PrintableString(ciphertext) + (-PrintableString(key)))
