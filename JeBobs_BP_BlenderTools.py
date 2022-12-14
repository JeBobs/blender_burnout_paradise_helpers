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
	"category": "Workflow"}

import bpy

def get_object_property(property, obj):
	# Check if the object has the specificed custom property
	if property in obj:
		# Return the value of the custom property
		return obj[property]
	else:
		return 0

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


def register():
	bpy.utils.register_class(BPDeleteLODRenderables)
	bpy.utils.register_class(BPDeleteSharedAssets)
	bpy.utils.register_class(BPCreateCarEmpties)

	bpy.types.VIEW3D_MT_object.append(object_menu_func)
	bpy.types.VIEW3D_MT_add.append(add_menu_func)

def unregister():
	bpy.utils.unregister_class(BPDeleteLODRenderables)
	bpy.utils.unregister_class(BPDeleteSharedAssets)
	bpy.utils.unregister_class(BPCreateCarEmpties)

def object_menu_func(self, context):
	self.layout.operator(BPDeleteLODRenderables.bl_idname)
	self.layout.operator(BPDeleteSharedAssets.bl_idname)

def add_menu_func(self, context):
	self.layout.operator(BPCreateCarEmpties.bl_idname)

# This allows you to run the script directly from blenders text editor
# to test the addon without having to install it.
#if __name__ == "__main__":
#    register()