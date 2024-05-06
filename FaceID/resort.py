import os
import shutil

# Define your source and target directories
source_dir = '/Users/Eros/Downloads/1'  # Update this path
target_dir = '/Users/Eros/Downloads/1Sorted'  # Update this path

def organize_photos(src_dir, tgt_dir):
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".jpg"):
                # Extract the unique identifier from the filename
                try:
                    unique_id = file.split('w768_h1280')[1].split('1.jpg')[0]
                except IndexError:
                    print(f"Filename format unexpected: {file}")
                    continue
                # Create a new directory path using the unique identifier
                new_dir = os.path.join(tgt_dir, unique_id)
                # Make the directory if it doesn't already exist
                os.makedirs(new_dir, exist_ok=True)
                # Construct the source and destination file paths
                src_path = os.path.join(root, file)
                dst_path = os.path.join(new_dir, file)
                # Copy the file to the new location
                shutil.copy2(src_path, dst_path)
                print(f"Copied {file} to {new_dir}")

# Call the function with your specified directories
organize_photos(source_dir, target_dir)
