from PyMdlxConverter.common.binarystream import BinaryStream
from PyMdlxConverter.parsers.mdlx.tokenstream import TokenStream
from PyMdlxConverter.parsers.mdlx.genericobject import GenericObject
from PyMdlxConverter.parsers.errors import TokenStreamError


class CollisionShape(GenericObject):

    def __init__(self):
        super().__init__(flags=0x2000)
        self.type = -1
        self.vertices = [[], []]  # 2 by 3 float array
        self.bounds_radius = 0

    def read_mdx(self, stream: BinaryStream, version):
        super().read_mdx(stream, version)
        self.type = stream.read_uint32()
        self.vertices[0] = stream.read_float32_array(3)
        if self.type != 2:
            self.vertices[1] = stream.read_float32_array(3)
        if self.type == 2 or self.type == 3:
            self.bounds_radius = stream.read_float32()

    def write_mdx(self, stream: BinaryStream, version):
        super().write_mdx(stream, version)
        stream.write_uint32(self.type)
        stream.write_float32_array(self.vertices[0])
        if self.type != 2:
            stream.write_float32_array(self.vertices[1])
        if self.type == 2 or self.type == 3:
            stream.write_float32(self.bounds_radius)

    def read_mdl(self, stream: TokenStream):
        for token in super().read_generic_block(stream):
            if token == 'Box':
                self.type = 0
            elif token == 'Plane':
                self.type = 1
            elif token == 'Sphere':
                self.type = 2
            elif token == 'Cylinder':
                self.type = 3
            elif token == 'Vertices':
                count = stream.read_int()
                stream.read()
                self.vertices[0] = stream.read_vector(3)
                if count == 2:
                    self.vertices[1] = stream.read_vector(3)
                stream.read()
            elif token == 'BoundsRadius':
                self.bounds_radius = stream.read_float()
            else:
                raise TokenStreamError('CollisionShape', token)

    def write_mdl(self, stream: TokenStream, version=None):
        stream.start_object_block('CollisionShape', self.name)
        self.write_generic_header(stream)
        _type = ''
        vertices = 2
        bounds_radius = False
        if self.type == 0:
            _type = 'Box'
        elif self.type == 1:
            _type = 'Plane'
        elif self.type == 2:
            _type = 'Sphere'
            vertices = 1
            bounds_radius = True
        elif self.type == 3:
            _type = 'Cylinder'
            bounds_radius = True
        stream.write_flag(_type)
        stream.start_block('Vertices', vertices)
        stream.write_vector(self.vertices[0])
        if vertices == 2:
            stream.write_vector(self.vertices[1])
        stream.end_block()
        if bounds_radius:
            stream.write_number_attrib('BoundsRadius', self.bounds_radius)
        self.write_generic_animations(stream)
        stream.end_block()

    def get_byte_length(self, version=None):
        size = 16 + super().get_byte_length(version=version)
        if self.type != 2:
            size += 12
        if self.type == 2 or self.type == 3:
            size += 4
        return size
