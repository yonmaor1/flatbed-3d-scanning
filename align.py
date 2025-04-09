import cv2
import numpy as np
import os
import sys

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
            angle = extract_angle_from_filename(filename)
            images.append((image, angle))
            angles.append(angle)

    # Rotate images back to the orientation of *_0.png
    rotated_images = [rotate_image(image, angle) for image, angle in images]

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

if __name__ == "__main__":
    main()
