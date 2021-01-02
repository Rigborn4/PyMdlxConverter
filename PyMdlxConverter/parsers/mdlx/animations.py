from PyMdlxConverter.common.binarystream import BinaryStream
from PyMdlxConverter.parsers.mdlx.tokenstream import TokenStream


class Animation(object):

    def __init__(self):
        self.name = ''
        self.interpolation_type = 0
        self.global_sequence_id = -1
        self.frames = []
        self.values = []
        self.in_tans = []
        self.out_tans = []
        self.byte_value = 0

    def read_mdx_value(self, stream: BinaryStream) -> tuple:
        return 0, 1

    def write_mdx_value(self, stream: BinaryStream, value):
        pass

    def read_mdl_value(self, stream: TokenStream) -> tuple:
        return 0, 1

    def write_mdl_value(self, stream: TokenStream, name, value):
        pass

    def read_mdx(self, stream: BinaryStream, name: str):
        frames = self.frames
        values = self.values
        in_tans = self.in_tans
        out_tans = self.out_tans
        tracks_count = stream.read_uint32()
        interpolation_type = stream.read_uint32()
        self.name = name
        self.interpolation_type = interpolation_type
        self.global_sequence_id = stream.read_int32()
        for i in range(tracks_count):
            frames.append(stream.read_int32())
            values.append(self.read_mdx_value(stream))
            if interpolation_type > 1:
                in_tans.append(self.read_mdx_value(stream))
                out_tans.append(self.read_mdx_value(stream))

    def write_mdx(self, stream: BinaryStream):
        interpolation_type = self.interpolation_type
        frames = self.frames
        values = self.values
        in_tans = self.in_tans
        out_tans = self.out_tans
        tracks_count = len(frames)
        stream.write(self.name)
        stream.write_uint32(tracks_count)
        stream.write_uint32(interpolation_type)
        stream.write_int32(self.global_sequence_id)
        for i in range(tracks_count):
            stream.write_int32(frames[i])
            self.write_mdx_value(stream, values[i])
            if interpolation_type > 1:
                self.write_mdx_value(stream, in_tans[i])
                self.write_mdx_value(stream, out_tans[i])

    def read_mdl(self, stream: TokenStream, name):
        frames = self.frames
        values = self.values
        in_tans = self.in_tans
        out_tans = self.out_tans
        self.name = name
        tracks_count = stream.read_int()
        stream.read()
        interpolation_type = 0
        token = stream.read()
        if token == 'DontInterp':
            interpolation_type = 0
        elif token == 'Linear':
            interpolation_type = 1
        elif token == 'Hermite':
            interpolation_type = 2
        elif token == 'Bezier':
            interpolation_type = 3
        self.interpolation_type = interpolation_type
        if stream.peek() == 'GlobalSeqId':
            stream.read()
            self.global_sequence_id = stream.read_int()
        for i in range(tracks_count):
            frames.append(stream.read_int())
            values.append(self.read_mdl_value(stream))
            if interpolation_type > 1:
                stream.read()
                in_tans.append(self.read_mdl_value(stream))
                stream.read()
                out_tans.append(self.read_mdl_value(stream))
        stream.read()

    def write_mdl(self, stream: TokenStream, name, version=None):
        interpolation_type = self.interpolation_type
        frames = self.frames
        values = self.values
        in_tans = self.in_tans
        out_tans = self.out_tans
        tracks_count = len(frames)
        stream.start_block(name, len(self.frames))
        token = ''
        if self.interpolation_type == 0:
            token = 'DontInterp'
        elif self.interpolation_type == 1:
            token = 'Linear'
        elif self.interpolation_type == 2:
            token = 'Hermite'
        elif self.interpolation_type == 3:
            token = 'Bezier'
        stream.write_flag(token)
        if self.global_sequence_id != -1:
            stream.write_number_attrib('GlobalSeqId', self.global_sequence_id)
        for i in range(tracks_count):
            self.write_mdl_value(stream, f'{frames[i]}:', values[i])
            if interpolation_type > 1:
                stream.indent()
                self.write_mdl_value(stream, 'InTan', in_tans[i])
                self.write_mdl_value(stream, 'OutTan', out_tans[i])
                stream.unindent()
        stream.end_block()

    def get_byte_length(self):
        tracks_count = len(self.frames)
        size = 16
        if tracks_count:
            if isinstance(self.values[0], (int, float)):
                bytes_per_value = 4
            elif isinstance(self.values[0], (list, tuple)):
                bytes_per_value = len(self.values[0]) * 4
            values_per_track = 1
            if self.interpolation_type > 1:
                values_per_track = 3
            size += (4 + values_per_track * bytes_per_value) * tracks_count
        return size


class UintAnimation(Animation):

    def read_mdx_value(self, stream: BinaryStream) -> tuple:
        self.byte_value = 4
        return stream.read_uint32()

    def write_mdx_value(self, stream: BinaryStream, value):
        stream.write_uint32_array(value)

    def read_mdl_value(self, stream: TokenStream):
        self.byte_value = 4
        return stream.read_int()

    def write_mdl_value(self, stream: TokenStream, name, value):
        stream.write_number_attrib(name, value)


class FloatAnimation(Animation):

    def read_mdx_value(self, stream: BinaryStream) -> tuple:
        self.byte_value = 4
        return stream.read_float32()

    def write_mdx_value(self, stream: BinaryStream, value):
        stream.write_float32(value)

    def read_mdl_value(self, stream: TokenStream) -> tuple:
        self.byte_value = 4
        return stream.read_float()

    def write_mdl_value(self, stream: TokenStream, name, value):
        stream.write_number_attrib(name, value)


class Vector3Animation(Animation):

    def read_mdx_value(self, stream: BinaryStream) -> tuple:
        self.byte_value = 12
        return stream.read_float32_array(3)

    def write_mdx_value(self, stream: BinaryStream, value):
        stream.write_float32_array(value)

    def read_mdl_value(self, stream: TokenStream) -> tuple:
        self.byte_value = 12
        return stream.read_vector(3)

    def write_mdl_value(self, stream: TokenStream, name, value):
        stream.write_vector_attrib(name, value)


class Vector4Animation(Animation):

    def read_mdx_value(self, stream: BinaryStream) -> tuple:
        self.byte_value = 16
        return stream.read_float32_array(4)

    def write_mdx_value(self, stream: BinaryStream, value):
        stream.write_float32_array(value)

    def read_mdl_value(self, stream: TokenStream) -> tuple:
        self.byte_value = 16
        return stream.read_vector(4)

    def write_mdl_value(self, stream: TokenStream, name, value):
        stream.write_vector_attrib(name, value)
