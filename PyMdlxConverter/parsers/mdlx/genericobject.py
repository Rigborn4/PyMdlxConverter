from PyMdlxConverter.common.binarystream import BinaryStream
from PyMdlxConverter.parsers.mdlx.tokenstream import TokenStream
from PyMdlxConverter.parsers.mdlx.animatedobject import AnimatedObject


class GenericObject(AnimatedObject):

    def __init__(self, flags=None):
        super().__init__()
        self.flags = flags
        self.name = ''
        self.object_id = -1
        self.parent_id = -1

    def read_mdx(self, stream: BinaryStream, version):
        size = stream.read_uint32()
        self.name = stream.read(80)
        self.object_id = stream.read_int32()
        self.parent_id = stream.read_int32()
        self.flags = stream.read_uint32()
        self.read_animations(stream, size - 96)

    def write_mdx(self, stream: BinaryStream, version):
        stream.write_uint32(self.get_generic_byte_length())
        stream.write(self.name)
        stream.skip(80 - len(self.name))
        stream.write_int32(self.object_id)
        stream.write_int32(self.parent_id)
        stream.write_uint32(self.flags)
        for animation in self.each_animation(True):
            animation.write_mdx(stream)

    def write_non_generic_animation_chunks(self, stream: BinaryStream):
        for animation in self.each_animation(False):
            animation.write_mdx(stream)

    def read_generic_block(self, stream: TokenStream):
        self.name = stream.read()
        for token in self.read_animated_block(stream):
            if token == 'ObjectId':
                self.object_id = stream.read_int()
            elif token == 'Parent':
                self.parent_id = stream.read_int()
            elif token == 'BillboardedLockZ':
                self.flags |= 0x40
            elif token == 'BillboardedLockY':
                self.flags |= 0x20
            elif token == 'BillboardedLockX':
                self.flags |= 0x10
            elif token == 'Billboarded':
                self.flags |= 0x8
            elif token == 'CameraAnchored':
                self.flags |= 0x80
            elif token == 'DontInherit':
                for token in stream.read_block():
                    if token == 'Rotation':
                        self.flags |= 0x2
                    elif token == 'Translation':
                        self.flags |= 0x1
                    elif token == 'Scaling':
                        self.flags |= 0x4
            elif token == 'Translation':
                self.read_animation(stream, 'KGTR')
            elif token == 'Rotation':
                self.read_animation(stream, 'KGRT')
            elif token == 'Scaling':
                self.read_animation(stream, 'KGSC')
            else:
                yield token

    def write_generic_header(self, stream: TokenStream):
        stream.write_number_attrib('ObjectId', self.object_id)
        if self.parent_id != -1:
            stream.write_number_attrib('Parent', self.parent_id)
        if self.flags & 0x40:
            stream.write_flag('BillboardedLockZ')
        if self.flags & 0x20:
            stream.write_flag('BillboardedLockY')
        if self.flags & 0x10:
            stream.write_flag('BillboardedLockX')
        if self.flags & 0x8:
            stream.write_flag('Billboarded')
        if self.flags & 0x80:
            stream.write_flag('CameraAnchored')
        if self.flags & 0x2:
            stream.write_flag('DontInherit { Rotation }')
        if self.flags & 0x1:
            stream.write_flag('DontInherit { Translation }')
        if self.flags & 0x4:
            stream.write_flag('DontInherit { Scaling }')

    def write_generic_animations(self, stream: TokenStream):
        self.write_animation(stream, 'KGTR')
        self.write_animation(stream, 'KGRT')
        self.write_animation(stream, 'KGSC')

    def each_animation(self, want_generic):
        for animation in self.animations:
            name = animation.name
            is_generic = (name == 'KGTR' or name == 'KGRT' or name == 'KGSC')
            if (want_generic and is_generic) or (not want_generic and not is_generic):
                yield animation

    def get_generic_byte_length(self):
        size = 96
        for animation in self.each_animation(True):
            size += animation.get_byte_length()
        return size

    def get_byte_length(self, version=None):
        return 96 + super().get_byte_length(version=version)