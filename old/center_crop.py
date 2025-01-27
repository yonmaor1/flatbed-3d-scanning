import cv2
import numpy as np
import argparse
import os

def load_image(image_path):
    return cv2.imread(image_path)

def warp_image(image, src_points, dst_points):
    M = cv2.getPerspectiveTransform(src_points, dst_points)
    height, width = image.shape[:2]
    warped_image = cv2.warpPerspective(image, M, (width, height))
    return warped_image

def crop_image(image, control_points):
    x_coords = [p[0] for p in control_points]
    y_coords = [p[1] for p in control_points]
    x_min, x_max = int(min(x_coords)), int(max(x_coords))
    y_min, y_max = int(min(y_coords)), int(max(y_coords))
    return image[y_min:y_max, x_min:x_max]

def save_image(image, output_path):
    cv2.imwrite(output_path, image)

def draw_control_points(image, control_points):
    for point in control_points:
        cv2.drawMarker(image, point.astype(np.int32), color=(0, 0, 255), markerType=cv2.MARKER_CROSS, markerSize=20, thickness=2)
    return image

def main(image_paths, control_points, output_paths):
    # Define the destination points (aligned control points)
    dst_points = np.array(control_points[0], dtype=np.float32)
    print(control_points)

    for i, image_path in enumerate(image_paths):
        image = load_image(image_path)
        src_points = np.array(control_points[i], dtype=np.float32)
        
        # # Draw control points on the image
        # image_with_points = draw_control_points(image.copy(), src_points)
        # cv2.imshow(f"Image with Control Points {i}", image_with_points)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        
        warped_image = warp_image(image, src_points, dst_points)
        cropped_image = crop_image(warped_image, dst_points)
        save_image(cropped_image, output_paths[i])
        print(f"Saved aligned and cropped image to {output_paths[i]}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Align images based on control points.")
    parser.add_argument("-i", "--input_dir", required=True, help="Input directory containing images")
    args = parser.parse_args()

    image_paths = [os.path.join(args.input_dir, f) for f in os.listdir(args.input_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
    image_paths.sort()

    output_dir = f"{args.input_dir}_aligned"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_paths = [os.path.join(output_dir, os.path.basename(f)) for f in image_paths]

    # Define the control points for each image (hardcoded for now)
    control_points = [
        [(1741, 2734), (1752, 1533), (2946, 1549), (2934, 2749)],  # Control points for 0
        [(2692, 2561 + 22), (1498, 2562 + 22), (1496, 1362 + 22), (2690, 1360 + 22)],  # Control points for 90
        [(2494 + 44, 1407 + 31), (2489 + 44, 2610 + 31), (1295 + 44, 2601 + 31), (1301 + 44, 1399 + 31)],  # Control points for 180
        [(1408 + 26, 1831), (2603 + 26, 1832), (2601 + 26, 3032), (1407 + 26, 3031)]   # Control points for 270
    ]

    main(image_paths, control_points, output_paths)