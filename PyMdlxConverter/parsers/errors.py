class BinaryStreamError(Exception):
    def __init__(self, buffer_type):
        self.message = f'BinaryStream: expected bytes or bytearray object got {buffer_type} instead'

    def __str__(self):
        return self.message


class ByteStreamError(Exception):
    def __init__(self, func_name, left_bytes, want_bytes=None):
        if want_bytes:
            self.message = f'ByteStream: {func_name}: premature end - want {want_bytes} bytes but have {left_bytes}'
        else:
            self.message = f'ByteStream: {func_name}: premature end - want 1 byte but have {left_bytes}'

    def __str__(self):
        return self.message


class TokenStreamError(Exception):
    def __init__(self, section, token, want_name=None, want_target=None):
        if want_name:
            if want_target:
                self.message = f"TokenStream: Unknown token in {section} {want_name}'s "+f'Target: "{token}"'
            else:
                self.message = f'TokenStream: Unknown token in {section} {want_name}: "{token}"'
        else:
            self.message = f'TokenStream: Unknown token in {section}: "{token}"'

    def __str__(self):
        return self.message
