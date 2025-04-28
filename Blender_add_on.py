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
        result = subprocess.run(
            ["python", "Main.py", str(self.scan_number), self.path, str(self.dpi)],
            stdout=subprocess.PIPE,
            text=True
        )
        
        # find most recent scan folder
        scan_folder = "scan0"
        # sort folders by number and pick highest
        try:
            scans_path = os.path.join(self.path, "scanner-controller", "scanner-controller", "scans")
            scan_folders = [
                folder for folder in os.listdir(scans_path)
                if folder.startswith("scan") and folder[4:].isdigit()
            ]
            
            if scan_folders:
                scan_folders.sort(key=lambda f: int(f[4:]))
                scan_folder = scan_folders[-1]
        except:
            print("Scans folder not found.")


        height_map_path = self.path + "/scanner-controller/scanner-controller/scans/" + str(scan_folder) + "/height_map.png"
        print(f"Height map path: {height_map_path}")

        # load height map
        height_map = bpy.data.images.load(height_map_path)
            
        # create plane
        # TODO: Add option to change size?
        # find size of height map
        # Get image width and height
        img_width = height_map.size[0]
        img_height = height_map.size[1]

        bpy.ops.mesh.primitive_plane_add(size=1.00, enter_editmode=False, align='WORLD', location=(0, 0, 0))
        plane = bpy.context.active_object # set the active object (the plane)

        # scale plane to match image size
        scale = 0.1
        plane.scale.y = img_width * scale / 2  # Plane's original size is 2x2, need to divide by 2
        plane.scale.x = img_height * scale / 2

        # Subdivide it
        bpy.ops.object.mode_set(mode='EDIT')
        # Number of subdivisions is based on the DPI, may need to change?
        bpy.ops.mesh.subdivide(number_cuts=self.dpi)
        bpy.ops.object.mode_set(mode='OBJECT')

        # unwrap so texture doesn't repeat
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
        bpy.ops.object.mode_set(mode='OBJECT')

        # subdivision Surface modifier to smooth
        subd = plane.modifiers.new(name='Subdivision', type='SUBSURF')
        subd.levels = 2
        subd.render_levels = 2
        subd.subdivision_type = 'SIMPLE'

        # add displace with texture of image type
        displace = plane.modifiers.new(name='Displace', type='DISPLACE')
        texture = bpy.data.textures.new(name="HeightMapTex", type='IMAGE')

        texture.image = bpy.data.images.load(height_map_path)
        displace.texture = texture
        displace.strength = 0.4 # TODO: Add option to change?
        # might need to be LOCAL instead of UV?
        displace.texture_coords = 'UV'

        print("Scan successful.")

        return {'FINISHED'}        # Lets Blender know the operator finished successfully.

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
