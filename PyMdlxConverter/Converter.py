from PyMdlxConverter.parsers.mdlx.model import Model
from PyMdlxConverter.parsers.errors import BinaryStreamError


def convert(buffer, file_format=None):
    model = Model(buffer)
    if file_format == 'MDX':
        return model.save_mdx()
    elif file_format == 'MDL':
        return model.save_mdl()
    else:
        raise BinaryStreamError(type(buffer))