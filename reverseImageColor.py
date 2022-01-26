from PIL import Image
import PIL.ImageOps
import argparse
import os.path as osp
import os

def main(cfg):
    input_path = cfg.input_dir
    output_path = cfg.output_dir
    os.makedirs(output_path, exist_ok=True)

    valid_images = [".jpg",".png"]
    for f in os.listdir(input_path):
        ext = osp.splitext(f)[1]
        if ext.lower() not in valid_images:
            continue
        image = Image.open(osp.join(input_path,f))
        inverted_image = PIL.ImageOps.invert(image)
        final_path = osp.join(output_path,f)
        inverted_image.save(final_path)
        print('inverted: ' + f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', type=str, default=None)
    parser.add_argument('--output_dir', type=str, default=None)
    config = parser.parse_args()
    main(config)