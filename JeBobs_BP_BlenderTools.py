bl_info = {
	"name": "JeBobs Burnout Paradise Blender Helpers",
	"description": "Helper tools to work in tandem with DGIorio's Burnout Paradise Blender Tools",
	"author": "JeBobs",
	"version": (0, 1),
	"blender": (3, 0, 0),
	"location": "3D View or Search",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"support": "COMMUNITY",
	"category": "Workflow"
	}

import json
import os
import bpy
import bmesh
from bpy.props import StringProperty, BoolProperty, IntProperty
from bpy.types import Operator
import re
from bpy_extras.io_utils import ImportHelper

def get_object_property(property, obj):
	if property in obj:
		return obj[property]
	else:
		return 0
	
def extract_number(name):
	match = re.search(r'_(\d+)', name)
	return match.group(1) if match else '000'
		
class SplitMesh(bpy.types.Operator):
	bl_idname = "object.split_mesh"
	bl_label = "Split Mesh"

	def execute(self, context):
		original_mesh = context.active_object
		if original_mesh is None or original_mesh.type != 'MESH':
			self.report({'ERROR'}, "No active mesh object selected")
			return {'CANCELLED'}

		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.select_all(action='DESELECT')
		bpy.ops.object.mode_set(mode='OBJECT')

		while len(original_mesh.data.vertices) >= 255:
			selected_vertices = 0
			for poly in original_mesh.data.polygons:
				if selected_vertices + len(poly.vertices) > 255:
					break
				poly.select = True
				selected_vertices += len(poly.vertices)

			bpy.ops.object.mode_set(mode='EDIT')
			bpy.ops.mesh.separate(type='SELECTED')
			bpy.ops.object.mode_set(mode='OBJECT')

			new_mesh = context.selected_objects[0]
			identifier = self.get_next_identifier()
			new_mesh.name = "PolygonSoupMesh_{:03d}".format(identifier)
			new_mesh.data.name = new_mesh.name
			new_mesh.location = original_mesh.location
			new_mesh.rotation_euler = original_mesh.rotation_euler
			new_mesh.scale = original_mesh.scale

		return {'FINISHED'}

	def get_next_identifier(self):
		existing_identifiers = []
		for obj in bpy.context.scene.objects:
			if obj.name.startswith('PolygonSoupMesh_'):
				try:
					identifier = int(obj.name[16:].split('.')[0])
					existing_identifiers.append(identifier)
				except ValueError:
					pass

		existing_identifiers.sort()
		for i in range(1, len(existing_identifiers) + 2):
			if i not in existing_identifiers:
				return i


class BPCreatePolygonSoup(bpy.types.Operator):
	bl_idname = "object.bp_create_polygon_soup"
	bl_label = "BP - Create Polygon Soup"

	def execute(self, context):
		bpy.ops.object.split_mesh()
	
		for obj in bpy.context.selected_objects:
			if obj.type == 'MESH':
				bpy.context.view_layer.objects.active = obj
				bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')
				original_location = obj.matrix_world.translation.copy()
				mesh_name = obj.name
				number = extract_number(mesh_name)
				empty_name = f"PolygonSoup_{number}"
				bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
				empty = bpy.context.object
				empty.name = empty_name
				empty.rotation_euler = (1.5708, 0, 1.5708)
				empty.scale = (0.015, 0.015, 0.015)
				obj.rotation_euler = (obj.rotation_euler.to_matrix() @ empty.rotation_euler.to_matrix().inverted()).to_euler()
				obj.scale = (
					obj.scale[0] / empty.scale[0],
					obj.scale[1] / empty.scale[1],
					obj.scale[2] / empty.scale[2]
				)
				bpy.context.view_layer.objects.active = obj
				obj.select_set(True)
				bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
				obj.parent = empty
				empty.location = original_location
				empty.rotation_euler = (1.5708, 0, 1.5708)
				empty.scale = (0.015, 0.015, 0.015)
				obj.location = (0, 0, 0)
				obj.rotation_euler = (0, 0, 0)
					
		return {'FINISHED'}

class BPDeleteLODRenderables(bpy.types.Operator):
	"""Delete LOD renderables from scene"""
	bl_idname = "object.bp_delete_lod_renderables"
	bl_label = "BP - Delete LOD Renderables"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		objects = bpy.context.scene.objects

		for obj in objects:
			renderable_index = get_object_property("renderable_index", obj)

			if renderable_index > 0:
				bpy.data.objects.remove(obj)
		return {'FINISHED'}

class BPDeleteSharedAssets(bpy.types.Operator):
	"""Delete shared TRK assets from scene"""
	bl_idname = "object.bp_delete_shared_assets"
	bl_label = "BP - Delete Shared Assets"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		objects = bpy.context.scene.objects

		for obj in objects:
			is_shared_asset = get_object_property("is_shared_asset", obj)

			if is_shared_asset > 0:
				bpy.data.objects.remove(obj)

		return {'FINISHED'}

