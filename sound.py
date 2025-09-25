import numpy as np
import sounddevice as sd
import time

samplerate = 44100
current_freq = 440.0  # global variable for frequency

def audio_callback(outdata, frames, time_info, status):
    global current_freq
    t = (np.arange(frames) + audio_callback.frame) / samplerate
    wave = np.sin(2 * np.pi * current_freq * t).astype(np.float32)
    outdata[:, 0] = 0.3 * wave  # mono output
    audio_callback.frame += frames

audio_callback.frame = 0

# --- Start audio stream ---
stream = sd.OutputStream(callback=audio_callback, samplerate=samplerate, channels=1)
stream.start()

def loop():
    global current_freq
    distances = [300, 1200, 600, 1800]  # fake test distances in mm
    i = 0
    while True:
        distance_value = distances[i % len(distances)]

        # Map distance → frequency (closer = higher pitch)
        freq = 200 + (2000 - 200) * (1 - min(distance_value, 2000) / 2000)
        current_freq = freq  # update frequency in real time

        print(f"Distance: {distance_value} mm → {current_freq:.1f} Hz")
        i += 1
        time.sleep(1.0)

########################

print(sd.query_devices())
loop()

########################