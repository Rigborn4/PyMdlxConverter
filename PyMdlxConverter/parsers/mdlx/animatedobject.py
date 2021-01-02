from PyMdlxConverter.common.binarystream import BinaryStream
from PyMdlxConverter.parsers.mdlx.tokenstream import TokenStream
from PyMdlxConverter.parsers.mdlx.animations import Animation
from PyMdlxConverter.parsers.mdlx.animationmap import anim_map as animation_map


class AnimatedObject(object):

    def __init__(self):
        self.animations = []
        self.animation = Animation()

    def read_animations(self, stream: BinaryStream, size: int):
        end = stream.index + size
        while stream.index < end:
            name = stream.read(4)
            animation = animation_map[name][1]()
            animation.read_mdx(stream, name)
            self.animations.append(animation)

    def write_animations(self, stream: BinaryStream):
        for animation in self.animations:
            animation.write_mdx(stream)

    def read_animated_block(self, stream: TokenStream):
        for token in stream.read_block():
            if token == 'static':
                yield f'static {stream.read()}'
            else:
                yield token

    def read_animation(self, stream: TokenStream, name):
        animation = animation_map[name][1]()
        animation.read_mdl(stream, name)
        self.animations.append(animation)

    def write_animation(self, stream: TokenStream, name):
        for animation in self.animations:
            if animation.name == name:
                animation.write_mdl(stream, animation_map[name][0])
                return True
        return False

    def get_byte_length(self, version=None):
        size = 0
        for animation in self.animations:
            size += animation.get_byte_length()
        return size
