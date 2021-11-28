from PyMdlxConverter.common.binarystream import BinaryStream
from PyMdlxConverter.parsers.mdlx.tokenstream import TokenStream
from PyMdlxConverter.parsers.mdlx.extent import Extent
from PyMdlxConverter.parsers.errors import TokenStreamError


class Geoset(object):

    def __init__(self):
        self.vertices = None
        self.normals = None
        self.face_type_groups = None
        self.face_groups = []
        self.faces = None
        self.vertex_groups = None
        self.matrix_groups = None
        self.matrix_indices = None
        self.material_id = 0
        self.selection_group = 0
        self.selection_flags = 0
        self.lod = -1
        self.lod_name = ''
        self.extent = Extent()
        self.sequence_extents = []
        self.tangents = []
        self.skin = []
        self.uv_sets = []

    def read_mdx(self, stream: BinaryStream, version: int):
        stream.read_uint32()
        stream.skip(4)  # VRTX TAG
        self.vertices = stream.read_float32_array(stream.read_uint32() * 3)
        stream.skip(4)  # NRMS TAG
        self.normals = stream.read_float32_array(stream.read_uint32() * 3)
        stream.skip(4)  # PTYP TAG
        self.face_type_groups = stream.read_uint32_array(stream.read_uint32())
        stream.skip(4)  # PCNT TAG
        self.face_groups = stream.read_uint32_array(stream.read_uint32())
        stream.skip(4)  # PVTX TAG
        self.faces = stream.read_uint16_array(stream.read_uint32())
        stream.skip(4)  # GNDX TAG
        self.vertex_groups = stream.read_uint8_array(stream.read_uint32())
        stream.skip(4)  # MTGC TAG
        self.matrix_groups = stream.read_uint32_array(stream.read_uint32())
        stream.skip(4)  # MATS TAG
        self.matrix_indices = stream.read_uint32_array(stream.read_uint32())
        self.material_id = stream.read_uint32()
        self.selection_group = stream.read_uint32()
        self.selection_flags = stream.read_uint32()
        if version > 800:
            self.lod = stream.read_int32()
            self.lod_name = stream.read(80)
        self.extent.read_mdx(stream)
        for i in range(stream.read_uint32()):
            extent = Extent()
            extent.read_mdx(stream)
            self.sequence_extents.append(extent)
        if version > 800:
            if stream.peek(4) == 'TANG':
                stream.skip(4)
                self.tangents = stream.read_float32_array(stream.read_uint32() * 4)
            if stream.peek(4) == 'SKIN':
                stream.skip(4)
                self.skin = stream.read_uint8_array(stream.read_uint32())
        stream.skip(4)
        for i in range(stream.read_uint32()):
            stream.skip(4)
            self.uv_sets.append(stream.read_float32_array(stream.read_uint32() * 2))

    def write_mdx(self, stream: BinaryStream, version: int):
        stream.write_uint32(self.get_byte_length(version))
        stream.write('VRTX')
        stream.write_uint32(len(self.vertices) // 3)
        stream.write_float32_array(self.vertices)
        stream.write('NRMS')
        stream.write_uint32(len(self.normals) // 3)
        stream.write_float32_array(self.normals)
        stream.write('PTYP')
        stream.write_uint32(len(self.face_type_groups))
        stream.write_uint32_array(self.face_type_groups)
        stream.write('PCNT')
        stream.write_uint32(len(self.face_groups))
        stream.write_uint32_array(self.face_groups)
        stream.write('PVTX')
        stream.write_uint32(len(self.faces))
        stream.write_uint16_array(self.faces)
        stream.write('GNDX')
        stream.write_uint32(len(self.vertex_groups))
        stream.write_uint8_array(self.vertex_groups)
        stream.write('MTGC')
        stream.write_uint32(len(self.matrix_groups))
        stream.write_uint32_array(self.matrix_groups)
        stream.write('MATS')
        stream.write_uint32(len(self.matrix_indices))
        stream.write_uint32_array(self.matrix_indices)
        stream.write_uint32(self.material_id)
        stream.write_uint32(self.selection_group)
        stream.write_uint32(self.selection_flags)
        if version > 800:
            stream.write_int32(self.lod)
            stream.write(self.lod_name)
            stream.skip(80 - len(self.lod_name))
        self.extent.write_mdx(stream)
        stream.write_uint32(len(self.sequence_extents))
        for sequence_extent in self.sequence_extents:
            sequence_extent.write_mdx(stream)
        if version > 800:
            if len(self.tangents):
                stream.write('TANG')
                stream.write_uint32(len(self.tangents) // 4)
                stream.write_float32_array(self.tangents)
            if len(self.skin):
                stream.write('SKIN')
                stream.write_uint32(len(self.skin))
                stream.write_uint8_array(self.skin)
        stream.write('UVAS')
        stream.write_uint32(len(self.uv_sets))
        for uv_set in self.uv_sets:
            stream.write('UVBS')
            stream.write_uint32(len(uv_set) // 2)
            stream.write_float32_array(uv_set)

    def read_mdl(self, stream: TokenStream):
        for token in stream.read_block():
            if token == 'Vertices':
                self.vertices = stream.read_vectors_block(stream.read_int(), 3)
            elif token == 'Normals':
                self.normals = stream.read_vectors_block(stream.read_int(), 3)
            elif token == 'TVertices':
                self.uv_sets.append(stream.read_vectors_block(stream.read_int(), 2))
            elif token == 'VertexGroup':
                vertex_groups = []
                for vertex_group in stream.read_block():
                    vertex_groups.append(int(vertex_group))
                self.vertex_groups = vertex_groups
            elif token == 'Tangents':
                self.tangents = stream.read_vectors_block(stream.read_int(), 4)
            elif token == 'SkinWeights':
                self.skin = stream.read_vector(stream.read_int() * 8)
            elif token == 'Faces':
                self.face_type_groups = []
                vectors = stream.read_int()
                count = stream.read_int()
                stream.read()
                stream.read()
                self.faces = stream.read_single_vector_block(count)
                self.face_groups = [count]
                stream.read()
            elif token == 'Groups':
                indices = []
                groups = []
                stream.read_int()
                stream.read_int()
                for _ in stream.read_block():
                    size = 0
                    for index in stream.read_block():
                        indices.append(int(index))
                        size += 1
                    groups.append(size)
                self.matrix_indices = indices
                self.matrix_groups = groups
            elif token == 'MinimumExtent':
                self.extent.min = stream.read_vector(3)
            elif token == 'MaximumExtent':
                self.extent.max = stream.read_vector(3)
            elif token == 'BoundsRadius':
                self.extent.bounds_radius = stream.read_float()
            elif token == 'Anim':
                extent = Extent()
                for token in stream.read_block():
                    if token == 'MinimumExtent':
                        extent.min = stream.read_vector(3)
                    elif token == 'MaximumExtent':
                        extent.max = stream.read_vector(3)
                    elif token == 'BoundsRadius':
                        extent.bounds_radius = stream.read_float()
                self.sequence_extents.append(extent)
            elif token == 'MaterialID':
                self.material_id = stream.read_int()
            elif token == 'SelectionGroup':
                self.selection_group = stream.read_int()
            elif token == 'Unselectable':
                self.selection_flags = 4
            elif token == 'LevelOfDetail':
                self.lod = stream.read_int()
            elif token == 'Name':
                self.lod_name = stream.read()
            else:
                raise TokenStreamError('Geoset', token)

    def write_mdl(self, stream: TokenStream, version=None):
        stream.start_block('Geoset', None)
        stream.write_vector_array_block('Vertices', self.vertices, 3)
        stream.write_vector_array_block('Normals', self.normals, 3)
        for uv_set in self.uv_sets:
            stream.write_vector_array_block('TVertices', uv_set, 2)
        if version > 800 or len(self.tangents):
            stream.write_vector_array_block('Tangents', self.tangents, 4)
        if version > 800 or len(self.skin):
            stream.start_block('SkinWeights', len(self.skin) // 8)
            for i in range(0, len(self.skin), 8):
                stream.write_line(f'{", ".join([str(a) for a in self.skin[i:i + 8]])+","}')
        else:
            stream.start_block('VertexGroup', None)
            for i in range(len(self.vertex_groups)):
                stream.write_line(f'{self.vertex_groups[i]},')
        stream.end_block()
        stream.start_block('Faces', [str(1), str(len(self.faces))])
        stream.start_block('Triangles', None)
        stream.write_vector(self.faces)
        stream.end_block()
        stream.end_block()
        stream.start_block('Groups', [str(len(self.matrix_groups)), str(len(self.matrix_indices))])
        index = 0
        for group_size in self.matrix_groups:
            stream.write_vector_attrib('Matrices', self.matrix_indices[index: index + group_size])
            index += group_size
        stream.end_block()
        self.extent.write_mdl(stream)
        for sequence_extent in self.sequence_extents:
            stream.start_block('Anim', None)
            sequence_extent.write_mdl(stream)
            stream.end_block()
        stream.write_number_attrib('MaterialID', self.material_id)
        stream.write_number_attrib('SelectionGroup', self.selection_group)
        if self.selection_flags == 4:
            stream.write_flag('Unselectable')
        if version > 800:
            stream.write_number_attrib('LevelOfDetail', self.lod)
            if len(self.lod_name):
                stream.write_string_attrib('Name', self.lod_name)
        stream.end_block()

    def get_byte_length(self, version):
        size = (120 + (len(self.vertices) * 4) + (len(self.normals) * 4) + (len(self.face_type_groups) * 4)
                + (len(self.face_groups) * 4) + (len(self.faces) * 2) + (len(self.vertex_groups) * 1)
                + (len(self.matrix_groups) * 4) + (len(self.matrix_indices) * 4)
                + ((len(self.sequence_extents)) * 28))
        if version > 800:
            size += 84
        if len(self.tangents):
            size += 8 + (4 * len(self.tangents))
        if len(self.skin):
            size += 8 + (1 * len(self.skin))
        for idx, uv_set in enumerate(self.uv_sets):
            size += 8 + (4 * len(self.uv_sets[idx]))
        return size
