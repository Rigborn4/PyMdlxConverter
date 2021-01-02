from PyMdlxConverter.common.binarystream import BinaryStream
from PyMdlxConverter.parsers.mdlx.tokenstream import TokenStream
from PyMdlxConverter.parsers.mdlx.genericobject import GenericObject
from PyMdlxConverter.parsers.errors import TokenStreamError


class Light(GenericObject):

    def __init__(self):
        super().__init__(flags=0x200)
        self.type = -1
        self.attenuation = [0, 0]
        self.color = 3
        self.intensity = 0
        self.ambient_color = 3
        self.ambient_intensity = 0

    def read_mdx(self, stream: BinaryStream, version):
        start = stream.index
        size = stream.read_uint32()
        super().read_mdx(stream, version)
        self.type = stream.read_uint32()
        self.attenuation = stream.read_float32_array(2)
        self.color = stream.read_float32_array(3)
        self.intensity = stream.read_float32()
        self.ambient_color = stream.read_float32_array(3)
        self.ambient_intensity = stream.read_float32()
        self.read_animations(stream, size - (stream.index - start))

    def write_mdx(self, stream: BinaryStream, version):
        stream.write_uint32(self.get_byte_length())
        super().write_mdx(stream, version)
        stream.write_uint32(self.name)
        stream.write_float32_array(self.attenuation)
        stream.write_float32_array(self.color)
        stream.write_float32(self.intensity)
        stream.write_float32_array(self.ambient_color)
        stream.write_float32(self.ambient_intensity)
        self.write_non_generic_animation_chunks(stream)

    def read_mdl(self, stream: TokenStream):
        for token in super().read_generic_block(stream):
            if token == 'Omnidirectional':
                self.type = 0
            elif token == 'Directional':
                self.type = 1
            elif token == 'Ambient':
                self.type = 2
            elif token == 'static AttenuationStart':
                self.attenuation[0] = stream.read_float()
            elif token == 'AttenuationStart':
                self.read_animation(stream, 'KLAS')
            elif token == 'static AttenuationEnd':
                self.attenuation[1] = stream.read_float()
            elif token == 'AttenuationEnd':
                self.read_animation(stream, 'KLAE')
            elif token == 'static Intensity':
                self.intensity = stream.read_float()
            elif token == 'Intensity':
                self.read_animation(stream, 'KLAI')
            elif token == 'static Color':
                self.color = stream.read_color()
            elif token == 'Color':
                self.read_animation(stream, 'KLAC')
            elif token == 'static AmbIntensity':
                self.ambient_intensity = stream.read_float()
            elif token == 'AmbIntensity':
                self.read_animation(stream, 'KLBI')
            elif token == 'static AmbColor':
                self.ambient_color = stream.read_color()
            elif token == 'AmbColor':
                self.read_animation(stream, 'KLBC')
            elif token == 'Visibility':
                self.read_animation(stream, 'KLAV')
            else:
                raise TokenStreamError('Light', token)

    def write_mdl(self, stream: TokenStream, version=None):
        stream.start_object_block('Light', self.name)
        self.write_generic_header(stream)
        if self.type == 0:
            stream.write_flag('Omnidirectional')
        elif self.type == 1:
            stream.write_flag('Directional')
        elif self.type == 2:
            stream.write_flag('Ambient')
        if not self.write_animation(stream, 'KLAS'):
            stream.write_number_attrib('static AttenuationStart', self.attenuation[0])
        if not self.write_animation(stream, 'KLAE'):
            stream.write_number_attrib('static AttenuationEnd', self.attenuation[1])
        if not self.write_animation(stream, 'KLAI'):
            stream.write_number_attrib('static Intensity', self.intensity)
        if not self.write_animation(stream, 'KLAC'):
            stream.write_color('static Color', self.color)
        if not self.write_animation(stream, 'KLBI'):
            stream.write_number_attrib('static AmbIntensity', self.ambient_intensity)
        if not self.write_animation(stream, 'KLBC'):
            stream.write_color('static AmbColor', self.ambient_color)
        self.write_animation(stream, 'KLAV')
        self.write_generic_animations(stream)
        stream.end_block()

    def get_byte_length(self, version=None):
        return 48 + super().get_byte_length(version=version)
