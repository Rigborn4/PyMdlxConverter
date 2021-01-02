from typing import Union
import struct
from PyMdlxConverter.parsers.errors import ByteStreamError, BinaryStreamError


class BinaryStream(object):

    def __init__(self, buffer: Union[bytearray, bytes], byte_offset=None, byte_length=None):
        self.byte_offset = byte_offset or 0
        self.byte_length = byte_length or 0
        if isinstance(buffer, bytearray):
            self.buffer = buffer
            self.index = 0
            self.remaining = self.byte_length if self.byte_length else len(self.buffer)
        elif isinstance(buffer, bytes):
            self.buffer = buffer
            self.index = 0
            self.remaining = self.byte_length if self.byte_length else len(self.buffer)
        else:
            raise BinaryStreamError(type(buffer))
        self.buffer_array = bytearray(buffer)

    def substream(self, byte_length):
        return BinaryStream(self.buffer, self.index, byte_length)

    def skip(self, byte_count):
        if self.remaining < byte_count:
            raise ByteStreamError('skip', self.remaining, want_bytes=byte_count)
        self.index += byte_count
        self.remaining -= byte_count

    def seek(self, index):
        self.index = index
        self.remaining = self.byte_length - index

    def peek(self, size, allow_nulls=False):
        buffer_array = self.buffer_array
        index = self.index
        data = struct.unpack("<{}s".format(size), buffer_array[index:index + size])
        data = data[0].decode()
        if not allow_nulls:
            data = data.rstrip('\x00')
        return data

    def read(self, size, allow_nulls=False):
        size = size or self.remaining
        if self.remaining < size:
            raise ByteStreamError('read', self.remaining, want_bytes=size)
        data = self.peek(size, allow_nulls)
        self.index += size
        self.remaining -= size
        return data

    def peek_until_null(self):
        buffer_array = self.buffer_array
        index = self.index
        data = ""
        b = buffer_array[index]
        i = 0
        while b != 0:
            data += chr(b)
            i += 1
            b = buffer_array[index + 1]
        return data

    def read_until_null(self):
        data = self.peek_until_null()
        self.index += len(data) + 1
        self.remaining -= len(data) + 1
        return data

    def peek_char_array(self, size):
        buffer_array = self.buffer_array
        index = self.index
        data = []
        for i in range(size):
            data.append(chr(buffer_array[index + i]))
        return data

    def read_char_array(self, size):
        if self.remaining < size:
            raise ByteStreamError('read_char_array', self.remaining, want_bytes=size)
        data = self.peek_char_array(size)
        self.index += size
        self.remaining -= size
        return data

    def read_int8(self):
        if self.remaining < 1:
            raise ByteStreamError('read_int8', self.remaining)
        index = self.index
        buffer_array = self.buffer_array
        data = struct.unpack('b', buffer_array[index:index + 1])
        self.index += 1
        self.remaining -= 1
        return data[0]

    def read_int16(self):
        if self.remaining < 2:
            raise ByteStreamError('read_int16', self.remaining, want_bytes=2)
        index = self.index
        buffer_array = self.buffer_array
        data = struct.unpack('<h', buffer_array[index:index + 2])
        self.index += 2
        self.remaining -= 2
        return data[0]

    def read_int32(self):
        if self.remaining < 4:
            raise ByteStreamError('read_int32', self.remaining, want_bytes=4)
        index = self.index
        buffer_array = self.buffer_array
        data = struct.unpack('<i', buffer_array[index:index + 4])
        self.index += 4
        self.remaining -= 4
        return data[0]

    def read_uint8(self):
        if self.remaining < 1:
            raise ByteStreamError('read_uint8', self.remaining)
        index = self.index
        buffer_array = self.buffer_array
        data = struct.unpack('<B', buffer_array[index:index + 1])
        self.index += 1
        self.remaining -= 1
        return data[0]

    def read_uint16(self):
        if self.remaining < 2:
            raise ByteStreamError('read_uint16', self.remaining, want_bytes=2)
        index = self.index
        buffer_array = self.buffer_array
        data = struct.unpack('<H', buffer_array[index:index + 2])
        self.index += 2
        self.remaining -= 2
        return data[0]

    def read_uint32(self):
        if self.remaining < 4:
            raise ByteStreamError('read_uint32', self.remaining, want_bytes=4)
        index = self.index
        buffer_array = self.buffer_array
        data = struct.unpack('<I', buffer_array[index:index + 4])
        self.index += 4
        self.remaining -= 4
        return data[0]

    def read_float32(self):
        if self.remaining < 4:
            raise ByteStreamError('read_float32', self.remaining, want_bytes=4)
        index = self.index
        buffer_array = self.buffer_array
        data = struct.unpack('<f', buffer_array[index:index + 4])
        self.index += 4
        self.remaining -= 4
        return data[0]

    def read_float64(self):
        if self.remaining < 8:
            raise ByteStreamError('read_float64', self.remaining, want_bytes=8)
        index = self.index
        buffer_array = self.buffer_array
        data = struct.unpack('<d', buffer_array[index:index + 8])
        self.index += 8
        self.remaining -= 8
        return data[0]

    def read_int8_array(self, array_size):
        if self.remaining < array_size:
            raise ByteStreamError('read_int8_array', self.remaining, want_bytes=array_size)
        index = self.index
        buffer_array = self.buffer_array
        data = struct.unpack('<{}b'.format(array_size), buffer_array[index:index + array_size])
        self.index += array_size
        self.remaining -= array_size
        return data

    def read_int16_array(self, array_size):
        if self.remaining < array_size * 2:
            raise ByteStreamError('read_int16_array', self.remaining, want_bytes=array_size * 2)
        index = self.index
        buffer_array = self.buffer_array
        data = struct.unpack('<{}h'.format(array_size), buffer_array[index:index + array_size * 2])
        self.index += array_size * 2
        self.remaining -= array_size * 2
        return data

    def read_int32_array(self, array_size):
        if self.remaining < array_size * 4:
            raise ByteStreamError('read_int32_array', self.remaining, want_bytes=array_size * 4)
        index = self.index
        buffer_array = self.buffer_array
        data = struct.unpack('<{}i'.format(array_size), buffer_array[index:index + array_size * 4])
        self.index += array_size * 4
        self.remaining -= array_size * 4
        return data

    def read_uint8_array(self, array_size):
        if self.remaining < array_size:
            raise ByteStreamError('read_uint8_array', self.remaining, want_bytes=array_size)
        index = self.index
        buffer_array = self.buffer_array
        data = struct.unpack('<{}B'.format(array_size), buffer_array[index:index + array_size])
        self.index += array_size
        self.remaining -= array_size
        return data

    def read_uint16_array(self, array_size):
        if self.remaining < array_size * 2:
            raise ByteStreamError('read_uint16_array', self.remaining, want_bytes=array_size * 2)
        index = self.index
        buffer_array = self.buffer_array
        data = struct.unpack('<{}H'.format(array_size), buffer_array[index:index + (array_size * 2)])
        self.index += array_size * 2
        self.remaining -= array_size * 2
        return data

    def read_uint32_array(self, array_size):
        if self.remaining < array_size * 4:
            raise ByteStreamError('read_uint32_array', self.remaining, want_bytes=array_size * 4)
        index = self.index
        buffer_array = self.buffer_array
        data = struct.unpack('<{}I'.format(array_size), buffer_array[index:index + (array_size * 4)])
        self.index += (array_size * 4)
        self.remaining -= (array_size * 4)
        return data

    def read_float32_array(self, array_size):
        if self.remaining < array_size * 4:
            raise ByteStreamError('read_float32_array', self.remaining, want_bytes=array_size * 4)
        index = self.index
        buffer_array = self.buffer_array
        data = struct.unpack('<{}f'.format(array_size), buffer_array[index:index + (array_size * 4)])
        self.index += (array_size * 4)
        self.remaining -= (array_size * 4)
        return data

    def read_float64_array(self, array_size):
        if self.remaining < array_size * 8:
            raise ByteStreamError('read_float32_array', self.remaining, want_bytes=array_size * 8)
        index = self.index
        buffer_array = self.buffer_array
        data = struct.unpack('<{}d'.format(array_size), buffer_array[index:index + (array_size * 8)])
        self.index += array_size * 8
        self.remaining -= array_size * 8
        return data

    def write(self, value: Union[str, None]):
        buffer_array = self.buffer_array
        count = len(value)
        data = [bytes(i.encode()) for i in value]
        buffer_array[self.index: self.index + count] = struct.pack('{}c'.format(count), *data)
        self.index += count

    def write_int8(self, value):
        self.buffer_array[self.index:self.index + 1] = struct.pack('<b', value)
        self.index += 1

    def write_int16(self, value):
        self.buffer_array[self.index:self.index + 2] = struct.pack('<h', value)
        self.index += 2

    def write_int32(self, value):
        self.buffer_array[self.index:self.index + 4] = struct.pack('<i', value)
        self.index += 4

    def write_uint8(self, value):
        self.buffer_array[self.index:self.index + 1] = struct.pack('<B', value)
        self.index += 1

    def write_uint16(self, value):
        self.buffer_array[self.index:self.index + 2] = struct.pack('<H', value)
        self.index += 2

    def write_uint32(self, value):
        self.buffer_array[self.index:self.index + 4] = struct.pack('<I', value)
        self.index += 4

    def write_float32(self, value):
        self.buffer_array[self.index:self.index + 4] = struct.pack('<f', value)
        self.index += 4

    def write_float64(self, value):
        self.buffer_array[self.index:self.index + 8] = struct.pack('<d', value)
        self.index += 8

    def write_int8_array(self, value):
        array_size = len(value)
        self.buffer_array[self.index: self.index + array_size] = struct.pack('<{}b'.format(array_size), *value)
        self.index += array_size

    def write_int16_array(self, value):
        array_size = len(value)
        self.buffer_array[self.index: self.index + (array_size * 2)] = struct.pack('<{}h'.format(array_size), *value)
        self.index += array_size * 2

    def write_int32_array(self, value):
        array_size = len(value)
        self.buffer_array[self.index: self.index + (array_size * 4)] = struct.pack('<{}i'.format(array_size), *value)
        self.index += array_size * 4

    def write_uint8_array(self, value):
        array_size = len(value)
        self.buffer_array[self.index: self.index + array_size] = struct.pack('{}B'.format(array_size), *value)
        self.index += array_size

    def write_uint16_array(self, value):
        array_size = len(value)
        self.buffer_array[self.index: self.index + (array_size * 2)] = struct.pack('{}H'.format(array_size), * value)
        self.index += array_size * 2

    def write_uint32_array(self, value):
        array_size = len(value)
        self.buffer_array[self.index: self.index + (array_size * 4)] = struct.pack('{}I'.format(array_size), *value)
        self.index += array_size * 4

    def write_float32_array(self, value):
        array_size = len(value)
        self.buffer_array[self.index: self.index + (array_size * 4)] = struct.pack('{}f'.format(array_size), *value)
        self.index += array_size * 4

    def write_float64_array(self, value):
        array_size = len(value)
        self.buffer_array[self.index: self.index + (array_size * 8)] = struct.pack('{}d'.format(array_size), *value)
        self.index += array_size * 8
