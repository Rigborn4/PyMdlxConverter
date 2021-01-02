from PyMdlxConverter.common.binarystream import BinaryStream
from PyMdlxConverter.parsers.mdlx.tokenstream import TokenStream
from PyMdlxConverter.parsers.mdlx.layer import Layer
from PyMdlxConverter.parsers.errors import TokenStreamError


class Material(object):

    def __init__(self):
        self.priority_plane = 0
        self.flags = 0
        self.shader = ''
        self.layers = []

    def read_mdx(self, stream: BinaryStream, version: int):
        stream.read_uint32()
        self.priority_plane = stream.read_int32()
        self.flags = stream.read_uint32()
        if version > 800:
            self.shader = stream.read(80)
        stream.skip(4)  # LAYS
        for i in range(stream.read_uint32()):
            layer = Layer()
            layer.read_mdx(stream, version)
            self.layers.append(layer)

    def write_mdx(self, stream: BinaryStream, version: int):
        stream.write_uint32(self.get_byte_length(version))
        stream.write_int32(self.priority_plane)
        stream.write_uint32(self.flags)
        if version > 800:
            stream.write(self.shader)
            stream.skip(80 - len(self.shader))
        stream.write('LAYS')
        stream.write_uint32(len(self.layers))
        for layer in self.layers:
            layer.write_mdx(stream, version)

    def read_mdl(self, stream: TokenStream, version=None):
        for token in stream.read_block():
            if token == 'ConstantColor':
                self.flags |= 0x1
            elif token == 'TwoSided':
                self.flags |= 0x2
            elif token == 'SortPrimsNearZ':
                self.flags |= 0x8
            elif token == 'SortPrimsFarZ':
                self.flags |= 0x10
            elif token == 'FullResolution':
                self.flags |= 0x20
            elif token == 'PriorityPlane':
                self.priority_plane = stream.read_int()
            elif token == 'Shader':
                self.shader = stream.read()
            elif token == 'Layer':
                layer = Layer()
                layer.read_mdl(stream)
                self.layers.append(layer)
            else:
                raise TokenStreamError('Material', token)

    def write_mdl(self, stream: TokenStream, version=None):
        stream.start_block('Material', None)
        if self.flags & 0x1:
            stream.write_flag('ConstantColor')
        if version > 800:
            if self.flags & 0x2:
                stream.write_flag('TwoSided')
        if self.flags & 0x8:
            stream.write_flag('SortPrimsNearZ')
        if self.flags & 0x10:
            stream.write_flag('SortPrimsFarZ')
        if self.flags & 0x20:
            stream.write_flag('FullResolution')
        if self.priority_plane != 0:
            stream.write_number_attrib('PriorityPlane', self.priority_plane)
        if version > 800:
            stream.write_string_attrib('Shader', self.shader)
        for layer in self.layers:
            layer.write_mdl(stream, version=version)
        stream.end_block()

    def get_byte_length(self, version: int):
        size = 20
        if version > 800:
            size += 80
        for layer in self.layers:
            size += layer.get_byte_length(version)
        return size
