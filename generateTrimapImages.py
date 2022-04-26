import argparse
import os
from matplotlib import image
import numpy as np
import cv2
from scipy.ndimage.morphology import binary_erosion

IMG_EXT = ('.png', '.jpg', '.jpeg', '.JPG', '.JPEG')

trimap_erode_size = 10
trimap_fill_value = 128


def trimap(
    mask,
    foreground_threshold=250,
    background_threshold=5,
):
    is_foreground = mask > foreground_threshold
    is_background = mask < background_threshold
    structure = None
    if trimap_erode_size > 0:
        structure = np.ones(
            (trimap_erode_size, trimap_erode_size), dtype=np.int32)

    is_foreground = binary_erosion(is_foreground, structure=structure)
    is_background = binary_erosion(is_background, structure=structure, border_value=1)

    trimap = np.full(mask.shape, dtype=np.uint8, fill_value=trimap_fill_value)
    trimap[is_foreground] = 255
    trimap[is_background] = 0

    return trimap


def main(cfg):
    input_dir = cfg.input_dir
    trimaps_path = cfg.output_dir
    os.makedirs(trimaps_path, exist_ok=True)

    images_list = os.listdir(input_dir)
    for filename in images_list:
        if not filename.endswith(IMG_EXT):
            continue

        input_image = cv2.imread(os.path.join(input_dir, filename))
        input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
        trimap_image = trimap(input_image)
        trimap_filename = filename
        cv2.imwrite(os.path.join(trimaps_path, trimap_filename), trimap_image)
        print('done {}'.format(trimap_filename))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', type=str, default=None)
    parser.add_argument('--output_dir', type=str, default=None)
    config = parser.parse_args()
    main(config)
