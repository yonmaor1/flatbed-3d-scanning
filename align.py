import cv2
import numpy as np
from PIL import Image
import os
import sys

def get_arithmetic_mean(images):
    # Calculate the arithmetic mean of an array of images
    return np.mean(images, axis=0)

def get_arithmetic_std(images):
    # Calculate the standard deviation of an array of images
    return np.std(images, axis=0)

def get_image_dpi(image_path):
    # Get the DPI of the image
    with Image.open(image_path) as img:
        dpi = img.info.get('dpi', (72, 72))  # Default to (72, 72) if DPI info is not available
        return dpi
    
def extract_angle_from_filename(filename):
    # Extract the angle from the filename (e.g., "*_90.png" -> 90)
    filename = os.path.splitext(filename)[0]
    angle = filename.split('_')[-1]
    return int(angle)

def rotate_image(image, angle):
    # Rotate the image by the specified angle

    # print(angle)
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, -angle, 1.0)
    return cv2.warpAffine(image, rotation_matrix, (w, h))

def crop_edges(image, crop_size=2, dpi=72):
    # Crop `crop_size` inches from each edge of the image

    crop_size_pixels = int(crop_size * dpi)  # Convert inches to pixels
    h, w = image.shape[:2]
    return image[crop_size_pixels:h-crop_size_pixels, 
                 crop_size_pixels:w-crop_size_pixels]

