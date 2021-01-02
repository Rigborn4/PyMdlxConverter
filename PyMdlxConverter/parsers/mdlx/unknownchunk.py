from PyMdlxConverter.common.binarystream import BinaryStream


class UnknownChunk(object):

    def __init__(self, stream: BinaryStream, size: int, tag: str):
        self.tag = tag
        self.chunk = stream.read_uint8_array(size)

    def write_mdx(self, stream: BinaryStream):
        stream.write(self.tag)
        stream.write_uint32(len(self.chunk))
        stream.write_uint8_array(self.chunk)

    def get_byte_length(self) -> int:
        return 8 + len(self.chunk)
