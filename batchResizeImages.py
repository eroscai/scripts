import os
from PIL import Image

def resize_image(image_path, max_size):
    with Image.open(image_path) as img:
        width, height = img.size
        if width > max_size or height > max_size:
            # Calculate the new size preserving the aspect ratio
            if width > height:
                new_width = max_size
                new_height = int((max_size / width) * height)
            else:
                new_height = max_size
                new_width = int((max_size / height) * width)

            # Resize the image
            img = img.resize((new_width, new_height), Image.LANCZOS)

            # Save the image back to the same path
            img.save(image_path)
            print(f"Resized {image_path} to {new_width}x{new_height}")

def process_directory(directory, max_size):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                image_path = os.path.join(root, file)
                resize_image(image_path, max_size)

if __name__ == "__main__":
    max_size = 800  # Define the maximum size for the width or height
    current_directory = "/Users/Eros/Downloads/sticker"  # Get the current working directory
    process_directory(current_directory, max_size)