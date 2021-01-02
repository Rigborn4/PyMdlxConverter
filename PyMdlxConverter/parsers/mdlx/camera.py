from PyMdlxConverter.common.binarystream import BinaryStream
from PyMdlxConverter.parsers.mdlx.tokenstream import TokenStream
from PyMdlxConverter.parsers.mdlx.animatedobject import AnimatedObject
from PyMdlxConverter.parsers.errors import TokenStreamError


class Camera(AnimatedObject):

    def __init__(self):
        super().__init__()
        self.name = ''
        self.position = 3
        self.field_of_view = 0
        self.far_clipping_plane = 0
        self.near_clipping_plane = 0
        self.target_position = 3

    def read_mdx(self, stream: BinaryStream, version):
        size = stream.read_uint32()
        self.name = stream.read(80)
        self.position = stream.read_float32_array(3)
        self.field_of_view = stream.read_float32()
        self.far_clipping_plane = stream.read_float32()
        self.near_clipping_plane = stream.read_float32()
        self.target_position = stream.read_float32_array(3)
        self.read_animations(stream, size - 120)

    def write_mdx(self, stream: BinaryStream, version):
        stream.write_uint32(self.get_byte_length(version=version))
        stream.write(self.name)
        stream.skip(80 - len(self.name))
        stream.write_float32_array(self.position)
        stream.write_float32(self.field_of_view)
        stream.write_float32(self.far_clipping_plane)
        stream.write_float32(self.near_clipping_plane)
        stream.write_float32_array(self.target_position)
        self.write_animations(stream)

    def read_mdl(self, stream: TokenStream):
        self.name = stream.read()
        for token in stream.read_block():
            if token == 'Position':
                self.position = stream.read_vector(3)
            elif token == 'Translation':
                self.read_animation(stream, 'KCTR')
            elif token == 'Rotation':
                self.read_animation(stream, 'KCRL')
            elif token == 'FieldOfView':
                self.field_of_view = stream.read_float()
            elif token == 'FarClip':
                self.far_clipping_plane = stream.read_float()
            elif token == 'NearClip':
                self.near_clipping_plane = stream.read_float()
            elif token == 'Target':
                for token in stream.read_block():
                    if token == 'Position':
                        self.target_position = stream.read_vector(3)
                    elif token == 'Translation':
                        self.read_animation(stream, 'KTTR')
                    else:
                        raise TokenStreamError('Camera', token, want_name=self.name, want_target=1)
            else:
                raise TokenStreamError('Camera', token, want_name=self.name)

    def write_mdl(self, stream: TokenStream, version=None):
        stream.start_object_block('Camera', self.name)
        stream.write_vector_attrib('Position', self.position)
        self.write_animation(stream, 'KCTR')
        self.write_animation(stream, 'KCRL')
        stream.write_number_attrib('FieldOfView', self.field_of_view)
        stream.write_number_attrib('FarClip', self.far_clipping_plane)
        stream.write_number_attrib('NearClip', self.near_clipping_plane)
        stream.start_block('Target', None)
        stream.write_vector_attrib('Position', self.target_position)
        self.write_animation(stream, 'KTTR')
        stream.end_block()
        stream.end_block()

    def get_byte_length(self, version=None):
        return 120 + super().get_byte_length(version=version)