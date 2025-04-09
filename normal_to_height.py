# Calls module for converting normal maps to height maps
import argparse
import numpy as np
import imageio.v3 as iio
import module_normals_to_height  # Ensure this module is in the same directory

# Parse CLI arguments
parser = argparse.ArgumentParser(description="Convert normal map to height map")
parser.add_argument("in_img_path", help="Path to the input normal map", type=str)
parser.add_argument("out_img_path", help="Path to save the output height map", type=str)
parser.add_argument("--seamless", choices=["TRUE", "FALSE"], default="FALSE")

args = parser.parse_args()

# Read input normal map
in_img = iio.imread(args.in_img_path)

# Ensure correct shape: H, W, C → C, H, W
if len(in_img.shape) == 3 and in_img.shape[2] == 3:
    in_img = np.transpose(in_img, (2, 0, 1)) / 255.0  # Normalize to [0,1]
else:
    raise ValueError("Error: Input image must be an RGB normal map.")

# Apply height map conversion
out_img = module_normals_to_height.apply(
    in_img, args.seamless == "TRUE", lambda x, y: print(f"{x}/{y}")
)

# Convert back to H, W, C in [0, 255]
out_img = (np.transpose(out_img, (1, 2, 0)) * 255).astype(np.uint8)

# Save output height map
iio.imwrite(args.out_img_path, out_img)