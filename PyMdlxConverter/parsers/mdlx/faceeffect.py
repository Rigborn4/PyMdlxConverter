from PyMdlxConverter.common.binarystream import BinaryStream
from PyMdlxConverter.parsers.mdlx.tokenstream import TokenStream
from PyMdlxConverter.parsers.errors import TokenStreamError


class FaceEffect(object):

    def __init__(self):
        self.type = ''
        self.path = ''

    def read_mdx(self, stream: BinaryStream):
        self.type = stream.read(80)
        self.path = stream.read(260)

    def write_mdx(self, stream: BinaryStream):
        stream.write(self.type)
        stream.skip(80 - len(self.type))
        stream.write(self.path)
        stream.skip(260 - len(self.path))

    def read_mdl(self, stream: TokenStream, version=None):
        self.type = stream.read()
        for token in stream.read_block():
            if token == 'Path':
                self.path = stream.read()
            else:
                raise TokenStreamError('FaceEffect', token)

    def write_mdl(self, stream: TokenStream, version=None):
        stream.start_object_block('FaceFX', self.type)
        stream.write_string_attrib('Path', self.path)
        stream.end_block()