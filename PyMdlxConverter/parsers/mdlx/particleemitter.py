from PyMdlxConverter.common.binarystream import BinaryStream
from PyMdlxConverter.parsers.mdlx.tokenstream import TokenStream
from PyMdlxConverter.parsers.mdlx.genericobject import GenericObject
from PyMdlxConverter.parsers.errors import TokenStreamError


class ParticleEmitter(GenericObject):

    def __init__(self):
        super().__init__(flags=0x1000)
        self.emission_rate = 0
        self.gravity = 0
        self.longitude = 0
        self.latitude = 0
        self.path = ''
        self.life_span = 0
        self.speed = 0

    def read_mdx(self, stream: BinaryStream, version):
        start = stream.index
        size = stream.read_uint32()
        super().read_mdx(stream, version)
        self.emission_rate = stream.read_float32()
        self.gravity = stream.read_float32()
        self.longitude = stream.read_float32()
        self.latitude = stream.read_float32()
        self.path = stream.read(260)
        self.life_span = stream.read_float32()
        self.speed = stream.read_float32()
        self.read_animations(stream, size - (stream.index - start))

    def write_mdx(self, stream: BinaryStream, version):
        stream.write_int32(self.get_byte_length())
        super().write_mdx(stream, version)
        stream.write_float32(self.emission_rate)
        stream.write_float32(self.gravity)
        stream.write_float32(self.longitude)
        stream.write_float32(self.latitude)
        stream.write(self.path)
        stream.skip(260 - len(self.path))
        stream.write_float32(self.life_span)
        stream.write_float32(self.speed)
        self.write_non_generic_animation_chunks(stream)

    def read_mdl(self, stream: TokenStream, version=None):
        for token in super().read_generic_block(stream):
            if token == 'EmitterUsesMDL':
                self.flags |= 0x8000
            elif token == 'EmitterUsesTGA':
                self.flags |= 0x10000
            elif token == 'static EmissionRate':
                self.emission_rate = stream.read_float()
            elif token == 'EmissionRate':
                self.read_animation(stream, 'KPEE')
            elif token == 'static Gravity':
                self.gravity = stream.read_float()
            elif token == 'Gravity':
                self.read_animation(stream, 'KPEG')
            elif token == 'static Longitude':
                self.longitude = stream.read_float()
            elif token == 'Longitude':
                self.read_animation(stream, 'KPLN')
            elif token == 'static Latitude':
                self.latitude = stream.read_float()
            elif token == 'Latitude':
                self.read_animation(stream, 'KPLT')
            elif token == 'Visibility':
                self.read_animation(stream, 'KPEV')
            elif token == 'Particle':
                for token in self.read_animated_block(stream):
                    if token == 'static LifeSpan':
                        self.life_span = stream.read_float()
                    elif token == 'LifeSpan':
                        self.read_animation(stream, 'KPEL')
                    elif token == 'static InitVelocity':
                        self.speed = stream.read_float()
                    elif token == 'InitVelocity':
                        self.read_animation(stream, 'KPES')
                    elif token == 'Path':
                        self.path = stream.read()
            else:
                raise TokenStreamError('ParticleEmitter', token)

    def write_mdl(self, stream: TokenStream, version=None):
        stream.start_object_block('ParticleEmitter', self.name)
        self.write_generic_header(stream)
        if self.flags & 0x8000:
            stream.write_flag('EmitterUsesMDL')
        if self.flags & 0x10000:
            stream.write_flag('EmitterUsesTGA')
        if not self.write_animation(stream, 'KPEE'):
            stream.write_number_attrib('static EmissionRate', self.emission_rate)
        if not self.write_animation(stream, 'KPEG'):
            stream.write_number_attrib('static Gravity', self.gravity)
        if not self.write_animation(stream, 'KPLN'):
            stream.write_number_attrib('static Longitude', self.longitude)
        if not self.write_animation(stream, 'KPLT'):
            stream.write_number_attrib('static Latitude', self.latitude)
        self.write_animation(stream, 'KPEV')
        stream.start_block('Particle', None)
        if not self.write_animation(stream, 'KPEL'):
            stream.write_number_attrib('static LifeSpan', self.life_span)
        if not self.write_animation(stream, 'KPES'):
            stream.write_number_attrib('static InitVelocity', self.speed)
        if ((self.flags & 0x8000) or (self.flags & 0x10000)):
            stream.write_string_attrib('Path', self.path)
        stream.end_block()
        self.write_generic_animations(stream)
        stream.end_block()

    def get_byte_length(self, version=None):
        return 288 + super().get_byte_length(version=version)