from PyMdlxConverter.parsers.mdlx.model import Model


def parse(buffer):
    model = Model(buffer)
    model.load()
    return model

