import argparse
import os
import numpy as np
import cv2

IMG_EXT = ('.png', '.jpg', '.jpeg', '.JPG', '.JPEG')

trimap_erode_size = 5
trimap_dilate_size = 15
trimap_threshold = 200
trimap_dilate_value = 128

def trimap(mask, conf_threshold):
    h, w, _ = mask.shape
    maxW = max(h, w)
    scale = maxW / 1000
    erode_size = int(trimap_erode_size * scale)

    erode_kernel = np.ones((erode_size, erode_size), np.uint8)
    mask = cv2.erode(mask, erode_kernel) 

    dilate_Size = 2 * trimap_dilate_size + 1
    dilate_Size = int(dilate_Size * scale)
    dilate_kernel = np.ones((dilate_Size, dilate_Size), np.uint8)
    dilation = cv2.dilate(mask, dilate_kernel, iterations=2)

    remake = np.zeros_like(mask)
    remake[dilation == 255] = trimap_dilate_value  # Set every pixel within dilated region as probably foreground.
    remake[mask > conf_threshold] = 255  # Set every pixel with large enough probability as definitely foreground.

    return remake


def main(cfg):
    input_dir = cfg.input_dir
    trimaps_path = cfg.output_dir
    os.makedirs(trimaps_path, exist_ok=True)

    images_list = os.listdir(input_dir)
    for filename in images_list:
        if not filename.endswith(IMG_EXT):
            continue
        input_image = cv2.imread(os.path.join(input_dir, filename))
        input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
        trimap_image = trimap(input_image, trimap_threshold)
        trimap_filename = filename
        cv2.imwrite(os.path.join(trimaps_path, trimap_filename), trimap_image)
        print('done {}'.format(trimap_filename))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', type=str, default=None)
    parser.add_argument('--output_dir', type=str, default=None)
    config = parser.parse_args()
    main(config)