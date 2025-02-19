import os
import numpy as np
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip
from PIL import Image
import random

# Usage
base_path = r"D:\image2video\img\32777"
bgm_folder = r"D:\image2video\bgm"
output_folder = r"E:\Youtube\Outputs"

def find_numbered_folders(base_path):
    # Find all folders in the base path that are numbered
    folders = []
    for folder_name in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder_name)
        if os.path.isdir(folder_path):
            try:
                # Check if the folder name is a number
                if int(folder_name) > 0:
                    folders.append(folder_path)
            except ValueError:
                # If the folder name can't be converted to an integer, it's not numbered
                continue
    # Sort the folders by their numeric names
    folders.sort(key=lambda x: int(os.path.basename(x)))
    return folders

def random_select_bgm(bgm_folder):
    # Get all audio files in the bgm folder
    bgm_files = [os.path.join(bgm_folder, f) for f in os.listdir(bgm_folder) if f.endswith(('.mp3', '.wav'))]
    # Randomly select one
    return random.choice(bgm_files) if bgm_files else None

def create_video_from_images_with_bgm(folder_path, bgm_folder, output_folder):
    # List all images in the folder
    images = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.jpg', '.png'))]
    
    # Sort images to ensure they are in order if names suggest order
    images.sort()

    clips = []
    total_duration = 0
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
            duration = random.uniform(1, 3)  # Random duration between 1 to 4 seconds
        else:
            # After the 5th image, duration decreases progressively
            base_duration = 1.25  # Base duration for images after the first 5
            duration = max(0.5, base_duration - (i - 5) * 0.2)  # Duration drops from 2 to 0.5 seconds

        clip = ImageClip(img_array).set_duration(duration)

        # No transition, just center the image
        clip = clip.set_position('center')

        clips.append(clip)
        total_duration += duration

    # Concatenate all clips
    final_clip = concatenate_videoclips(clips)

    # Randomly select BGM
    bgm_path = random_select_bgm(bgm_folder)
    if not bgm_path:
        print(f"No BGM files found in {bgm_folder}")
        return

    # Load the background music
    audio = AudioFileClip(bgm_path)

    # Adjust audio length to match video or loop if necessary
    if audio.duration < total_duration:
        # If audio is shorter than video, loop it
        audio = audio.loop(duration=total_duration)
    else:
        # If audio is longer, trim it
        audio = audio.subclip(0, total_duration)

    # Set the audio of the video
    final_clip.audio = CompositeAudioClip([audio])

    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Construct the output file path
    output_file_path = os.path.join(output_folder, f"output_video_with_bgm_{os.path.basename(folder_path)}.mp4")

    # Write the video file with BGM to the specified output folder
    final_clip.write_videofile(output_file_path, fps=24, audio_codec='aac')

# Find all numbered folders
numbered_folders = find_numbered_folders(base_path)

# Process each numbered folder
for folder in numbered_folders:
    create_video_from_images_with_bgm(folder, bgm_folder, output_folder)