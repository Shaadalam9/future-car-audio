import pygame
import time
import threading

def play_sound(sound_file, volume):
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play()

def update_volume():
    global overtaking_flag
    global acceleration
    
    while overtaking_flag:
        # Calculate volume based on acceleration (you might need to adjust this calculation)
        volume = max(0.5, min(1.0, acceleration))  # Ensure volume is between 0.0 and 1.0
        if overtaking_flag:
            play_sound("files/overtaking_Sound.mp3", volume)
        else:
            play_sound("files/audio_1.mp3", volume)
        time.sleep(1)  # Adjust this delay as needed to control the update frequency

# Assuming this is where you get your acceleration input
acceleration = float(input("Enter acceleration: "))

# Start a thread to continuously update the volume and play the sound
overtaking_flag = True
thread = threading.Thread(target=update_volume)
thread.start()

# Your main code continues here
# For this example, I'll just make the main thread sleep for a while
time.sleep(10)  # Adjust this or replace it with your main logic

# Set overtaking_flag to False to stop the volume update thread
overtaking_flag = False
