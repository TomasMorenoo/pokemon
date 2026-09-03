import struct
from .constants import GEN3_CHAR_TABLE, STRING_TERMINATOR


def decode_gen3_string(data: bytes, max_length: int) -> str:
    chars = []
    for i in range(min(max_length, len(data))):
        byte = data[i]
        if byte == STRING_TERMINATOR:
            break
        chars.append(GEN3_CHAR_TABLE.get(byte, "?"))
    return "".join(chars)
