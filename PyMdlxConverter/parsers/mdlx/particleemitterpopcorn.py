from PyMdlxConverter.common.binarystream import BinaryStream
from PyMdlxConverter.parsers.mdlx.tokenstream import TokenStream
from PyMdlxConverter.parsers.mdlx.genericobject import GenericObject
from PyMdlxConverter.parsers.errors import TokenStreamError


class ParticleEmitterPopcorn(GenericObject):

    def __init__(self):
        super().__init__()
        self.life_span = 0
        self.emission_rate = 0
        self.speed = 0
        self.color = 3
        self.alpha = 1
        self.replaceable_id = 0
        self.path = ''
        self.animation_visibility_guide = ''

    def read_mdx(self, stream: BinaryStream, version):
        start = stream.index
        size = stream.read_uint32()
        super().read_mdx(stream, version)
        self.life_span = stream.read_float32()
        self.emission_rate = stream.read_float32()
        self.speed = stream.read_float32()
        self.color = stream.read_float32_array(3)
        self.alpha = stream.read_float32()
        self.replaceable_id = stream.read_uint32()
        self.path = stream.read(260)
        self.animation_visibility_guide = stream.read(260)
        self.read_animations(stream, size - (stream.index - start))

    def write_mdx(self, stream: BinaryStream, version):
        stream.write_uint32(self.get_byte_length())
        super().write_mdx(stream, version)
        stream.write_float32(self.life_span)
        stream.write_float32(self.emission_rate)
        stream.write_float32(self.speed)
        stream.write_float32_array(self.color)
        stream.write_float32(self.alpha)
        stream.write_uint32(self.replaceable_id)
        stream.write(self.path)
        stream.skip(260 - len(self.path))
        stream.write(self.animation_visibility_guide)
        stream.skip(260 - len(self.animation_visibility_guide))
        self.write_non_generic_animation_chunks(stream)

    def read_mdl(self, stream: TokenStream):
        for token in super().read_generic_block(stream):
            if token == 'SortPrimsFarZ':
                self.flags |= 0x10000
            elif token == 'Unshaded':
                self.flags |= 0x8000
            elif token == 'Unfogged':
                self.flags |= 0x40000
            elif token == 'static LifeSpan':
                self.life_span = stream.read_float()
            elif token == 'LifeSpan':
                self.read_animation(stream, 'KPPL')
            elif token == 'static EmissionRate':
                self.emission_rate = stream.read_float()
            elif token == 'EmissionRate':
                self.read_animation(stream, 'KPPE')
            elif token == 'static Speed':
                self.speed = stream.read_float()
            elif token == 'Speed':
                self.read_animation(stream, 'KPPS')
            elif token == 'static Color':
                self.color = stream.read_vector(3)
            elif token == 'Color':
                self.read_animation(stream, 'KPPC')
            elif token == 'static Alpha':
                self.alpha = stream.read_float()
            elif token == 'Alpha':
                self.read_animation(stream, 'KPPA')
            elif token == 'Visibility':
                self.read_animation(stream, 'KPPV')
            elif token == 'ReplaceableId':
                self.replaceable_id = stream.read_int()
            elif token == 'Path':
                self.path = stream.read()
            elif token == 'AnimVisibilityGuide':
                self.animation_visibility_guide = stream.read()
            else:
                raise TokenStreamError('ParticleEmitterPopcorn', token)

    def write_mdl(self, stream: TokenStream, version=None):
        stream.start_object_block('ParticleEmitterPopcorn', self.name)
        self.write_generic_header(stream)
        if self.flags & 0x10000:
            stream.write_flag('SortPrimsFarZ')
        if self.flags & 0x8000:
            stream.write_flag('Unshaded')
        if self.flags & 0x40000:
            stream.write_flag('Unfogged')
        if not self.write_animation(stream, 'KPPL'):
            stream.write_number_attrib('static LifeSpan', self.life_span)
        if not self.write_animation(stream, 'KPPE'):
            stream.write_number_attrib('static EmissionRate', self.emission_rate)
        if not self.write_animation(stream, 'KPPS'):
            stream.write_number_attrib('static Speed', self.speed)
        if not self.write_animation(stream, 'KPPC'):
            stream.write_vector_attrib('static Color', self.color)
        if not self.write_animation(stream, 'KPPA'):
            stream.write_number_attrib('static Alpha', self.alpha)
        self.write_animation(stream, 'KPPV')
        if self.replaceable_id != 0:
            stream.write_number_attrib('ReplaceableId', self.replaceable_id)
        if len(self.path):
            stream.write_string_attrib('Path', self.path)
        if len(self.animation_visibility_guide):
            stream.write_string_attrib('AnimVisibilityGuide', self.animation_visibility_guide)
        self.write_generic_animations(stream)
        stream.end_block()

    def get_byte_length(self, version=None):
        return 556 + super().get_byte_length(version=version)
