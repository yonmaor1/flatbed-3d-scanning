bl_info = {
    "name": "Flatbed 3D Scan",
    "blender": (2, 80, 0),
    "category": "Object",
}

import bpy


class ObjectFlatbed3DScan(bpy.types.Operator):
    """Object Flatbed 3D Scan"""
    bl_idname = "object.flatbed_3d_scan"
    bl_label = "Flatbed 3D Scan"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Sample code
        # scene = context.scene
        # for obj in scene.objects:
        #     obj.location.x += 1.0

        # run Main.py from the command line
        import os
        
        # move to scanner controller directory
        # TODO: add option to change scan directory
        os.chdir("C:/Users/selki/OneDrive/Desktop/ExtraneousFiles/18-500/flatbed-3d-scanning")

        # call Main.py
        print("Running Main.py")
        os.system("python Main.py")

        print("Scan successful.")
        return {'FINISHED'}        # Lets Blender know the operator finished successfully.
        # else:
        #     print("Scan unsuccessful.")
        #     return {'CANCELLED'}       # Lets Blender know the operator was cancelled.


def menu_func(self, context):
    self.layout.operator(ObjectFlatbed3DScan.bl_idname)

# store keymaps here to access after registration
addon_keymaps = []


def register():
    bpy.utils.register_class(ObjectFlatbed3DScan)
    bpy.types.VIEW3D_MT_object.append(menu_func)

    # handle the keymap
    wm = bpy.context.window_manager
    # Note that in background mode (no GUI available), keyconfigs are not available either,
    # so we have to check this to avoid nasty errors in background case.
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new(ObjectFlatbed3DScan.bl_idname, 'T', 'PRESS', ctrl=True, shift=True)
        addon_keymaps.append((km, kmi))

def unregister():
    # Note: when unregistering, it's usually good practice to do it in reverse order you registered.
    # Can avoid strange issues like keymap still referring to operators already unregistered...
    # handle the keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_class(ObjectFlatbed3DScan)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    register()

# TODO: Update this to allow user to change scan directory
class ScanPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    scan_path: bpy.props.StringProperty

    scan_path = bpy.props.StringProperty(
        name="Scanner Directory",
        subtype='DIR_PATH',
        default="/mnt/c/Users/selki/OneDrive/Desktop/ExtraneousFiles/18-500/flatbed-3d-scanning"
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "scan_path")

def get_scan_path():
    return bpy.context.preferences.addons[__name__].preferences.scan_path