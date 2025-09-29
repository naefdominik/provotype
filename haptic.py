import numpy as np
import sounddevice as sd
import time

samplerate = 44100
current_freq = 440.0  # global variable for frequency

def audio_callback(outdata, frames, *_):
    global current_freq
    t = (np.arange(frames, dtype=np.float32) + audio_callback.frame) / samplerate
    wave = np.sin(2 * np.pi * current_freq * t)
    outdata[:] = 0.3 * wave.reshape(-1, 1)
    audio_callback.frame += frames

audio_callback.frame = 0

# --- Start audio stream ---
print(sd.query_devices())
device_id = 0  # Headphone jack on Raspberry Pi

stream = sd.OutputStream(callback=audio_callback, samplerate=samplerate, channels=1, device=device_id)
stream.start()

def loop():
    global current_freq
    distances = [300, 1200, 600, 1800]
    i = 0
    while True:
        distance_value = distances[i % len(distances)]

        # Map distance → frequency, capped at 100 Hz
        freq = 50 + (100 - 50) * (1 - min(distance_value, 2000) / 2000)
        # Range is now 50 Hz (far) → 100 Hz (close)

        current_freq = min(freq, 100)  # safety cap

        print(f"Distance: {distance_value} mm → {current_freq:.1f} Hz")
        i += 1
        time.sleep(1.0)

loop()
