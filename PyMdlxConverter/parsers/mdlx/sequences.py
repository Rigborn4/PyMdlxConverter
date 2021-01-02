from PyMdlxConverter.common.binarystream import BinaryStream
from PyMdlxConverter.parsers.mdlx.tokenstream import TokenStream
from PyMdlxConverter.parsers.mdlx.extent import Extent
from PyMdlxConverter.parsers.errors import TokenStreamError


class Sequence(object):

    def __init__(self):
        self.name = ''
        self.interval = [0, 0]
        self.move_speed = 0
        self.flags = 0
        self.rarity = 0
        self.sync_point = 0
        self.extent = Extent()

    def read_mdx(self, stream: BinaryStream):
        self.name = stream.read(80)
        self.interval = stream.read_uint32_array(2)
        self.move_speed = stream.read_float32()
        self.flags = stream.read_uint32()
        self.rarity = stream.read_float32()
        self.sync_point = stream.read_uint32()
        self.extent.read_mdx(stream)

    def write_mdx(self, stream: BinaryStream):
        stream.write(self.name)
        stream.skip(80 - len(self.name))
        stream.write_uint32_array(self.interval)
        stream.write_float32(self.move_speed)
        stream.write_uint32(self.flags)
        stream.write_float32(self.rarity)
        stream.write_uint32(self.sync_point)
        self.extent.write_mdx(stream)

    def read_mdl(self, stream: TokenStream):
        self.name = stream.read()
        for token in stream.read_block():
            if token == 'Interval':
                self.interval = stream.read_vector(2)
            elif token == 'NonLooping':
                self.flags = 1
            elif token == 'MoveSpeed':
                self.move_speed = stream.read_float()
            elif token == 'Rarity':
                self.rarity = stream.read_float()
            elif token == 'MinimumExtent':
                self.extent.min = stream.read_vector(3)
            elif token == 'MaximumExtent':
                self.extent.max = stream.read_vector(3)
            elif token == 'BoundsRadius':
                self.extent.bounds_radius = stream.read_float()
            else:
                raise TokenStreamError('Sequence', token)

    def write_mdl(self, stream: TokenStream, version=None):
        stream.start_object_block('Anim', self.name)
        stream.write_vector_attrib('Interval', self.interval)
        if self.flags == 1:
            stream.write_flag('NonLooping')
        if self.move_speed != 0:
            stream.write_number_attrib('MoveSpeed', self.move_speed)
        if self.rarity != 0:
            stream.write_number_attrib('Rarity', self.rarity)
        self.extent.write_mdl(stream)
        stream.end_block()
