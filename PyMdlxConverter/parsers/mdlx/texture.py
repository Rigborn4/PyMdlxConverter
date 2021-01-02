from PyMdlxConverter.common.binarystream import BinaryStream
from PyMdlxConverter.parsers.mdlx.tokenstream import TokenStream
from PyMdlxConverter.parsers.errors import TokenStreamError


class Texture(object):

    def __init__(self):
        self.replaceable_id = 0
        self.path = ''
        self.flags = 0

    def read_mdx(self, stream: BinaryStream):
        self.replaceable_id = stream.read_uint32()
        self.path = stream.read(260)
        self.flags = stream.read_uint32()

    def write_mdx(self, stream: BinaryStream):
        stream.write_uint32(self.replaceable_id)
        stream.write(self.path)
        stream.skip(260 - len(self.path))
        stream.write_uint32(self.flags)

    def read_mdl(self, stream: TokenStream):
        for token in stream.read_block():
            if token == 'Image':
                self.path = stream.read()
            elif token == 'ReplaceableId':
                self.replaceable_id = stream.read_int()
            elif token == 'WrapWidth':
                self.flags |= 0x1
            elif token == 'WrapHeight':
                self.flags |= 0x2
            else:
                raise TokenStreamError('Texture', token)

    def write_mdl(self, stream: TokenStream, version=None):
        stream.start_block('Bitmap', None)
        if len(self.path):
            stream.write_string_attrib('Image', self.path)
        if self.replaceable_id != 0:
            stream.write_number_attrib('ReplaceableId', self.replaceable_id)
        if self.flags & 0x1:
            stream.write_flag('WrapWidth')
        if self.flags & 0x2:
            stream.write_flag('WrapHeight')
        stream.end_block()
