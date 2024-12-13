from depth_from_normals.height_map import (
    estimate_height_map,
)  # Local file 'height_map.py' in this repository.
from matplotlib import pyplot as plt
import numpy as np
from skimage import io
import argparse

parser = argparse.ArgumentParser(description="3D reconstruction from normal map")
parser.add_argument("-i", "--input", type=str, required=True, help="Path to the input normal map image")
parser.add_argument('-o', '--out', type=str, required=True, help='Directory where the output images will be saved')
parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
args = parser.parse_args()

def save_obj(vertices, faces, filename):
    with open(filename, 'w') as file:
        for v in vertices:
            file.write(f"v {v[0]} {v[1]} {v[2]}\n")
        for f in faces:
            file.write(f"f {f[0]} {f[1]} {f[2]}\n")

def create_mesh_from_height_map(heights):
    rows, cols = heights.shape
    vertices = []
    faces = []
    
    for y in range(rows):
        for x in range(cols):
            vertices.append((x, y, 10 * heights[y, x]))
    
    for y in range(rows - 1):
        for x in range(cols - 1):
            v1 = y * cols + x + 1
            v2 = v1 + 1
            v3 = v1 + cols
            v4 = v3 + 1
            faces.append((v1, v2, v4))
            faces.append((v1, v4, v3))
    
    return vertices, faces

def main():
    print('surface reconstruction from normal map')
    normal_img: np.ndarray = io.imread(args.input)

    heights = estimate_height_map(normal_img, raw_values=True)

    # (dbg) plotting the normal map and the estimated height map
    if args.debug:
        figure, axes = plt.subplots(1, 2, figsize=(7, 3))
        _ = axes[0].imshow(normal_img)
        _ = axes[1].imshow(heights)

        x, y = np.meshgrid(range(heights.shape[1]), range(heights.shape[0]))
        _, axes = plt.subplots(1, 1, subplot_kw={"projection": "3d"})
        _ = axes.scatter(x, y, heights, c=heights)

    vertices, faces = create_mesh_from_height_map(heights)

    out_path = args.out if args.out else 'output.obj'
    save_obj(vertices, faces, out_path)

    if args.debug:
        plt.show()

    print(f"Surface reconstruction saved to {out_path}")

main()