import argparse
import os
import numpy as np
import cv2

IMG_EXT = ('.png', '.jpg', '.jpeg', '.JPG', '.JPEG')
trimap_size = 50
trimap_threshold = 200

def trimap(mask, size, conf_threshold):
    pixels = 2 * size + 1
    kernel = np.ones((pixels, pixels), np.uint8)

    dilation = cv2.dilate(mask, kernel, iterations=2)

    remake = np.zeros_like(mask)
    remake[dilation == 255] = 127  # Set every pixel within dilated region as probably foreground.
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
        trimap_image = trimap(input_image, trimap_size, trimap_threshold)
        trimap_filename = os.path.basename(filename).split('.')[0] + '.png'
        cv2.imwrite(os.path.join(trimaps_path, trimap_filename), trimap_image)
        print('done {}'.format(trimap_filename))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', type=str, default=None)
    parser.add_argument('--output_dir', type=str, default=None)
    config = parser.parse_args()
    main(config)