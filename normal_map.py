import math
import argparse
import os
from PIL import Image, ImageFilter
import numpy as np

print("Normal map generation")

ALPHA = math.pi/6

parser = argparse.ArgumentParser(description="Create a normal map from a set of scanned images")
parser.add_argument('-i', '--in_dir', type=str, required=True, help='Directory where the input images are located')
parser.add_argument('-o', '--out', type=str, required=True, help='Directory where the normal map will be saved')
args = parser.parse_args()
in_dir = args.in_dir

image_paths = [os.path.join(in_dir, f) for f in os.listdir(in_dir) if os.path.isfile(os.path.join(in_dir, f)) and '_aligned' not in f]

def load_image(image_path):
    image = Image.open(image_path)
    return image

def load_image_brightness(image):
    image = image.convert('L')
    # image = image.filter(ImageFilter.GaussianBlur(radius=4))
    return np.array(image, dtype=np.int16)

I_0_img = None
I_90_img = None
I_180_img = None
I_270_img = None

I_0 = None
I_90 = None
I_180 = None
I_270 = None

for path in image_paths:
    if '_0' in path:
        I_0_img = load_image(path)
        I_0 = load_image_brightness(I_0_img)
    elif '_90' in path:
        I_90_img = load_image(path)
        I_90 = load_image_brightness(I_90_img)
    elif '_180' in path:
        I_180_img = load_image(path)
        I_180 = load_image_brightness(I_180_img)
    elif '_270' in path:
        I_270_img = load_image(path)
        I_270 = load_image_brightness(I_270_img)

def compute_normal_map():

    # diff_270_90 = np.subtract(I_270, I_90)
    # diff_270_90 = np.subtract(diff_270_90, 127)
    diff_270_90 = (I_90 - I_270) # - 127
    diff_0_180 = (I_0 - I_180) # - 127
    # diff_270_90 = np.array(ImageChops.difference(I_270_img.convert('L'), I_90_img.convert('L')))
    # diff_0_180 = np.array(ImageChops.difference(I_0_img.convert('L'), I_180_img.convert('L')))

    # print("np: ", diff_270_90_np.shape, np.min(diff_270_90_np), np.max(diff_270_90_np))
    # print("pil: ", diff_270_90.shape, np.min(diff_270_90), np.max(diff_270_90))

    # np_pill_diff = np.abs(diff_270_90_np - diff_270_90)
    # Image.fromarray(np_pill_diff).show()

    # print("diff_270_90: ", np.min(diff_270_90), np.max(diff_270_90))

    n_x = diff_270_90 / (2 * math.tan(ALPHA))
    n_y = diff_0_180 / (2 * math.tan(ALPHA))
    n_z = np.average([I_0, I_90, I_180, I_270], axis=0)

    n_z_preview = Image.fromarray(n_z).convert('RGB')
    n_z_preview_data = np.array(n_z_preview)
    black_pixels = (n_z_preview_data == [0, 0, 0]).all(axis=2)
    n_z_preview_data[black_pixels] = [255, 0, 0]
    n_z_preview = Image.fromarray(n_z_preview_data)
    # n_z_preview.show()

    n_x = np.nan_to_num(n_x, nan=0)
    n_y = np.nan_to_num(n_y, nan=0)
    n_z = np.nan_to_num(n_z, nan=1)

    normals = np.dstack((n_x, n_y, n_z))
    norms = np.linalg.norm(normals, axis=2, keepdims=True)

    zero_normals = (normals == 0).all(axis=2)
    normals[zero_normals] = [0, 0, 1]

    normals /= norms

    return normals

def normal_map_visualization(normal_map):
    normal_map_visual = np.zeros_like(normal_map)
    # print("n_x: ", np.min(normal_map[:, :, 0]), np.max(normal_map[:, :, 0]))
    # print(np.min(normal_map[:, :, 1]), np.max(normal_map[:, :, 1]))
    # print(np.min(normal_map[:, :, 2]), np.max(normal_map[:, :, 2]))

    normal_map_visual[:, :, :2] = (normal_map[:, :, :2] + 1) / 2 * 255
    normal_map_visual[:, :, 2] = normal_map[:, :, 2] * 255
    normal_map_visual = normal_map_visual.astype(np.uint8)

    return Image.fromarray(normal_map_visual)

normal_map = compute_normal_map()
normal_map_visual = normal_map_visualization(normal_map)

out_path = args.out if args.out else 'normal_map.png'
normal_map_visual.save(out_path)

print("Normal map generated successfully.")
# normal_map_visual.show()