from PyMdlxConverter.common.binarystream import BinaryStream
from PyMdlxConverter.parsers.mdlx.tokenstream import TokenStream
from PyMdlxConverter.parsers.mdlx.genericobject import GenericObject
from PyMdlxConverter.parsers.errors import TokenStreamError


class RibbonEmitter(GenericObject):

    def __init__(self):
        super().__init__(flags=0x4000)
        self.height_above = 0
        self.height_below = 0
        self.alpha = 0
        self.color = 3
        self.lifespan = 0
        self.texture_slot = 0
        self.emission_rate = 0
        self.rows = 0
        self.columns = 0
        self.material_id = 0
        self.gravity = 0

    def read_mdx(self, stream: BinaryStream, version):
        start = stream.index
        size = stream.read_uint32()
        super().read_mdx(stream, version)
        self.height_above = stream.read_float32()
        self.height_below = stream.read_float32()
        self.alpha = stream.read_float32()
        self.color = stream.read_float32_array(3)
        self.lifespan = stream.read_float32()
        self.texture_slot = stream.read_uint32()
        self.emission_rate = stream.read_uint32()
        self.rows = stream.read_uint32()
        self.columns = stream.read_uint32()
        self.material_id = stream.read_int32()
        self.gravity = stream.read_float32()
        self.read_animations(stream, size - (stream.index - start))

    def write_mdx(self, stream: BinaryStream, version):
        stream.write_uint32(self.get_byte_length())
        super().write_mdx(stream, version)
        stream.write_float32(self.height_above)
        stream.write_float32(self.height_below)
        stream.write_float32(self.alpha)
        stream.write_float32_array(self.color)
        stream.write_float32(self.lifespan)
        stream.write_uint32(self.texture_slot)
        stream.write_uint32(self.emission_rate)
        stream.write_uint32(self.rows)
        stream.write_uint32(self.columns)
        stream.write_int32(self.material_id)
        stream.write_float32(self.gravity)
        self.write_non_generic_animation_chunks(stream)

    def read_mdl(self, stream: TokenStream):
        for token in super().read_generic_block(stream):
            if token == 'static HeightAbove':
                self.height_above = stream.read_float()
            elif token == 'HeightAbove':
                self.read_animation(stream, 'KRHA')
            elif token == 'static HeightBelow':
                self.height_below = stream.read_float()
            elif token == 'HeightBelow':
                self.read_animation(stream, 'KRHB')
            elif token == 'static Alpha':
                self.alpha = stream.read_float()
            elif token == 'Alpha':
                self.read_animation(stream, 'KRAL')
            elif token == 'static Color':
                self.color = stream.read_color()
            elif token == 'Color':
                self.read_animation(stream, 'KRCO')
            elif token == 'static TextureSlot':
                self.texture_slot = stream.read_int()
            elif token == 'TextureSlot':
                self.read_animation(stream, 'KRTX')
            elif token == 'Visibility':
                self.read_animation(stream, 'KRVS')
            elif token == 'EmissionRate':
                self.emission_rate = stream.read_int()
            elif token == 'LifeSpan':
                self.lifespan = stream.read_float()
            elif token == 'Gravity':
                self.gravity = stream.read_float()
            elif token == 'Rows':
                self.rows = stream.read_int()
            elif token == 'Columns':
                self.columns = stream.read_int()
            elif token == 'MaterialID':
                self.material_id = stream.read_int()
            else:
                raise TokenStreamError('RibbonEmitter', token)

    def write_mdl(self, stream: TokenStream, version=None):
        stream.start_object_block('RibbonEmitter', self.name)
        self.write_generic_header(stream)
        if not self.write_animation(stream, 'KRHA'):
            stream.write_number_attrib('static HeightAbove', self.height_above)
        if not self.write_animation(stream, 'KRHB'):
            stream.write_number_attrib('static HeightBelow', self.height_below)
        if not self.write_animation(stream, 'KRAL'):
            stream.write_number_attrib('static Alpha', self.alpha)
        if not self.write_animation(stream, 'KRCO'):
            stream.write_color('static Color', self.color)
        if not self.write_animation(stream, 'KRTX'):
            stream.write_number_attrib('static TextureSlot', self.texture_slot)
        self.write_animation(stream, 'KRVS')
        stream.write_number_attrib('EmissionRate', self.emission_rate)
        stream.write_number_attrib('LifeSpan', self.lifespan)
        if self.gravity != 0:
            stream.write_number_attrib('Gravity', self.gravity)
        stream.write_number_attrib('Rows', self.rows)
        stream.write_number_attrib('Columns', self.columns)
        stream.write_number_attrib('MaterialID', self.material_id)
        self.write_generic_animations(stream)
        stream.end_block()

    def get_byte_length(self, version=None):
        return 56 + super().get_byte_length(version=version)