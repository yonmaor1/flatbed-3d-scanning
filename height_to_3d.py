import bpy
import sys

def height_to_3d(scan_id, dpi):
    # Import the height map
    height_map_path = "scanner-controller/scanner-controller/scans/scan" + str(scan_id) + "/height_map.png"
    
    # create plane
    # TODO: Add option to change size?
    bpy.ops.mesh.primitive_plane_add(size=10.00, enter_editmode=False, align='WORLD', location=(0, 0, 0))
    plane = bpy.context.active_object # set the active object (the plane)

    # Subdivide it
    bpy.ops.object.mode_set(mode='EDIT')
    # Number of subdivisions is based on the DPI, may need to change?
    bpy.ops.mesh.subdivide(number_cuts=dpi)
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

if __name__ == "__main__":
  num = int(sys.argv[1])
  dpi = sys.argv[2]
  height_to_3d(num, dpi)