from PyMdlxConverter.common.binarystream import BinaryStream
from PyMdlxConverter.parsers.mdlx.tokenstream import TokenStream
from PyMdlxConverter.parsers.mdlx.genericobject import GenericObject
from PyMdlxConverter.parsers.errors import TokenStreamError


class EventObject(GenericObject):

    def __init__(self):
        super().__init__(flags=0x400)
        self.global_sequence_id = -1
        self.tracks = []

    def read_mdx(self, stream: BinaryStream, version):
        super().read_mdx(stream, version)
        stream.skip(4)  # KEVT TAG
        count = stream.read_uint32()
        self.global_sequence_id = stream.read_int32()
        self.tracks = stream.read_uint32_array(count)

    def write_mdx(self, stream: BinaryStream, version):
        super().write_mdx(stream, version)
        stream.write('KEVT')
        stream.write_uint32(len(self.tracks))
        stream.write_int32(self.global_sequence_id)
        stream.write_uint32_array(self.tracks)

    def read_mdl(self, stream: TokenStream):
        for token in super().read_generic_block(stream):
            if token == 'EventTrack':
                count = stream.read_int()
                stream.read()
                if stream.peek() == 'GlobalSeqId':
                    stream.read()
                    self.global_sequence_id = stream.read_int()
                for i in range(count):
                    self.tracks.append(stream.read_int())
                stream.read()
            else:
                raise TokenStreamError('EventObject', token)

    def write_mdl(self, stream: TokenStream, version=None):
        stream.start_object_block('EventObject', self.name)
        self.write_generic_header(stream)
        stream.start_block('EventTrack', len(self.tracks))
        if self.global_sequence_id != -1:
            stream.write_number_attrib('GlobalSeqId', self.global_sequence_id)
        for track in self.tracks:
            stream.write_flag(f'{track}')
        stream.end_block()
        self.write_generic_animations(stream)
        stream.end_block()

    def get_byte_length(self, version=None):
        return 12 + (len(self.tracks) * 1) + super().get_byte_length(version=version)