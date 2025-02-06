import os
import io
import numpy as np
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip, CompositeVideoClip
from PIL import Image
import random

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
                continue
    folders.sort(key=lambda x: int(os.path.basename(x)))
    return folders

def random_select_bgm(bgm_folder):
    bgm_files = [os.path.join(bgm_folder, f) for f in os.listdir(bgm_folder) if f.endswith(('.mp3', '.wav'))]
    return random.choice(bgm_files) if bgm_files else None

def create_video_from_images_with_bgm(folder_path, bgm_folder, output_folder):
    # List all images in the folder
    images = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.jpg', '.png'))]
    images.sort()

    clips = []
    total_duration = 0

    for i, image_path in enumerate(images):
        # Open and resize the image (resize height to 720)
        with Image.open(image_path) as img:
            new_height = 720
            new_width = int(img.width * (new_height / img.height))
            img_resized = img.resize((new_width, new_height), Image.LANCZOS)
            img_array = np.array(img_resized)

        # --- Duration logic ---
        if i == 0:
            # Force the very first image to be 4 seconds long
            duration = 4
        else:
            # For subsequent images, use your existing duration logic
            if i < 5:
                duration = random.uniform(1, 3)
            else:
                base_duration = 1.25
                duration = max(0.5, base_duration - (i - 5) * 0.2)

        clip = ImageClip(img_array).set_duration(duration).set_position('center')
        clips.append(clip)
        total_duration += duration

    # Concatenate the image clips
    final_clip = concatenate_videoclips(clips)

    # --- Create the overlay clip for the first 4 seconds ---
    overlay_path = r"D:\Playground\image2video\material\gray.png"
    overlay_clip = ImageClip(overlay_path).set_duration(4).set_start(0)
    
    # To animate the overlay, we define key positions.
    # These positions are in (x, y) pixels based on the final video size.
    # We assume:
    #   - right top: (video_width - overlay_width, 0)
    #   - center: ((video_width - overlay_width)/2, (video_height - overlay_height)/2)
    #   - left top: (0, 0)
    #   - right bottom: (video_width - overlay_width, video_height - overlay_height)
    #   - left center: (0, (video_height - overlay_height)/2)
    #
    # We create a function that returns the (x,y) position based on time t.
    # (t goes from 0 to 4 seconds)
    def overlay_position(t):
        # Get video dimensions from the final clip
        video_width, video_height = final_clip.size
        # Get overlay dimensions (assuming they do not change during animation)
        ow, oh = overlay_clip.w, overlay_clip.h
        
        # Define the key positions at t=0,1,2,3,4 seconds:
        key_positions = [
            (video_width - ow, 0),                           # t = 0 sec: right top
            ((video_width - ow) / 2, (video_height - oh) / 2), # t = 1 sec: center
            (0, 0),                                          # t = 2 sec: left top
            (video_width - ow, video_height - oh),           # t = 3 sec: right bottom
            (0, (video_height - oh) / 2)                       # t = 4 sec: left center
        ]
        
        # Determine which segment we are in:
        # There are 4 segments over 4 seconds.
        if t >= 4:
            return key_positions[-1]
        seg = int(t)  # t in [0,1)->seg0, [1,2)->seg1, etc.
        t_seg = t - seg  # local time within the segment (0 to 1)
        
        x0, y0 = key_positions[seg]
        x1, y1 = key_positions[seg + 1]
        
        # Linear interpolation between the two key positions:
        x = x0 + (x1 - x0) * t_seg
        y = y0 + (y1 - y0) * t_seg
        return (x, y)

    # Set the overlay clip’s animated position
    overlay_clip = overlay_clip.set_position(overlay_position)

    # --- Set up the background music ---
    bgm_path = random_select_bgm(bgm_folder)
    if not bgm_path:
        print(f"No BGM files found in {bgm_folder}")
        return

    audio = AudioFileClip(bgm_path)
    if audio.duration < total_duration:
        audio = audio.loop(duration=total_duration)
    else:
        audio = audio.subclip(0, total_duration)

    # Assign audio to final_clip
    final_clip.audio = CompositeAudioClip([audio])

    # --- Composite the overlay onto the final clip ---
    # The overlay (animated for 4 seconds) will appear on top
    composite_clip = CompositeVideoClip([final_clip, overlay_clip], size=final_clip.size)
    composite_clip.audio = final_clip.audio  # Preserve the audio

    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_file_path = os.path.join(output_folder, f"output_video_with_bgm_{os.path.basename(folder_path)}.mp4")
    composite_clip.write_videofile(output_file_path, fps=24, audio_codec='aac')

# --- Usage ---
base_path = r"D:\Playground\image2video\img"
bgm_folder = r"D:\Playground\image2video\bgm"
output_folder = r"D:\Playground\image2video\outputs"

numbered_folders = find_numbered_folders(base_path)
for folder in numbered_folders:
    create_video_from_images_with_bgm(folder, bgm_folder, output_folder)