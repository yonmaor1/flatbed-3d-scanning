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
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, -angle, 1.0)
    return cv2.warpAffine(image, rotation_matrix, (w, h))

def crop_edges(image, crop_size=2, dpi=72):
    # Crop `crop_size` inches from each edge of the image

    crop_size_pixels = int(crop_size * dpi)  # Convert inches to pixels
    h, w = image.shape[:2]
    return image[crop_size:h-crop_size, crop_size:w-crop_size]

def find_bounding_box(image):
    # Convert to grayscale and threshold to find the object
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))
        return x, y, w, h
    return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python align.py <directory>")
        sys.exit(1)

    input_dir = sys.argv[1]
    if not os.path.isdir(input_dir):
        print(f"Error: {input_dir} is not a valid directory.")
        sys.exit(1)

    images = []
    angles = []
    for filename in sorted(os.listdir(input_dir)):
        if filename.endswith(".png"):
            filepath = os.path.join(input_dir, filename)
            image = cv2.imread(filepath)
            if image is None:
                print(f"Error: Unable to read {filepath}")
                sys.exit(1)
            
            dpi = get_image_dpi(filepath)[0]
            image = crop_edges(image, crop_size=2, dpi=dpi)
            angle = extract_angle_from_filename(filename)
            images.append(image)
            angles.append(angle)

    # Rotate images back to the orientation of *_0.png
    rotated_images = [rotate_image(image, angle) for image, angle in zip(images, angles)]

    comment = '''
    # Use the first image to determine the bounding box
    bbox = find_bounding_box(rotated_images[0])
    if bbox is None:
        print("Error: Unable to determine bounding box.")
        sys.exit(1)

    x, y, w, h = bbox

    # Crop all images around the bounding box
    cropped_images = [img[y:y+h, x:x+w] for img in rotated_images]

    # Save the cropped images
    output_dir = os.path.join(input_dir, "aligned")
    os.makedirs(output_dir, exist_ok=True)
    for _, (cropped, (_, angle)) in enumerate(zip(cropped_images, images)):
        output_path = os.path.join(output_dir, f"aligned_{angle}.png")
        cv2.imwrite(output_path, cropped)

    print(f"Aligned images saved to {output_dir}")

    '''

    # Calculate the arithmetic mean and standard deviation
    mean_image = get_arithmetic_mean(images)
    std_image = get_arithmetic_std(images)

    # Display the mean and standard deviation images
    cv2.imshow("Mean Image", mean_image.astype(np.uint8))
    cv2.imshow("Standard Deviation Image", std_image.astype(np.uint8))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
