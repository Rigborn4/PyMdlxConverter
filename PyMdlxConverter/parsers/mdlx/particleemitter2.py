from PyMdlxConverter.common.binarystream import BinaryStream
from PyMdlxConverter.parsers.mdlx.tokenstream import TokenStream
from PyMdlxConverter.parsers.mdlx.genericobject import GenericObject
from PyMdlxConverter.parsers.errors import TokenStreamError


class ParticleEmitter2(GenericObject):

    def __init__(self):
        super().__init__() # can't call parent init because particleemitter2 has no flag tag. At least not that I know of
        self.speed = 0
        self.variation = 0
        self.latitude = 0
        self.gravity = 0
        self.life_span = 0
        self.emission_rate = 0
        self.width = 0
        self.length = 0
        self.filter_mode = 0
        self.rows = 0
        self.columns = 0
        self.head_or_tail = 0
        self.tail_length = 0
        self.time_middle = 0
        self.segment_colors = [[], [], []]  #  read 3 by 3 float array
        self.segment_alphas = [] #3
        self.segment_scaling = [] #3
        self.head_intervals = [[], []]  # read 2 by 3 float array
        self.tail_intervals = [[], []]  # read 2 by 3 float array
        self.texture_id = -1
        self.squirt = 0
        self.priority_plane = 0
        self.replaceable_id = 0

    def read_mdx(self, stream: BinaryStream, version):
        start = stream.index
        size = stream.read_uint32()
        super().read_mdx(stream, version)
        self.speed = stream.read_float32()
        self.variation = stream.read_float32()
        self.latitude = stream.read_float32()
        self.gravity = stream.read_float32()
        self.life_span = stream.read_float32()
        self.emission_rate = stream.read_float32()
        self.width = stream.read_float32()
        self.length = stream.read_float32()
        self.filter_mode = stream.read_uint32()
        self.rows = stream.read_uint32()
        self.columns = stream.read_uint32()
        self.head_or_tail = stream.read_uint32()
        self.tail_length = stream.read_float32()
        self.time_middle = stream.read_float32()
        self.segment_colors[0] = stream.read_float32_array(3)
        self.segment_colors[1] = stream.read_float32_array(3)
        self.segment_colors[2] = stream.read_float32_array(3)
        self.segment_alphas = stream.read_uint8_array(3)
        self.segment_scaling = stream.read_float32_array(3)
        self.head_intervals[0] = stream.read_uint32_array(3)
        self.head_intervals[1] = stream.read_uint32_array(3)
        self.tail_intervals[0] = stream.read_uint32_array(3)
        self.tail_intervals[1] = stream.read_uint32_array(3)
        self.texture_id = stream.read_int32()
        self.squirt = stream.read_uint32()
        self.priority_plane = stream.read_int32()
        self.replaceable_id = stream.read_uint32()
        self.read_animations(stream, size - (stream.index - start))

    def write_mdx(self, stream: BinaryStream, version):
        stream.write_uint32(self.get_byte_length())
        super().write_mdx(stream, version)
        stream.write_float32(self.speed)
        stream.write_float32(self.variation)
        stream.write_float32(self.latitude)
        stream.write_float32(self.gravity)
        stream.write_float32(self.life_span)
        stream.write_float32(self.emission_rate)
        stream.write_float32(self.width)
        stream.write_float32(self.length)
        stream.write_uint32(self.filter_mode)
        stream.write_uint32(self.rows)
        stream.write_uint32(self.columns)
        stream.write_uint32(self.head_or_tail)
        stream.write_float32(self.tail_length)
        stream.write_float32(self.time_middle)
        stream.write_float32_array(self.segment_colors[0])
        stream.write_float32_array(self.segment_colors[1])
        stream.write_float32_array(self.segment_colors[2])
        stream.write_uint8_array(self.segment_alphas)
        stream.write_float32_array(self.segment_scaling)
        stream.write_uint32_array(self.head_intervals[0])
        stream.write_uint32_array(self.head_intervals[1])
        stream.write_uint32_array(self.tail_intervals[0])
        stream.write_uint32_array(self.tail_intervals[1])
        stream.write_int32(self.texture_id)
        stream.write_uint32(self.squirt)
        stream.write_int32(self.priority_plane)
        stream.write_uint32(self.replaceable_id)
        self.write_non_generic_animation_chunks(stream)

    def read_mdl(self, stream: TokenStream):
        for token in super().read_generic_block(stream):
            if token == 'SortPrimsFarZ':
                self.flags |= 0x10000
            elif token == 'Unshaded':
                self.flags |= 0x8000
            elif token == 'LineEmitter':
                self.flags |= 0x20000
            elif token == 'Unfogged':
                self.flags |= 0x40000
            elif token == 'ModelSpace':
                self.flags |= 0x80000
            elif token == 'XYQuad':
                self.flags |= 0x100000
            elif token == 'static Speed':
                self.speed = stream.read_float()
            elif token == 'Speed':
                self.read_animation(stream, 'KP2S')
            elif token == 'static Variation':
                self.variation = stream.read_float()
            elif token == 'Variation':
                self.read_animation(stream, 'KP2R')
            elif token == 'static Latitude':
                self.latitude = stream.read_float()
            elif token == 'Latitude':
                self.read_animation(stream, 'KP2L')
            elif token == 'static Gravity':
                self.gravity = stream.read_float()
            elif token == 'Gravity':
                self.read_animation(stream, 'KP2G')
            elif token == 'Visibility':
                self.read_animation(stream, 'KP2V')
            elif token == 'Squirt':
                self.squirt = 1
            elif token == 'LifeSpan':
                self.life_span = stream.read_float()
            elif token == 'static EmissionRate':
                self.emission_rate = stream.read_float()
            elif token == 'EmissionRate':
                self.read_animation(stream, 'KP2E')
            elif token == 'static Width':
                self.width = stream.read_float()
            elif token == 'Width':
                self.read_animation(stream, 'KP2N')
            elif token == 'static Length':
                self.length = stream.read_float()
            elif token == 'Length':
                self.read_animation(stream, 'KP2W')
            elif token == 'Blend':
                self.filter_mode = 0
            elif token == 'Additive':
                self.filter_mode = 1
            elif token == 'Modulate':
                self.filter_mode = 2
            elif token == 'Modulate2x':
                self.filter_mode = 3
            elif token == 'AlphaKey':
                self.filter_mode = 4
            elif token == 'Rows':
                self.rows = stream.read_int()
            elif token == 'Columns':
                self.columns = stream.read_int()
            elif token == 'Head':
                self.head_or_tail = 0
            elif token == 'Tail':
                self.head_or_tail = 1
            elif token == 'Both':
                self.head_or_tail = 2
            elif token == 'TailLength':
                self.tail_length = stream.read_float()
            elif token == 'Time':
                self.time_middle = stream.read_float()
            elif token == 'SegmentColor':
                stream.read()
                for i in range(3):
                    stream.read()
                    self.segment_colors[i] = stream.read_color()
                stream.read()
            elif token == 'Alpha':
                self.segment_alphas = stream.read_vector(3)
            elif token == 'ParticleScaling':
                self.segment_scaling = stream.read_vector(3)
            elif token == 'LifeSpanUVAnim':
                self.head_intervals[0] = stream.read_vector(3)
            elif token == 'DecayUVAnim':
                self.head_intervals[1] = stream.read_vector(3)
            elif token == 'TailUVAnim':
                self.tail_intervals[0] = stream.read_vector(3)
            elif token == 'TailDecayUVAnim':
                self.tail_intervals[1] = stream.read_vector(3)
            elif token == 'TextureID':
                self.texture_id = stream.read_int()
            elif token == 'ReplaceableId':
                self.replaceable_id = stream.read_int()
            elif token == 'PriorityPlane':
                self.priority_plane = stream.read_int()
            else:
                raise TokenStreamError('ParticleEmitter2', token)

    def write_mdl(self, stream: TokenStream, version=None):
        stream.start_object_block('ParticleEmitter2', self.name)
        self.write_generic_header(stream)
        if self.flags & 0x10000:
            stream.write_flag('SortPrimsFarZ')
        if self.flags & 0x8000:
            stream.write_flag('Unshaded')
        if self.flags & 0x20000:
            stream.write_flag('LineEmitter')
        if self.flags & 0x40000:
            stream.write_flag('Unfogged')
        if self.flags & 0x80000:
            stream.write_flag('ModelSpace')
        if self.flags & 0x100000:
            stream.write_flag('XYQuad')
        if not self.write_animation(stream, 'KP2S'):
            stream.write_number_attrib('static Speed', self.speed)
        if not self.write_animation(stream, 'KP2R'):
            stream.write_number_attrib('static Variation', self.variation)
        if not self.write_animation(stream, 'KP2L'):
            stream.write_number_attrib('static Latitude', self.latitude)
        if not self.write_animation(stream, 'KP2G'):
            stream.write_number_attrib('static Gravity', self.gravity)
        self.write_animation(stream, 'KP2V')
        if self.squirt:
            stream.write_flag('Squirt')
        stream.write_number_attrib('LifeSpan', self.life_span)
        if not self.write_animation(stream, 'KP2E'):
            stream.write_number_attrib('static EmissionRate', self.emission_rate)
        if not self.write_animation(stream, 'KP2N'):
            stream.write_number_attrib('static Width', self.width)
        if not self.write_animation(stream, 'KP2W'):
            stream.write_number_attrib('static Length', self.length)
        if self.filter_mode == 0:
            stream.write_flag('Blend')
        elif self.filter_mode == 1:
            stream.write_flag('Additive')
        elif self.filter_mode == 2:
            stream.write_flag('Modulate')
        elif self.filter_mode == 3:
            stream.write_flag('Modulate2x')
        elif self.filter_mode == 4:
            stream.write_flag('AlphaKey')
        stream.write_number_attrib('Rows', self.rows)
        stream.write_number_attrib('Columns', self.columns)
        if self.head_or_tail == 0:
            stream.write_flag('Head')
        elif self.head_or_tail == 1:
            stream.write_flag('Tail')
        elif self.head_or_tail == 2:
            stream.write_flag('Both')
        stream.write_number_attrib('TailLength', self.tail_length)
        stream.write_number_attrib('Time', self.time_middle)
        stream.start_block('SegmentColor', None)
        stream.write_color('Color', self.segment_colors[0])
        stream.write_color('Color', self.segment_colors[1])
        stream.write_color('Color', self.segment_colors[2])
        stream.end_block_comma()
        stream.write_vector_attrib('Alpha', self.segment_alphas)
        stream.write_vector_attrib('ParticleScaling', self.segment_scaling)
        stream.write_vector_attrib('LifeSpanUVAnim', self.head_intervals[0])
        stream.write_vector_attrib('DecayUVAnim', self.head_intervals[1])
        stream.write_vector_attrib('TailUVAnim', self.tail_intervals[0])
        stream.write_vector_attrib('TailDecayUVAnim', self.tail_intervals[1])
        stream.write_number_attrib('TextureID', self.texture_id)
        if self.replaceable_id != 0:
            stream.write_number_attrib('ReplaceableId', self.replaceable_id)
        if self.priority_plane != 0:
            stream.write_number_attrib('PriorityPlane', self.priority_plane)
        self.write_generic_animations(stream)
        stream.end_block()

    def get_byte_length(self, version=None):
        return 175 + super().get_byte_length(version=version)