class BPCreateCarEmpties(bpy.types.Operator):
		"""Create the needed empties for baseline Paradise cars."""
		bl_idname = "object.create_car_empties"
		bl_label = "BP - Create Car Empties"
		bl_options = {'REGISTER', 'UNDO'}

		def execute(self, context):
			# List of empty names to create
			empty_names = ["Wheel_FL", "Wheel_FR", "Wheel_RL", "Wheel_RR", "Boost_L1", "Boost_L2", "Boost_R1", "Boost_R2", "Light_BrakeL", "Light_BrakeR", "Light_Brake", "Light_High-BeamL", "Light_High-BeamR", "Light_High-Beam", "Light_BlinkerL", "Light_BlinkerR", "Light_Blinker", "Light_TailL", "Light_TailR", "Light_Tail", "Light_ReversingL", "Light_ReversingR", "Light_Reversing"]
	
			# Iterate over the empty names and create an empty for each one
			for name in empty_names:
				bpy.ops.object.add(type='EMPTY')
				active = bpy.context.active_object
				active.name = name
				
				# TODO: Move this into its own def and create a menu option to reset their positions

				# Find left/right orientation, if marked "1" or "2" 
				# then find the second to last character in the name (i.e. Boost_L1)
				index = -1
				if int(name.endswith("1")):
					index = index - 1
					active.matrix_world[2][3] = -0.125
				if int(name.endswith("2")):
					index = index - 1
					active.matrix_world[2][3] = -0.25

				if "Wheel_" in name:
					active.matrix_world[2][3] = -1

				# Check if the marker is left or right
				if name[index] == "R":
					# If it's "R", set X to 1
					active.matrix_world[0][3] = 1
				elif name[index] == "L":
					# If it's "L", set X to -1
					active.matrix_world[0][3] = -1

				# Reversing, taillights, blinkers, brakes, back wheels, and boosts in the back
				if "Reversing" in name or "Tail" in name or "Blinker" in name or "Brake" in name or "Boost" in name:
					active.matrix_world[1][3] = -2
				# High Beams, front wheels in the front
				elif "High-Beam" in name:				
						active.matrix_world[1][3] = 2

				if "Wheel_F" in name:
					active.matrix_world[1][3] = 1
				elif "Wheel_R" in name:
					active.matrix_world[1][3] = -1

				# Move everything up by one unit (it's too low normally)
				active.matrix_world[2][3] = active.matrix_world[2][3] + 1

				print(name + " Location: " + str(active.matrix_world))

			return {'FINISHED'}
		
class BPNameFromResourceDB(Operator, ImportHelper):
	"""BP - Name from Resource DB"""
	bl_idname = "object.name_from_resource_db"
	bl_label = "BP - Name from Resource DB"
	bl_options = {'REGISTER', 'UNDO'}

	use_filter_folder = True  # Allow folder selection
	
	directory: StringProperty(
		name="Directory",
		description="Folder containing JSON files",
		subtype='DIR_PATH'
	)

	def clean_name(self, full_name):
		"""
		Clean up the name by removing .Material, .Texture, .Object, and ?ID= parts.
		"""
		name = full_name.split(".")[0]
		name = name.split("?ID=")[0]
		name = re.sub(r"_LOD\d+", "", name)
		return name

	def find_name_by_id(self, json_data, object_id):
		"""
		Look for a matching name based on the object_id (GameExplorerIndex) in the JSON data.
		"""
		for key, value in json_data.items():
			match = re.search(r"\?ID=(\d+)", value)
			if match and match.group(1) == str(object_id):
				return self.clean_name(value.split("/")[-1])
		return None

	def execute(self, context):
		if not os.path.exists(self.directory):
			self.report({'ERROR'}, f"Path not found: {self.directory}")
			return {'CANCELLED'}

		json_data = {}
		for filename in os.listdir(self.directory):
			if filename.endswith(".json"):
				with open(os.path.join(self.directory, filename), 'r') as json_file:
					data = json.load(json_file)
					json_data.update({k.lower(): v for k, v in data.items()})
		
		for material in bpy.data.materials:
			if "_" in material.name:
				material_id = material.name.replace("_", "").lower()
				if material_id in json_data:
					new_name = json_data[material_id].split("/")[-1]
					cleaned_name = self.clean_name(new_name)
					material.name = cleaned_name
					self.report({'INFO'}, f"Renamed material {material_id} to {cleaned_name}")
		
		for texture in bpy.data.textures:
			if "_" in texture.name:
				texture_id = texture.name.replace("_", "").lower()
				if texture_id in json_data:
					new_name = json_data[texture_id].split("/")[-1]
					cleaned_name = self.clean_name(new_name)
					texture.name = cleaned_name
					self.report({'INFO'}, f"Renamed texture {texture_id} to {cleaned_name}")

		for obj in bpy.data.objects:
			if "_" in obj.name:
				object_id = obj.name.replace("_", "").lower()
				if object_id in json_data:
					new_name = json_data[object_id].split("/")[-1]
					cleaned_name = self.clean_name(new_name)
					obj.name = cleaned_name
					self.report({'INFO'}, f"Renamed object {object_id} to {cleaned_name}")
				else:
					if "GameExplorerIndex" in obj:
						game_explorer_index = obj["GameExplorerIndex"]
						name_by_id = self.find_name_by_id(json_data, game_explorer_index)
						if name_by_id:
							obj.name = name_by_id
							self.report({'INFO'}, f"Renamed object by GameExplorerIndex {game_explorer_index} to {name_by_id}")

		return {'FINISHED'}
	