def find_bounding_box(image):
    # Convert to grayscale and threshold to find the object
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        # print(f"Found {len(contours)} contours.")
        x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))
        # print(f"Bounding box: x={x}, y={y}, w={w}, h={h}")

        # Draw the bounding box on the image for preview
        image_copy = image.copy()
        cv2.rectangle(image_copy, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Display the image with the bounding box for debugging
        # print("Original bounding box:")
        # cv2.imshow("Bounding Box Preview", image_copy)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        return x, y, w, h
    return None

def refine_bounding_box(image, bbox, images, angles):
    x, y, w, h = bbox
    size_small = min(w, h)
    size_large = max(w, h)

    candidates = []
    for size in [size_small, size_large]:
        # Generate 4 possible orientations for each square size
        candidates.append((x, y, size, size))  # Align left/top
        candidates.append((x + w - size, y, size, size))  # Align right/top
        candidates.append((x, y + h - size, size, size))  # Align left/bottom
        candidates.append((x + w - size, y + h - size, size, size))  # Align right/bottom

    best_bbox = None
    smallest_mse = float('inf')

    for candidate in candidates:
        cx, cy, cw, ch = candidate
        # Ensure the candidate bounding box is within image bounds
        if cx < 0 or cy < 0 or cx + cw > image.shape[1] or cy + ch > image.shape[0]:
            continue

        # Crop and rotate the images using the candidate bounding box
        cropped_images = [crop_by_bounding_box(img, candidate) for img in images]
        rotated_images = [rotate_image(img, -angle) for img, angle in zip(cropped_images, angles)]

        # Compute the mean rotated image
        mean_rotated_image = np.mean(rotated_images, axis=0)

        # Compute the Mean Squared Error (MSE) between the aligned images
        mse_sum = 0
        # for i in range(len(rotated_images)):
        #     for j in range(i + 1, len(rotated_images)):
        #         mse_sum += np.mean((rotated_images[i] - rotated_images[j]) ** 2)
        # mean_mse = mse_sum / (len(rotated_images) * (len(rotated_images) - 1) / 2)

        for rot_img in rotated_images:
            mse_sum += np.mean((mean_rotated_image - rot_img) ** 2)

        mean_mse = mse_sum / len(rotated_images) # should be 4

        # Update the best bounding box if the current one has a smaller MSE
        if mean_mse < smallest_mse:
            smallest_mse = mean_mse
            best_bbox = candidate
        

        # DEBUG Preview the mean rotated image
        # print(f"MMSE = {mean_mse}")
        # cv2.imshow(f"Mean Rotated Image", mean_rotated_image.astype(np.uint8))
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

    return best_bbox

def crop_by_bounding_box(image, bbox):
    # Crop the image using the bounding box
    x, y, w, h = bbox
    return image[y:y+h, x:x+w]

def main():
    if len(sys.argv) != 2:
        print("Usage: python align.py <directory>")
        sys.exit(1)

    input_dir = sys.argv[1]
    if not os.path.isdir(input_dir):
        print(f"Error: {input_dir} is not a valid directory.")
        sys.exit(1)

    print(f"Processing images in directory: {input_dir}")

    images = []
    angles = []
    for filename in sorted(os.listdir(input_dir)):
        if filename.endswith(".png"):
            try:
                filepath = os.path.join(input_dir, filename)
                image = cv2.imread(filepath)
                if image is None:
                    print(f"Error: Unable to read {filepath}")
                    sys.exit(1)
                
                dpi = get_image_dpi(filepath)[0]
                # image = crop_edges(image, crop_size=2, dpi=dpi)
                angle = extract_angle_from_filename(filename)
                images.append(image)
                angles.append(angle)
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                continue
    if len(images) != 4:
        print(f"Error: Expected 4 images, but found {len(images)}.")
        sys.exit(1)


    # Calculate the arithmetic mean and standard deviation
    mean_image = get_arithmetic_mean(images)
    std_image = get_arithmetic_std(images)
    std_image = 255 - std_image
    # std_image = cv2.normalize(std_image, None, 0, 255, cv2.NORM_MINMAX)


    # Find the bounding box on the standard deviation image
    bbox = find_bounding_box(std_image.astype(np.uint8))

    bbox = refine_bounding_box(image, bbox, images, angles)

    if bbox is not None:
        x, y, w, h = bbox

        cv2.rectangle(std_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        margin = 10

        # Adjust the bounding box to include a margin
        x -= margin
        y -= margin
        w += 2 * margin
        h += 2 * margin
        # Draw the bounding box on the standard deviation image
        cv2.rectangle(std_image, (x, y), (x + w, y + h), (255, 0, 0), 2)
    else:
        print("Error: Unable to determine bounding box on the standard deviation image.")

    if bbox is not None:
        x, y, w, h = bbox
        cv2.rectangle(std_image, (x, y), (x + w, y + h), (255, 0, 0), 2)
    else:
        print("Error: Unable to refine bounding box.")
        sys.exit(1)

    # DEBUG : Display the mean and standard deviation images
    # cv2.imshow("Mean Image", mean_image.astype(np.uint8))
    # cv2.imshow("Standard Deviation Image", std_image.astype(np.uint8))
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # Save the standard deviation image for debugging purposes
    std_image_path = os.path.join(f"{input_dir}/", "std_image.png")
    # cv2.imwrite(std_image_path, std_image.astype(np.uint8)) # DEBUG
    # print(f"Standard deviation image saved to {std_image_path}")

    # Crop each image using the bounding box
    cropped_images = [crop_by_bounding_box(image, bbox) for image in images]

    # Rotate images back to the orientation of *_0.png
    rotated_images = [rotate_image(image, -angle) for image, angle in zip(cropped_images, angles)]

    # Compute the mean rotated image
    mean_rotated_image = np.mean(rotated_images, axis=0)

    # Display the mean rotated image
    # cv2.imshow("Mean Rotated Image", mean_rotated_image.astype(np.uint8))
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()


    # Save the cropped images
    output_dir = os.path.join(input_dir, "aligned")
    if os.path.exists(output_dir):
        overwrite = input(f"Warning: {output_dir} already exists. Overwrite? [y/n]")
        if overwrite.lower() == 'y':
            print(f"Overwriting directory: {output_dir}")
            for filename in os.listdir(output_dir):
                filepath = os.path.join(output_dir, filename)
                if os.path.isfile(filepath):
                    os.remove(filepath)
        else:
            print("Exiting without saving.")
            sys.exit(0)
    else:
        print(f"Creating directory: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
    for image, angle in zip(rotated_images, angles):
        output_path = os.path.join(output_dir, f"aligned_{angle}.png")
        cv2.imwrite(output_path, image)

    print(f"Aligned images saved to {output_dir}")

if __name__ == "__main__":
    main()
