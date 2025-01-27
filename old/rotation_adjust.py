'''import cv2
import numpy as np
import os
import sys
import argparse

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 150)
    return edged

def find_contours(edged):
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def find_registration_pattern(contours):
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
        if len(approx) == 4: # assuming the grid is a rectangle
            return approx
    return None

def get_rotation_angle(pattern):
    rect = cv2.minAreaRect(pattern)
    angle = rect[-1]
    if angle < -45:
        angle += 90
    return angle

def rotate_image(image, angle):
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h))
    return rotated

def crop_to_pattern(image, pattern):
    x, y, w, h = cv2.boundingRect(pattern)
    return image[y:y+h, x:x+w]

def process_image(image_path):
    image = cv2.imread(image_path)
    edged = preprocess_image(image)
    contours = find_contours(edged)
    pattern = find_registration_pattern(contours)
    
    if pattern is not None:
        angle = get_rotation_angle(pattern)
        rotated_image = rotate_image(image, angle)
        cropped_image = crop_to_pattern(rotated_image, pattern)
        return cropped_image
    else:
        print(f"Registration pattern not found in {image_path}.")
        return None

def main():
    parser = argparse.ArgumentParser(description="Process images in a directory to align them based on a registration pattern.")
    parser.add_argument('-i', '--in_dir', type=str, required=True, help='Directory where the input images are located')
    args = parser.parse_args()
    in_dir = args.in_dir

    image_paths = [os.path.join(in_dir, f) for f in os.listdir(in_dir) if os.path.isfile(os.path.join(in_dir, f)) and '_aligned' not in f]

    for i, image_path in enumerate(image_paths):
        processed_image = process_image(image_path)
        if processed_image is not None:
            output_path = f"{image_path}_aligned.jpg"
            cv2.imwrite(output_path, processed_image)
            print(f"Saved aligned image to {output_path}")

if __name__ == "__main__":
    main()'''

import cv2
import numpy as np
import argparse
import os

def load_image(image_path):
    return cv2.imread(image_path)

def find_keypoints_and_descriptors(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    orb = cv2.ORB_create()
    keypoints, descriptors = orb.detectAndCompute(gray, None)
    return keypoints, descriptors

def match_features(descriptors1, descriptors2):
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descriptors1, descriptors2)
    matches = sorted(matches, key=lambda x: x.distance)
    return matches

def find_affine_transform(keypoints1, keypoints2, matches):
    src_pts = np.float32([keypoints1[m.queryIdx].pt for m in matches]).reshape(-1, 2)
    dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in matches]).reshape(-1, 2)
    M, _ = cv2.estimateAffinePartial2D(src_pts, dst_pts)
    return M

def align_images(image, pattern_image):
    keypoints1, descriptors1 = find_keypoints_and_descriptors(image)
    keypoints2, descriptors2 = find_keypoints_and_descriptors(pattern_image)
    matches = match_features(descriptors1, descriptors2)
    M = find_affine_transform(keypoints1, keypoints2, matches)
    height, width = image.shape[:2]
    aligned_image = cv2.warpAffine(image, M, (int(0.7 * width), int(0.7 * height)))
    return aligned_image, M

def process_images(image_paths, pattern_image_path):
    pattern_image = load_image(pattern_image_path)
    aligned_images = []
    transforms = []

    for image_path in image_paths:
        image = load_image(image_path)
        aligned_image, M = align_images(image, pattern_image)
        aligned_images.append(aligned_image)
        transforms.append(M)

    return aligned_images, transforms

def find_largest_common_rectangle(transforms, pattern_image):
    height, width = pattern_image.shape[:2]
    corners = np.array([[0, 0], [0, height], [width, 0], [width, height]], dtype=np.float32)
    transformed_corners = []

    for M in transforms:
        transformed = cv2.transform(np.array([corners]), M)[0]
        transformed_corners.append(transformed)

    all_corners = np.vstack(transformed_corners)
    min_x = np.max(all_corners[:, 0].min())
    min_y = np.max(all_corners[:, 1].min())
    max_x = np.min(all_corners[:, 0].max())
    max_y = np.min(all_corners[:, 1].max())

    return int(min_x), int(min_y), int(max_x), int(max_y)

def main(image_paths, pattern_image_path):
    aligned_images, transforms = process_images(image_paths, pattern_image_path)
    pattern_image = load_image(pattern_image_path)
    min_x, min_y, max_x, max_y = find_largest_common_rectangle(transforms, pattern_image)

    for i, aligned_image in enumerate(aligned_images):
        # cropped_image = aligned_image[min_y:max_y, min_x:max_x]
        output_path = f"{image_paths[i].split('.')[0]}_aligned.jpg"
        cv2.imwrite(output_path, aligned_image)
        print(f"Saved aligned image to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Align images based on a reference pattern.")
    parser.add_argument('-i', '--in_dir', type=str, required=True, help='Directory where the input images are located')
    parser.add_argument('-p', '--pattern', type=str, required=True, help='Path to the reference pattern image')
    args = parser.parse_args()
    in_dir = args.in_dir
    pattern_image_path = args.pattern

    image_paths = [os.path.join(in_dir, f) for f in os.listdir(in_dir) if os.path.isfile(os.path.join(in_dir, f)) and '_aligned' not in f]
    main(image_paths, pattern_image_path)