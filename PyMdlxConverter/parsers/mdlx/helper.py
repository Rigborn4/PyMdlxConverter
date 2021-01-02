from PyMdlxConverter.parsers.mdlx.tokenstream import TokenStream
from PyMdlxConverter.parsers.mdlx.genericobject import GenericObject
from PyMdlxConverter.parsers.errors import TokenStreamError


class Helper(GenericObject):

    def __init__(self):
        super().__init__(flags=0x0)

    def read_mdl(self, stream: TokenStream):
        for token in super().read_generic_block(stream):
            raise TokenStreamError('Helper', token)

    def write_mdl(self, stream: TokenStream, version=None):
        stream.start_object_block('Helper', self.name)
        self.write_generic_header(stream)
        self.write_generic_animations(stream)
        stream.end_block()