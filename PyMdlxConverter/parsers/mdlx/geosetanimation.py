from PyMdlxConverter.common.binarystream import BinaryStream
from PyMdlxConverter.parsers.mdlx.tokenstream import TokenStream
from PyMdlxConverter.parsers.mdlx.animatedobject import AnimatedObject
from PyMdlxConverter.parsers.errors import TokenStreamError


class GeosetAnimation(AnimatedObject):

    def __init__(self):
        super().__init__()
        self.alpha = 1
        self.flags = 0
        self.color = [1, 1, 1]
        self.geoset_id = -1

    def read_mdx(self, stream: BinaryStream, version):
        size = stream.read_uint32()
        self.alpha = stream.read_float32()
        self.flags = stream.read_uint32()
        self.color = stream.read_float32_array(3)
        self.geoset_id = stream.read_int32()
        self.read_animations(stream, size - 28)

    def write_mdx(self, stream: BinaryStream, version):
        stream.write_uint32(self.get_byte_length())
        stream.write_float32(self.alpha)
        stream.write_uint32(self.flags)
        stream.write_float32_array(self.color)
        stream.write_int32(self.geoset_id)
        self.write_animations(stream)

    def read_mdl(self, stream: TokenStream, version=None):
        for token in super().read_animated_block(stream):
            if token == 'DropShadow':
                self.flags |= 0x1
            elif token == 'static Alpha':
                self.alpha = stream.read_float()
            elif token == 'Alpha':
                self.read_animation(stream, 'KGAO')
            elif token == 'static Color':
                self.flags |= 0x2
                self.color = stream.read_color()
            elif token == 'Color':
                self.flags |= 0x2
                self.read_animation(stream, 'KGAC')
            elif token == 'GeosetId':
                self.geoset_id = stream.read_int()
            else:
                raise TokenStreamError('GeosetAnimation', token)

    def write_mdl(self, stream: TokenStream, version=None):
        stream.start_block('GeosetAnim', None)
        if self.flags & 0x1:
            stream.write_flag('DropShadow')
        if not self.write_animation(stream, 'KGAO'):
            stream.write_number_attrib('static Alpha', self.alpha)
        if self.flags & 0x2:
            if not self.write_animation(stream, 'KGAC') and (self.color[0] != 1 or self.color[1] != 1
                                                             or self.color[2] != 1):
                stream.write_color('static Color ', self.color)
        stream.write_number_attrib('GeosetId', self.geoset_id)
        stream.end_block()

    def get_byte_length(self, version=None):
        return 28 + super().get_byte_length()
