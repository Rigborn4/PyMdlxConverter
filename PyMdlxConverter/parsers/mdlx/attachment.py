from PyMdlxConverter.common.binarystream import BinaryStream
from PyMdlxConverter.parsers.mdlx.tokenstream import TokenStream
from PyMdlxConverter.parsers.mdlx.genericobject import GenericObject
from PyMdlxConverter.parsers.errors import TokenStreamError


class Attachment(GenericObject):

    def __init__(self):
        super().__init__(flags=0x800)
        self.path = ''
        self.attachment_id = 0

    def read_mdx(self, stream: BinaryStream, version):
        start = stream.index
        size = stream.read_uint32()
        super().read_mdx(stream, version)
        self.path = stream.read(260)
        self.attachment_id = stream.read_int32()
        self.read_animations(stream, size - (stream.index - start))

    def write_mdx(self, stream: BinaryStream, version):
        stream.write_uint32(self.get_byte_length())
        super().write_mdx(stream, version)
        stream.write(self.path)
        stream.skip(260 - len(self.path))
        stream.write_int32(self.attachment_id)
        self.write_non_generic_animation_chunks(stream)

    def read_mdl(self, stream: TokenStream):
        for token in super().read_generic_block(stream):
            if token == 'AttachmentID':
                self.attachment_id = stream.read_int()
            elif token == 'Path':
                self.path = stream.read()
            elif token == 'Visibility':
                self.read_animation(stream, 'KATV')
            else:
                raise TokenStreamError('Attachment', token, want_name=self.name)

    def write_mdl(self, stream: TokenStream, version=None):
        stream.start_object_block('Attachment', self.name)
        self.write_generic_header(stream)
        stream.write_number_attrib('AttachmentID', self.attachment_id)
        if len(self.path):
            stream.write_string_attrib('Path', self.path)
        self.write_animation(stream, 'KATV')
        self.write_generic_animations(stream)
        stream.end_block()

    def get_byte_length(self, version=None):
        return 268 + super().get_byte_length(version=version)
