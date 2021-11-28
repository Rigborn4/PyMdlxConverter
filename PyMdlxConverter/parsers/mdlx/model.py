import os

from PyMdlxConverter.common.binarystream import BinaryStream
from PyMdlxConverter.parsers.mdlx.tokenstream import TokenStream
from PyMdlxConverter.parsers.mdlx.extent import Extent
from PyMdlxConverter.parsers.mdlx.sequences import Sequence
from PyMdlxConverter.parsers.mdlx.material import Material
from PyMdlxConverter.parsers.mdlx.texture import Texture
from PyMdlxConverter.parsers.mdlx.textureanimation import TextureAnimation
from PyMdlxConverter.parsers.mdlx.geoset import Geoset
from PyMdlxConverter.parsers.mdlx.geosetanimation import GeosetAnimation
from PyMdlxConverter.parsers.mdlx.bone import Bone
from PyMdlxConverter.parsers.mdlx.light import Light
from PyMdlxConverter.parsers.mdlx.helper import Helper
from PyMdlxConverter.parsers.mdlx.attachment import Attachment
from PyMdlxConverter.parsers.mdlx.particleemitter import ParticleEmitter
from PyMdlxConverter.parsers.mdlx.particleemitter2 import ParticleEmitter2
from PyMdlxConverter.parsers.mdlx.particleemitterpopcorn import ParticleEmitterPopcorn
from PyMdlxConverter.parsers.mdlx.ribbonemitter import RibbonEmitter
from PyMdlxConverter.parsers.mdlx.camera import Camera
from PyMdlxConverter.parsers.mdlx.eventobject import EventObject
from PyMdlxConverter.parsers.mdlx.collisionshape import CollisionShape
from PyMdlxConverter.parsers.mdlx.faceeffect import FaceEffect
from PyMdlxConverter.parsers.mdlx.unknownchunk import UnknownChunk
from PyMdlxConverter.parsers.errors import TokenStreamError
from typing import Union
from datetime import datetime
from dateutil.tz import tzlocal
import atexit


