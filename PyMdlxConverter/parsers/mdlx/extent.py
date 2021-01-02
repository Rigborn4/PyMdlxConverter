from PyMdlxConverter.common.binarystream import BinaryStream
from PyMdlxConverter.parsers.mdlx.tokenstream import TokenStream


class Extent(object):

    def __init__(self):
        self.bounds_radius = 0
        self.min = [0, 0, 0]
        self.max = [0, 0, 0]

    def read_mdx(self, stream: BinaryStream):
        self.bounds_radius = stream.read_float32()
        self.min = stream.read_float32_array(3)
        self.max = stream.read_float32_array(3)

    def write_mdx(self, stream: BinaryStream):
        stream.write_float32(self.bounds_radius)
        stream.write_float32_array(self.min)
        stream.write_float32_array(self.max)

    def write_mdl(self, stream: TokenStream, version=None):
        if self.min[0] != 0 or self.min[1] != 0 or self.min[2] != 0:
            stream.write_vector_attrib('MinimumExtent', self.min)
        if self.max[0] != 0 or self.max[1] != 0 or self.max[2] != 0:
            stream.write_vector_attrib('MaximumExtent', self.max)
        if self.bounds_radius != 0:
            stream.write_number_attrib('BoundsRadius', self.bounds_radius)