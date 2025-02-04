import os
import io
import numpy as np
from moviepy.editor import ImageClip, concatenate_videoclips
from PIL import Image
import random

def create_video_from_images(folder_path):
    # List all images in the folder
    images = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.jpg', '.png'))]
    
    # Sort images to ensure they are in order if names suggest order
    images.sort()

    clips = []
    for i, image_path in enumerate(images):
        # Open the image with PIL and resize it
        with Image.open(image_path) as img:
            # Resize the image to a height of 720 pixels while keeping aspect ratio
            new_height = 720
            new_width = int(img.width * (new_height / img.height))
            img_resized = img.resize((new_width, new_height), Image.LANCZOS)
            
            # Convert the image to a numpy array
            img_array = np.array(img_resized)

        # Now create the clip from the numpy array
        if i < 5:  # For the first 5 images
            duration = random.uniform(1, 4)  # Random duration between 1 to 4 seconds
        else:
            # After the 5th image, duration decreases progressively
            base_duration = 1.25  # Base duration for images after the first 5
            duration = max(0.5, base_duration - (i - 5) * 0.2)  # Duration drops from 2 to 0.5 seconds

        clip = ImageClip(img_array).set_duration(duration)

        # No transition, just center the image
        clip = clip.set_position('center')

        clips.append(clip)

    # Concatenate all clips
    final_clip = concatenate_videoclips(clips)

    # Write the video file
    final_clip.write_videofile("output_video.mp4", fps=24)

# Usage
folder_path = r"D:\Playground\image2video\img"
create_video_from_images(folder_path)