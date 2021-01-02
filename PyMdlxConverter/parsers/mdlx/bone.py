from PyMdlxConverter.common.binarystream import BinaryStream
from PyMdlxConverter.parsers.mdlx.tokenstream import TokenStream
from PyMdlxConverter.parsers.mdlx.genericobject import GenericObject
from PyMdlxConverter.parsers.errors import TokenStreamError


class Bone(GenericObject):

    def __init__(self):
        super().__init__(flags=0x100)
        self.geoset_id = -1
        self.geoset_animation_id = -1

    def read_mdx(self, stream: BinaryStream, version):
        super().read_mdx(stream, version)
        self.geoset_id = stream.read_int32()
        self.geoset_animation_id = stream.read_int32()

    def write_mdx(self, stream: BinaryStream, version):
        super().write_mdx(stream, version)
        stream.write_int32(self.geoset_id)
        stream.write_int32(self.geoset_animation_id)

    def read_mdl(self, stream: TokenStream):
        for token in super().read_generic_block(stream):
            if token == 'GeosetId':
                token = stream.read()
                if token == 'Multiple':
                    self.geoset_id = -1
                else:
                    self.geoset_id = int(token)
            elif token == 'GeosetAnimId':
                token = stream.read()
                if token == 'None':
                    self.geoset_animation_id = -1
                else:
                    self.geoset_animation_id = int(token)
            else:
                raise TokenStreamError('Bone', token, want_name=self.name)

    def write_mdl(self, stream: TokenStream, version=None):
        stream.start_object_block('Bone', self.name)
        self.write_generic_header(stream)
        if self.geoset_id == -1:
            stream.write_flag_attrib('GeosetId', 'Multiple')
        else:
            stream.write_number_attrib('GeosetId', self.geoset_id)
        if self.geoset_animation_id == -1:
            stream.write_flag_attrib('GeosetAnimId', 'None')
        else:
            stream.write_number_attrib('GeosetAnimId', self.geoset_animation_id)
        self.write_generic_animations(stream)
        stream.end_block()

    def get_byte_length(self, version=None):
        return 8 + super().get_byte_length(version=version)