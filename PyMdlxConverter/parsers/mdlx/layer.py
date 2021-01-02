from PyMdlxConverter.common.binarystream import BinaryStream
from PyMdlxConverter.parsers.mdlx.tokenstream import TokenStream
from PyMdlxConverter.parsers.mdlx.animatedobject import AnimatedObject
from PyMdlxConverter.parsers.errors import TokenStreamError

filter_map_mdx = {'None': 0,
              'Transparent': 1,
              'Blend': 2,
              'Additive': 3,
              'AddAlpha': 4,
              'Modulate': 5,
              'Modulate2x': 6}

filter_map_mdl = {value: key for (key, value) in filter_map_mdx.items()}


def filter_mode_to_mdx(val):
    return filter_map_mdx[val]


def filter_mode_to_mdl(val):
    return filter_map_mdl[val]


class Layer(AnimatedObject):

    def __init__(self):
        super().__init__()
        self.filter_mode = 0
        self.flags = 0
        self.texture_id = -1
        self.texture_animation_id = -1
        self.coord_id = 0
        self.alpha = 1
        self.emissive_gain = 1
        self.fresnel_color = [1, 1, 1]
        self.fresnel_opacity = 0
        self.fresnel_team_color = 0

    def read_mdx(self, stream: BinaryStream, version: int):
        start = stream.index
        size = stream.read_uint32()
        self.filter_mode = stream.read_uint32()
        self.flags = stream.read_uint32()
        self.texture_id = stream.read_int32()
        self.texture_animation_id = stream.read_int32()
        self.coord_id = stream.read_uint32()
        self.alpha = stream.read_float32()
        if version > 800:
            self.emissive_gain = stream.read_float32()
            self.fresnel_color = stream.read_float32_array(3)
            self.fresnel_opacity = stream.read_float32()
            self.fresnel_team_color = stream.read_float32()
        self.read_animations(stream, size - (stream.index - start))

    def write_mdx(self, stream: BinaryStream, version):
        stream.write_uint32(self.get_byte_length(version))
        stream.write_uint32(self.filter_mode)
        stream.write_uint32(self.flags)
        stream.write_int32(self.texture_id)
        stream.write_int32(self.texture_animation_id)
        stream.write_uint32(self.coord_id)
        stream.write_float32(self.alpha)
        if version > 800:
            stream.write_float32(self.emissive_gain)
            stream.write_float32_array(self.fresnel_color)
            stream.write_float32(self.fresnel_opacity)
            stream.write_float32(self.fresnel_team_color)
        self.write_animations(stream)

    def read_mdl(self, stream: TokenStream):
        for token in super().read_animated_block(stream):
            if token == 'FilterMode':
                self.filter_mode = filter_mode_to_mdx(stream.read())
            elif token == 'Unshaded':
                self.flags |= 0x1
            elif token == 'SphereEnvMap':
                self.flags |= 0x2
            elif token == 'TwoSided':
                self.flags |= 0x10
            elif token == 'Unfogged':
                self.flags |= 0x20
            elif token == 'NoDepthTest':
                self.flags |= 0x40
            elif token == 'NoDepthSet':
                self.flags |= 0x80
            elif token == 'Unlit':
                self.flags |= 0x100
            elif token == 'static TextureID':
                self.texture_id = stream.read_int()
            elif token == 'TextureID':
                self.read_animation(stream, 'KMTF')
            elif token == 'TVertexAnimId':
                self.texture_animation_id = stream.read_int()
            elif token == 'CoordId':
                self.coord_id = stream.read_int()
            elif token == 'static Alpha':
                self.alpha = stream.read_float()
            elif token == 'Alpha':
                self.read_animation(stream, 'KMTA')
            elif token == 'static EmissiveGain':
                self.emissive_gain = stream.read_float()
            elif token == 'EmissiveGain':
                self.read_animation(stream, 'KMTE')
            elif token == 'static FresnelColor':
                self.fresnel_color = stream.read_vector(3)
            elif token == 'FresnelColor':
                self.read_animation(stream, 'KFC3')
            elif token == 'static FresnelOpacity':
                self.fresnel_opacity = stream.read_float()
            elif token == 'FresnelOpacity':
                self.read_animation(stream, 'KFCA')
            elif token == 'static FresnelTeamColor':
                self.fresnel_team_color = stream.read_float()
            elif token == 'FresnelTeamColor':
                self.read_animation(stream, 'KFTC')
            else:
                raise TokenStreamError('Layer', token)

    def write_mdl(self, stream: TokenStream, version=None):
        stream.start_block('Layer', None)  # headers ??
        stream.write_flag_attrib('FilterMode', filter_mode_to_mdl(self.filter_mode))
        if self.flags & 0x1:
            stream.write_flag('Unshaded')
        if self.flags & 0x2:
            stream.write_flag('SphereEnvMap')
        if self.flags & 0x10:
            stream.write_flag('TwoSided')
        if self.flags & 0x20:
            stream.write_flag('Unfogged')
        if self.flags & 0x40:
            stream.write_flag('NoDepthTest')
        if self.flags & 0x80:
            stream.write_flag('NoDepthSet')
        if version > 800:
            if self.flags & 0x100:
                stream.write_flag('Unlit')
        if not self.write_animation(stream, 'KMTF'):
            stream.write_number_attrib('static TextureID', self.texture_id)
        if self.texture_animation_id != -1:
            stream.write_number_attrib('TVertexAnimId', self.texture_animation_id)
        if self.coord_id != 0:
            stream.write_number_attrib('CoordId', self.coord_id)
        if not self.write_animation(stream, 'KMTA') and self.alpha != 1:
            stream.write_number_attrib('static Alpha', self.alpha)
        if version > 800:
            if not self.write_animation(stream, 'KMTE') and self.emissive_gain != 1:
                stream.write_number_attrib('static EmissiveGain', self.emissive_gain)
            if not self.write_animation(stream, 'KFC3') and (self.fresnel_color[0] != 1 or self.fresnel_color[1] != 1
            or self.fresnel_color[2] != 1):
                stream.write_vector_attrib('static FresnelColor', self.fresnel_color)
            if not self.write_animation(stream, 'KFCA') and self.fresnel_opacity != 0:
                stream.write_number_attrib('static FresnelOpacity', self.fresnel_opacity)
            if not self.write_animation(stream, 'KFTC') and self.fresnel_team_color != 0:
                stream.write_number_attrib('static FresnelTeamColor', self.fresnel_team_color)
        stream.end_block()

    def get_byte_length(self, version=None):
        size = 28 + super().get_byte_length(version=version)
        if version > 800:
            size += 24
        return size
