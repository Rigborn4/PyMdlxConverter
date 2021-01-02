from PyMdlxConverter.common.binarystream import BinaryStream
from PyMdlxConverter.parsers.mdlx.tokenstream import TokenStream
from PyMdlxConverter.parsers.mdlx.animatedobject import AnimatedObject
from PyMdlxConverter.parsers.errors import TokenStreamError


class TextureAnimation(AnimatedObject):

    def read_mdx(self, stream: BinaryStream):
        size = stream.read_uint32()
        self.read_animations(stream, size - 4)

    def write_mdx(self, stream: BinaryStream):
        stream.write_uint32(self.get_byte_length())
        self.write_animations(stream)

    def read_mdl(self, stream: TokenStream):
        for token in stream.read_block():
            if token == 'Translation':
                self.read_animation(stream, 'KTAT')
            elif token == 'Rotation':
                self.read_animation(stream, 'KTAR')
            elif token == 'Scaling':
                self.read_animation(stream, 'KTAS')
            else:
                raise TokenStreamError('TextureAnimation', token)

    def write_mdl(self, stream: TokenStream, version=None):
        stream.start_block('TVertexAnim', None)
        self.write_animation(stream, 'KTAT')
        self.write_animation(stream, 'KTAR')
        self.write_animation(stream, 'KTAS')
        stream.end_block()