class BPDeletePropParts(bpy.types.Operator):
	"""BP - Delete Prop Parts"""
	bl_idname = "object.delete_prop_parts"
	bl_label = "BP - Delete Prop Parts"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		objects_to_delete = []

		for obj in bpy.context.scene.objects:
			if "prop_type" in obj:
				if obj["prop_type"] == "prop_part":
					objects_to_delete.append(obj)
					objects_to_delete.extend(obj.children)
		
		for obj in objects_to_delete:
			bpy.data.objects.remove(obj, do_unlink=True)

		self.report({'INFO'}, f"Deleted {len(objects_to_delete)} prop parts")
		return {'FINISHED'}
	
class BPDeletePropAlternatives(bpy.types.Operator):
	"""BP - Delete Prop Alternatives"""
	bl_idname = "object.delete_prop_alternatives"
	bl_label = "BP - Delete Prop Alternatives"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		objects_to_delete = []

		for obj in bpy.context.scene.objects:
			if "prop_type" in obj:
				if obj["prop_type"] == "prop_alternative":
					objects_to_delete.append(obj)
					objects_to_delete.extend(obj.children)
		
		for obj in objects_to_delete:
			bpy.data.objects.remove(obj, do_unlink=True)

		self.report({'INFO'}, f"Deleted {len(objects_to_delete)} alternative props")
		return {'FINISHED'}


class BPDeleteBackdrops(bpy.types.Operator):
	"""BP - Delete Backdrops"""
	bl_idname = "object.delete_backdrop_objects"
	bl_label = "BP - Delete Backdrops"
	bl_options = {'REGISTER', 'UNDO'}

	name_substrings = ["BD_", "BdZone", "_backdrop"]

	def execute(self, context):
		objects_to_delete = set()

		for obj in bpy.context.scene.objects:
			if any(substring.lower() in obj.name.lower() for substring in self.name_substrings):
				objects_to_delete.add(obj)
				objects_to_delete.update(obj.children)
		
		for obj in objects_to_delete:
			bpy.data.objects.remove(obj, do_unlink=True)

		self.report({'INFO'}, f"Deleted {len(objects_to_delete)} backdrop objects")
		return {'FINISHED'}


def register():
	bpy.utils.register_class(BPDeleteLODRenderables)
	bpy.utils.register_class(BPDeleteSharedAssets)
	bpy.utils.register_class(BPCreateCarEmpties)
	bpy.utils.register_class(BPCreatePolygonSoup)
	bpy.utils.register_class(BPDeletePropParts)
	bpy.utils.register_class(BPDeletePropAlternatives)
	bpy.utils.register_class(BPDeleteBackdrops)
	bpy.utils.register_class(BPNameFromResourceDB)
	bpy.utils.register_class(SplitMesh)

	bpy.types.VIEW3D_MT_object.append(object_menu_func)
	bpy.types.VIEW3D_MT_add.append(add_menu_func)


def unregister():
	bpy.utils.unregister_class(BPDeleteLODRenderables)
	bpy.utils.unregister_class(BPDeleteSharedAssets)
	bpy.utils.unregister_class(BPCreateCarEmpties)
	bpy.utils.unregister_class(BPDeletePropParts)
	bpy.utils.unregister_class(BPDeletePropAlternatives)
	bpy.utils.unregister_class(BPDeleteBackdrops)
	bpy.utils.unregister_class(BPCreatePolygonSoup)
	bpy.utils.unregister_class(BPNameFromResourceDB)
	bpy.utils.unregister_class(SplitMesh)

	bpy.types.VIEW3D_MT_object.remove(object_menu_func)
	bpy.types.VIEW3D_MT_add.remove(add_menu_func)

def object_menu_func(self, context):
	self.layout.operator(BPNameFromResourceDB.bl_idname)
	self.layout.operator(BPDeleteLODRenderables.bl_idname)
	self.layout.operator(BPDeleteSharedAssets.bl_idname)
	self.layout.operator(BPDeletePropParts.bl_idname)
	self.layout.operator(BPDeletePropAlternatives.bl_idname)
	self.layout.operator(BPDeleteBackdrops.bl_idname)
	self.layout.operator(BPCreatePolygonSoup.bl_idname)

def add_menu_func(self, context):
	self.layout.operator(BPCreateCarEmpties.bl_idname)