class Model(object):

    def __init__(self, buffer: Union[bytearray, bytes, str]):
        self.buffer = buffer
        self.stream = None
        self.version = 800
        self.name = ''
        self.animation_file = ""
        self.extent = Extent()
        self.blend_time = 0
        self.sequences = []
        self.global_sequences = []
        self.materials = []
        self.textures = []
        self.texture_animations = []
        self.geosets = []
        self.geoset_animations = []
        self.bones = []
        self.lights = []
        self.helpers = []
        self.attachments = []
        self.pivot_points = []
        self.particle_emitters = []
        self.particle_emitters2 = []
        self.particle_emitters_popcorn = []
        self.ribbon_emitters = []
        self.cameras = []
        self.event_objects = []
        self.collision_shapes = []
        self.face_effects = []
        self.bind_pose = []
        self.unknown_chunks = []
        self.mdl_num_of_chunk = []
        self.mdl_comment = [""]

    @staticmethod
    def get_current_date_with_time_format():
        data = datetime.now(tzlocal())
        data = str(data)
        date = data[:19]
        time_format = data[26:]
        prefix = 'UTC'
        return f'{date} {prefix}{time_format}'

    def load(self):
        if isinstance(self.buffer, str):
            self.stream = TokenStream(buffer=self.buffer)
            self.load_mdl(self.stream)
        elif isinstance(self.buffer, (bytearray, bytes)):
            self.stream = BinaryStream(self.buffer)
            self.load_mdx()

    def load_mdx(self):
        stream = self.stream
        if stream.read(4) != 'MDLX':
            raise ValueError('Wrong Magic Number')
        tag = ''
        size = ''
        try:
            while stream.remaining > 0:
                tag = stream.read(4)
                size = stream.read_uint32()
                if tag == 'VERS':
                    self.load_version_chunk(stream)
                elif tag == 'MODL':
                    self.load_model_chunk(stream)
                elif tag == 'SEQS':
                    self.load_static_objects(self.sequences, Sequence, stream, int(size / 132))
                elif tag == 'GLBS':
                    self.load_global_sequence_chunk(stream, size)
                elif tag == 'MTLS':
                    self.load_dynamic_objects(self.materials, Material, stream, size)
                elif tag == 'TEXS':
                    self.load_static_objects(self.textures, Texture, stream, int(size / 268))
                elif tag == 'TXAN':
                    self.load_dynamic_objects(self.texture_animations, TextureAnimation, stream, size)
                elif tag == 'GEOS':
                    self.load_dynamic_objects(self.geosets, Geoset, stream, size)
                elif tag == 'GEOA':
                    self.load_dynamic_objects(self.geoset_animations, GeosetAnimation, stream, size)
                elif tag == 'BONE':
                    self.load_dynamic_objects(self.bones, Bone, stream, size)
                elif tag == 'LITE':
                    self.load_dynamic_objects(self.lights, Light, stream, size)
                elif tag == 'HELP':
                    self.load_dynamic_objects(self.helpers, Helper, stream, size)
                elif tag == 'ATCH':
                    self.load_dynamic_objects(self.attachments, Attachment, stream, size)
                elif tag == 'PIVT':
                    self.load_pivot_point_chunk(stream, size)
                elif tag == 'PREM':
                    self.load_dynamic_objects(self.particle_emitters, ParticleEmitter, stream, size)
                elif tag == 'PRE2':
                    self.load_dynamic_objects(self.particle_emitters2, ParticleEmitter2, stream, size)
                elif tag == 'CORN':
                    self.load_dynamic_objects(self.particle_emitters_popcorn, ParticleEmitterPopcorn, stream, size)
                elif tag == 'RIBB':
                    self.load_dynamic_objects(self.ribbon_emitters, RibbonEmitter, stream, size)
                elif tag == 'CAMS':
                    self.load_dynamic_objects(self.cameras, Camera, stream, size)
                elif tag == 'EVTS':
                    self.load_dynamic_objects(self.event_objects, EventObject, stream, size)
                elif tag == 'CLID':
                    self.load_dynamic_objects(self.collision_shapes, CollisionShape, stream, size)
                elif tag == 'FAFX':
                    self.load_static_objects(self.face_effects, FaceEffect, stream, int(size / 340))
                elif tag == 'BPOS':
                    self.load_bind_pose_chunk(stream, size)
                else:
                    self.unknown_chunks.append(UnknownChunk(stream, size, tag))
        except Exception as e:
            print(f'MDLX parsing error in {tag}: {e}')

    def load_version_chunk(self, stream):
        self.version = stream.read_uint32()

    def load_model_chunk(self, stream):
        self.name = stream.read(80)
        self.animation_file = stream.read(260)
        self.extent = Extent()
        self.extent.read_mdx(stream)
        self.blend_time = stream.read_uint32()

    def load_static_objects(self, out: Union[list, tuple], class_name, stream: BinaryStream, count: int):
        for i in range(count):
            obj = class_name()
            obj.read_mdx(stream)
            out.append(obj)

    def load_global_sequence_chunk(self, stream: BinaryStream, size: int):
        l = int(size / 4)
        i = 0
        while i < l:
            self.global_sequences.append(stream.read_uint32())
            i += 1

    def load_dynamic_objects(self, out: Union[list, tuple], class_name, stream: BinaryStream, size):
        end = stream.index + size
        while stream.index < end:
            obj = class_name()
            obj.read_mdx(stream, self.version)
            out.append(obj)

    def load_pivot_point_chunk(self, stream: BinaryStream, size: int):
        for i in range(int(size / 12)):
            self.pivot_points.append(stream.read_float32_array(3))

    def load_bind_pose_chunk(self, stream: BinaryStream, size: int):
        for i in range(stream.read_uint32()):
            self.bind_pose.append(stream.read_float32_array(12))

    def save_mdx(self):
        buffer = bytearray(self.get_byte_length())
        stream = BinaryStream(buffer)
        stream.write('MDLX')
        self.save_version_chunk(stream)
        self.save_model_chunk(stream)
        self.save_static_object_chunk(stream, 'SEQS', self.sequences, 132)
        self.save_global_sequence_chunk(stream)
        self.save_dynamic_object_chunk(stream, 'MTLS', self.materials)
        self.save_static_object_chunk(stream, 'TEXS', self.textures, 268)
        self.save_dynamic_object_chunk(stream, 'TXAN', self.texture_animations)
        self.save_dynamic_object_chunk(stream, 'GEOS', self.geosets)
        self.save_dynamic_object_chunk(stream, 'GEOA', self.geoset_animations)
        self.save_dynamic_object_chunk(stream, 'BONE', self.bones)
        self.save_dynamic_object_chunk(stream, 'LITE', self.lights)
        self.save_dynamic_object_chunk(stream, 'HELP', self.helpers)
        self.save_dynamic_object_chunk(stream, 'ATCH', self.attachments)
        self.save_pivot_point_chunk(stream)
        self.save_dynamic_object_chunk(stream, 'PREM', self.particle_emitters)
        self.save_dynamic_object_chunk(stream, 'PRE2', self.particle_emitters2)
        if self.version > 800:
            self.save_dynamic_object_chunk(stream, 'CORN', self.particle_emitters_popcorn)
        self.save_dynamic_object_chunk(stream, 'RIBB', self.ribbon_emitters)
        self.save_dynamic_object_chunk(stream, 'CAMS', self.cameras)
        self.save_dynamic_object_chunk(stream, 'EVTS', self.event_objects)
        self.save_dynamic_object_chunk(stream, 'CLID', self.collision_shapes)
        if self.version > 800:
            self.save_static_object_chunk(stream, 'FAFX', self.face_effects, 340)
            self.save_bind_pose_chunk(stream)
        for chunk in self.unknown_chunks:
            chunk.write_mdx(stream)
        return stream.buffer_array

    def save_version_chunk(self, stream: BinaryStream):
        stream.write('VERS')
        stream.write_uint32(4)
        stream.write_uint32(self.version)

    def save_model_chunk(self, stream: BinaryStream):
        stream.write('MODL')
        stream.write_uint32(372)
        stream.write(self.name)
        stream.skip(80 - len(self.name))
        stream.write(self.animation_file)
        stream.skip(260 - len(self.animation_file))
        self.extent.write_mdx(stream)
        stream.write_uint32(self.blend_time)

    def save_static_object_chunk(self, stream: BinaryStream, name, objects, size):
        if len(objects):
            stream.write(name)
            stream.write_uint32(len(objects) * size)
            for obj in objects:
                obj.write_mdx(stream)

    def save_global_sequence_chunk(self, stream: BinaryStream):
        if len(self.global_sequences):
            stream.write('GLBS')
            stream.write_uint32(len(self.global_sequences) * 4)
            for global_sequence in self.global_sequences:
                stream.write_uint32(global_sequence)

    def save_dynamic_object_chunk(self, stream: BinaryStream, name, objects):
        if len(objects):
            stream.write(name)
            stream.write_uint32(self.get_objects_byte_length(objects))
            for obj in objects:
                obj.write_mdx(stream, self.version)

    def save_pivot_point_chunk(self, stream: BinaryStream):
        if len(self.pivot_points):
            stream.write('PIVT')
            stream.write_uint32(len(self.pivot_points) * 12)
            for pivot_point in self.pivot_points:
                stream.write_float32_array(pivot_point)

    def save_bind_pose_chunk(self, stream: BinaryStream):
        if len(self.bind_pose):
            stream.write('BPOS')
            stream.write_uint32(4 + len(self.bind_pose) * 48)
            stream.write_uint32(len(self.bind_pose))
            for matrix in self.bind_pose:
                stream.write_float32_array(matrix)

    def load_mdl(self, stream):
        token = ''
        while token is not None:
            if token is None:
                break
            else:
                token = stream.read_token()
            if token == 'Version':
                self.load_version_block(stream)
            elif token == 'Model':
                self.load_model_block(stream)
            elif token == 'Sequences':
                self.load_numbered_object_block(self.sequences, Sequence, 'Anim', stream)
            elif token == 'GlobalSequences':
                self.load_global_sequence_block(stream)
            elif token == 'Textures':
                self.load_numbered_object_block(self.textures, Texture, 'Bitmap', stream)
            elif token == 'Materials':
                self.load_numbered_object_block(self.materials, Material, 'Material', stream)
            elif token == 'TextureAnims':
                self.load_numbered_object_block(self.texture_animations, TextureAnimation, 'TVertexAnim', stream)
            elif token == 'Geoset':
                self.load_object(self.geosets, Geoset, stream)
            elif token == 'GeosetAnim':
                self.load_object(self.geoset_animations, GeosetAnimation, stream)
            elif token == 'Bone':
                self.load_object(self.bones, Bone, stream)
            elif token == 'Light':
                self.load_object(self.lights, Light, stream)
            elif token == 'Helper':
                self.load_object(self.helpers, Helper, stream)
            elif token == 'Attachment':
                self.load_object(self.attachments, Attachment, stream)
            elif token == 'PivotPoints':
                self.load_pivot_point_block(stream)
            elif token == 'ParticleEmitter':
                self.load_object(self.particle_emitters, ParticleEmitter, stream)
            elif token == 'ParticleEmitter2':
                self.load_object(self.particle_emitters2, ParticleEmitter2, stream)
            elif token == 'ParticleEmitterPopcorn':
                self.load_object(self.particle_emitters_popcorn, ParticleEmitterPopcorn, stream)
            elif token == 'RibbonEmitter':
                self.load_object(self.ribbon_emitters, RibbonEmitter, stream)
            elif token == 'Camera':
                self.load_object(self.cameras, Camera, stream)
            elif token == 'EventObject':
                self.load_object(self.event_objects, EventObject, stream)
            elif token == 'CollisionShape':
                self.load_object(self.collision_shapes, CollisionShape, stream)
            elif token == 'FaceFX':
                self.load_object(self.face_effects, FaceEffect, stream)
            elif token == 'BindPose':
                self.load_bind_pose_block(stream)
            elif token is None:
                break
            else:
                raise ValueError(f'Unsupported block: {token}')

    def load_version_block(self, stream: TokenStream):
        for token in stream.read_block():
            if token == 'FormatVersion':
                self.version = stream.read_int()
            else:
                raise TokenStreamError('Version', token)

    def load_model_block(self, stream: TokenStream):
        self.name = stream.read()
        for token in stream.read_block():
            if token.startswith('Num'):
                stream.read()
            elif token == 'BlendTime':
                self.blend_time = stream.read_int()
            elif token == 'MinimumExtent':
                self.extent.min = stream.read_vector(3)
            elif token == 'MaximumExtent':
                self.extent.max = stream.read_vector(3)
            elif token == 'BoundsRadius':
                self.extent.bounds_radius = stream.read_float()
            elif token == 'AnimationFile':
                self.animation_file = stream.read()
            else:
                raise TokenStreamError('Model', token)

    def load_numbered_object_block(self, out, class_name, name, stream: TokenStream):
        stream.read()
        for token in stream.read_block():
            if token == name:
                obj = class_name()
                obj.read_mdl(stream)
                out.append(obj)
            else:
                raise TokenStreamError(name, token)

    def load_global_sequence_block(self, stream: TokenStream):
        stream.read()
        for token in stream.read_block():
            if token == 'Duration':
                self.global_sequences.append(stream.read_int())
            else:
                raise TokenStreamError('GlobalSequences', token)

    def load_object(self, out, class_name, stream: TokenStream):
        obj = class_name()
        obj.read_mdl(stream)
        out.append(obj)

    def load_pivot_point_block(self, stream: TokenStream):
        count = stream.read_int()
        stream.read()
        for i in range(count):
            self.pivot_points.append(stream.read_vector(3))
        stream.read()

    def load_bind_pose_block(self, stream: TokenStream):
        for token in stream.read_block():
            if token == 'Matrices':
                matrices = stream.read_int()
                stream.read()
                for i in range(matrices):
                    self.bind_pose.append(stream.read_vector(12))
                stream.read()
            else:
                raise TokenStreamError('BindPose', token)

    def save_mdl(self, comment=None):
        stream = TokenStream()
        tmp_file = open('tmp.data', 'a')
        stream.tmp_file = tmp_file
        if comment:
            #  comment[-1:] += Model.get_current_date_with_time_format()
            stream.write_comment(comment)
        self.save_version_block(stream)
        self.save_model_block(stream)
        self.save_static_objects_block(stream, 'Sequences', self.sequences)
        self.save_global_sequence_block(stream)
        self.save_static_objects_block(stream, 'Textures', self.textures)
        self.save_static_objects_block(stream, 'Materials', self.materials)
        self.save_static_objects_block(stream, 'TextureAnims', self.texture_animations)
        self.save_objects(stream, self.geosets)
        self.save_objects(stream, self.geoset_animations)
        self.save_objects(stream, self.bones)
        self.save_objects(stream, self.lights)
        self.save_objects(stream, self.helpers)
        self.save_objects(stream, self.attachments)
        self.save_pivot_point_block(stream)
        self.save_objects(stream, self.particle_emitters)
        self.save_objects(stream, self.particle_emitters2)
        if self.version > 800:
            self.save_objects(stream, self.particle_emitters_popcorn)
        self.save_objects(stream, self.ribbon_emitters)
        self.save_objects(stream, self.cameras)
        self.save_objects(stream, self.event_objects)
        self.save_objects(stream, self.collision_shapes)
        if self.version > 800:
            self.save_objects(stream, self.face_effects)
            self.save_bind_pose_block(stream)
        stream.tmp_file.close()
        with open('tmp.data', 'r') as f:
            stream.buffer = f.read()
        os.remove('tmp.data')
        return stream.buffer

    def save_version_block(self, stream: TokenStream):
        stream.start_block('Version', None)
        stream.write_number_attrib('FormatVersion', self.version)
        stream.end_block()

    def save_model_block(self, stream: TokenStream):
        stream.start_object_block('Model', self.name)
        self.mdl_num_of_chunk = [len(self.geosets), len(self.geoset_animations), len(self.helpers), len(self.lights),
                                 len(self.bones), len(self.attachments), len(self.particle_emitters),
                                 len(self.particle_emitters2), len(self.particle_emitters_popcorn),
                                 len(self.ribbon_emitters), len(self.event_objects), len(self.face_effects)]
        stream.write_number_attrib('NumGeosets', self.mdl_num_of_chunk[0])
        stream.write_number_attrib('NumGeosetAnims', self.mdl_num_of_chunk[1])
        stream.write_number_attrib('NumHelpers', self.mdl_num_of_chunk[2])
        stream.write_number_attrib('NumLights', self.mdl_num_of_chunk[3])
        stream.write_number_attrib('NumBones', self.mdl_num_of_chunk[4])
        stream.write_number_attrib('NumAttachments', self.mdl_num_of_chunk[5])
        stream.write_number_attrib('NumParticleEmitters', self.mdl_num_of_chunk[6])
        stream.write_number_attrib('NumParticleEmitters2', self.mdl_num_of_chunk[7])
        if self.version > 800:
            stream.write_number_attrib('NumParticleEmittersPopcorn', self.mdl_num_of_chunk[8])
        stream.write_number_attrib('NumRibbonEmitters', self.mdl_num_of_chunk[9])
        stream.write_number_attrib('NumEvents', self.mdl_num_of_chunk[10])
        if self.version > 800:
            stream.write_number_attrib('NumFaceFX', self.mdl_num_of_chunk[11])
        stream.write_number_attrib('BlendTime', self.blend_time)
        self.extent.write_mdl(stream)
        if len(self.animation_file):
            stream.write_string_attrib('AnimationFile', self.animation_file)
        stream.end_block()

    def save_static_objects_block(self, stream: TokenStream, name, objects):
        if len(objects):
            stream.start_block(name, len(objects))
            for obj in objects:
                obj.write_mdl(stream, version=self.version)
            stream.end_block()

    def save_global_sequence_block(self, stream: TokenStream):
        if len(self.global_sequences):
            stream.start_block('GlobalSequences', len(self.global_sequences))
            for global_sequence in self.global_sequences:
                stream.write_number_attrib('Duration', global_sequence)
            stream.end_block()

    def save_objects(self, stream: TokenStream, objects):
        for obj in objects:
            obj.write_mdl(stream, version=self.version)

    def save_pivot_point_block(self, stream: TokenStream):
        if len(self.pivot_points):
            stream.start_block('PivotPoints', len(self.pivot_points))
            for pivot_point in self.pivot_points:
                stream.write_vector(pivot_point)
            stream.end_block()

    def save_bind_pose_block(self, stream: TokenStream):
        if len(self.bind_pose):
            stream.start_block('BindPose', None)
            stream.start_block('Matrices', len(self.bind_pose))
            for matrix in self.bind_pose:
                stream.write_vector(matrix)
            stream.end_block()
            stream.end_block()

    def get_byte_length(self):
        size = 396
        size += self.get_static_objects_chunk_byte_length(self.sequences, 132)
        size += self.get_static_objects_chunk_byte_length(self.global_sequences, 4)
        size += self.get_dynamic_objects_chunk_byte_length(self.materials)
        size += self.get_static_objects_chunk_byte_length(self.textures, 268)
        size += self.get_dynamic_objects_chunk_byte_length(self.texture_animations)
        size += self.get_dynamic_objects_chunk_byte_length(self.geosets)
        size += self.get_dynamic_objects_chunk_byte_length(self.geoset_animations)
        size += self.get_dynamic_objects_chunk_byte_length(self.bones)
        size += self.get_dynamic_objects_chunk_byte_length(self.lights)
        size += self.get_dynamic_objects_chunk_byte_length(self.helpers)
        size += self.get_dynamic_objects_chunk_byte_length(self.attachments)
        size += self.get_static_objects_chunk_byte_length(self.pivot_points, 12)
        size += self.get_dynamic_objects_chunk_byte_length(self.particle_emitters)
        size += self.get_dynamic_objects_chunk_byte_length(self.particle_emitters2)
        if self.version > 800:
            size += self.get_dynamic_objects_chunk_byte_length(self.particle_emitters_popcorn)
        size += self.get_dynamic_objects_chunk_byte_length(self.ribbon_emitters)
        size += self.get_dynamic_objects_chunk_byte_length(self.cameras)
        size += self.get_dynamic_objects_chunk_byte_length(self.event_objects)
        size += self.get_dynamic_objects_chunk_byte_length(self.collision_shapes)
        if self.version > 800:
            size += self.get_static_objects_chunk_byte_length(self.face_effects, 340)
            size += self.get_bind_pose_chunk_byte_length()
        size += self.get_objects_byte_length(self.unknown_chunks)
        return size

    def get_objects_byte_length(self, objects):
        size = 0
        for obj in objects:
            size += obj.get_byte_length(version=self.version)
        return size

    def get_dynamic_objects_chunk_byte_length(self, objects):
        if len(objects):
            return 8 + self.get_objects_byte_length(objects)
        return 0

    def get_static_objects_chunk_byte_length(self, objects, size):
        if len(objects):
            return 8 + len(objects) * size
        return 0

    def get_bind_pose_chunk_byte_length(self):
        if len(self.bind_pose):
            return 12 + len(self.bind_pose) * 48
        return 0
