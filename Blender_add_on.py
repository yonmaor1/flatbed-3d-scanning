bl_info = {
    "name": "Flatbed 3D Scan",
    "blender": (2, 80, 0),
    "category": "Object",
}

import bpy


class WMFlatbed3DScan(bpy.types.Operator):
    """Object Flatbed 3D Scan"""
    bl_idname = "wm.flatbed_3d_scan"
    bl_label = "Flatbed 3D Scan"
    bl_options = {'REGISTER', 'UNDO'}

    # path variable
    path: bpy.props.StringProperty(
        name="Scan Directory",
        description="Directory that contains Main.py",
        default="//",
        maxlen=1024,
        subtype='DIR_PATH',
    )

    # scan number variable
    scan_number: bpy.props.IntProperty(
        name="Number of Scans",
        description="Number of scans and rotations",
        default=4,
        min=3,
        max=12,
    )

    dpi: bpy.props.IntProperty(
        name="DPI",
        description="DPI of the scan",
        default=300,
        min=100,
        max=4000,
    )

    def execute(self, context):
        # run Main.py from the command line
        import os
        import subprocess
        
        # move to configured Main.py directory
        os.chdir(self.path)

        # call Main.py
        print("Running Main.py")
        subprocess.run("python Main.py " + str(self.scan_number) + " " + self.path + " " + str(self.dpi))

        print("Scan successful.")

        return {'FINISHED'}        # Lets Blender know the operator finished successfully.
        # else:
        #     print("Scan unsuccessful.")
        #     return {'CANCELLED'}       # Lets Blender know the operator was cancelled.

    def invoke(self, context, event):
        # This is called when the operator is invoked.
        # It allows you to set up the operator's properties before executing it.
        # Brings up the dialogue box window
        return context.window_manager.invoke_props_dialog(self)


def menu_func(self, context):
    self.layout.operator(WMFlatbed3DScan.bl_idname)

# store keymaps here to access after registration
addon_keymaps = []


def register():
    bpy.utils.register_class(WMFlatbed3DScan)
    bpy.types.VIEW3D_MT_object.append(menu_func)

    # handle the keymap
    wm = bpy.context.window_manager
    # Note that in background mode (no GUI available), keyconfigs are not available either,
    # so we have to check this to avoid nasty errors in background case.
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new(WMFlatbed3DScan.bl_idname, 'T', 'PRESS', ctrl=True, shift=True)
        addon_keymaps.append((km, kmi))

def unregister():
    # Note: when unregistering, it's usually good practice to do it in reverse order you registered.
    # Can avoid strange issues like keymap still referring to operators already unregistered...
    # handle the keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.types.VIEW3D_MT_object.remove(menu_func)
    bpy.utils.unregister_class(WMFlatbed3DScan)


if __name__ == "__main__":
    register()

    bpy.ops.wm.flatbed_3d_scan('INVOKE_DEFAULT')
