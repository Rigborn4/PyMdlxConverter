from PyMdlxConverter.common.mathutils import float_decimals, float_array_decimals


class TokenStream(object):

    def __init__(self, buffer: str = None):
        self.buffer = buffer or ''
        self.index = 0
        self.precision = 1000000   # 6 digits after the decimal point
        self.ident = 0

    def read_token(self):
        buffer = self.buffer
        length = len(buffer)
        in_comment = False
        in_string = False
        token = ''
        while self.index < length:
            c = buffer[self.index]
            self.index += 1
            if in_comment:
                if c == '\n':
                    in_comment = False
            elif in_string:
                if c == '\\':
                    token += c + buffer[self.index]
                    self.index += 1
                elif c == '\n':
                    token += '\\n'
                elif c == '\r':
                    token += '\\r'
                elif c == '"':
                    return token
                else:
                    token += c
            elif c == ' ' or c == ',' or c == '\t' or c == '\n' or c == ':' or c == '\r':
                if len(token):
                    return token
            elif c == '{' or c == '}':
                if len(token):
                    self.index -= 1
                    return token
                else:
                    return c
            elif c == '/' and buffer[self.index] == '/':
                if len(token):
                    self.index -= 1
                    return token
                else:
                    in_comment = True
            elif c == '"':
                if len(token):
                    self.index -= 1
                    return token
                else:
                    in_string = True
            else:
                token += c

    def read(self):
        value = self.read_token()
        return value

    def peek(self):
        index = self.index
        value = self.read()
        self.index = index
        return value

    def read_int(self):
        return int(self.read())

    def read_float(self):
        return float(self.read())

    def read_vector(self, size):
        self.read()
        vector = []
        for i in range(size):
            vector.append(self.float_or_int())
        self.read()
        return vector

    def read_single_vector_block(self, size):
        self.read()
        self.read()
        vector_block = []
        for i in range(size):
            vector_block.append(self.float_or_int())
        self.read()
        self.read()
        return vector_block

    def read_vectors_block(self, size, vector_size):
        self.read()
        vector_block = []
        for i in range(size):
            vector_block += self.read_vector(vector_size)
        self.read()
        return vector_block

    def read_color(self):
        self.read()
        r, g, b, = self.read_float(), self.read_float(), self.read_float()
        self.read()
        return [b, g, r]

    def read_block(self):
        self.read()
        token = self.read()
        while token != '}':
            yield token
            token = self.read()

    def float_or_int(self):  # some other parsers use float value 1.0 as int 1 so it's always good to check.
        token = self.peek()
        try:
            token = int(token)
        except ValueError:
            token = float(token)
        if isinstance(token, int):
            return self.read_int()
        else:
            return self.read_float()

    def write_comment(self, data):
        for i in data:
            self.buffer += '//'+i+'\n'

    def write_line(self, line):
        t = '\t'
        self.buffer += f"{t * self.ident}{line}\n"

    def write_flag(self, flag):
        self.write_line(f'{flag},')

    def write_flag_attrib(self, name, flag):
        self.write_line(f'{name} {flag},')

    def write_number_attrib(self, name, value):
        if isinstance(value, int):
            self.write_line(f'{name} {value},')
        else:
            self.write_line(f'{name} {float_decimals(value, self.precision)},')

    def write_string_attrib(self, name, value):
        self.write_line(f'{name} "{value}",')

    def write_vector_attrib(self, name, value):
        self.write_line(f'{name} '+'{ '+f'{float_array_decimals(value, self.precision)} '+'},')

    def write_color(self, name, value):
        b = float_decimals(value[0], self.precision)
        g = float_decimals(value[1], self.precision)
        r = float_decimals(value[2], self.precision)
        self.write_line(f'{name} '+'{ '+f'{r}, '+f'{g}, '+f'{b} '+'},')

    def write_vector(self, value):
        self.write_line('{ '+f'{float_array_decimals(value, self.precision)} '+'},')

    def write_vector_array_block(self, name, vector: list, size):
        self.start_block(name, len(vector) // size)
        i = 0
        while i < len(vector):
            self.write_vector(vector[i:i + size])
            i += size
        self.end_block()

    def start_block(self, name, headers):
        if headers is not None:
            if isinstance(headers, list):
                name = f'{name} {" ".join(headers)}'
            else:
                name = f'{name} {headers}'
        self.write_line(f'{name} '+'{')
        self.ident += 1

    def start_object_block(self, header, name):
        n = name.replace('"', '\\"')
        self.write_line(f'{header} "{n}" '+'{')
        self.ident += 1

    def end_block(self):
        self.ident -= 1
        self.write_line('}')

    def end_block_comma(self):
        self.ident -= 1
        self.write_line('},')

    def indent(self):
        self.ident += 1

    def unindent(self):
        self.ident -= 1
