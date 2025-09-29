import qwiic_vl53l5cx
import sys
from math import sqrt
import time
import numpy as np
import sounddevice as sd
import pyttsx3
import random
import threading


# ============================================================================
# SENSOR SETUP
# ============================================================================
def setup_sensor():
    print("\nQwiic VL53LCX Distance Test\n")
    myVL53L5CX = qwiic_vl53l5cx.QwiicVL53L5CX()

    if myVL53L5CX.is_connected() == False:
        print("The device isn't connected to the system. Please check your connection", file=sys.stderr)
        sys.exit(1)

    print("Initializing sensor board. This can take up to 10s. Please wait.")
    if myVL53L5CX.begin() == False:
        print("Sensor initialization unsuccessful. Exiting...", file=sys.stderr)
        sys.exit(1)

    myVL53L5CX.set_resolution(8 * 8)
    myVL53L5CX.start_ranging()

    return myVL53L5CX


# ============================================================================
# AUDIO FEEDBACK SETUP
# ============================================================================
samplerate = 44100
current_freq = 440.0


def audio_callback(outdata, frames, *_):
    global current_freq
    t = (np.arange(frames, dtype=np.float32) + audio_callback.frame) / samplerate
    wave = np.sin(2 * np.pi * current_freq * t)
    outdata[:] = 0.3 * wave.reshape(-1, 1)
    audio_callback.frame += frames


audio_callback.frame = 0


def setup_audio():
    print(sd.query_devices())
    device_id = 0  # Headphone jack on Raspberry Pi
    stream = sd.OutputStream(callback=audio_callback, samplerate=samplerate, channels=1, device=device_id)
    stream.start()
    return stream


def update_audio_frequency(distance_value):
    global current_freq
    # Map distance → frequency: 50 Hz (far) → 100 Hz (close)
    freq = 50 + (100 - 50) * (1 - min(distance_value, 2000) / 2000)
    current_freq = min(freq, 100)


# ============================================================================
# VOICE FEEDBACK SETUP
# ============================================================================
engine = pyttsx3.init()
engine.setProperty("rate", 170)
engine.setProperty("volume", 0.1)

# Phrase pools
intro_phrases = [
    "Okay, listen carefully, I will explain this very clearly.",
    "Attention please, I will now describe what is happening.",
    "Let me hold your hand verbally and walk you through this.",
    "This is really important, so I will explain it step by step."
]

meaning_phrases_close = [
    "Oh no! That is super close. Please stop immediately.",
    "That is dangerously near. You should really be careful now.",
    "Wow, that is right in front of you. Don't move further!"
]

meaning_phrases_mid = [
    "That is kind of close, so please slow down a little.",
    "It's in your personal space bubble—be aware of it.",
    "You are doing fine, but just watch out in front."
]

meaning_phrases_far = [
    "That is far away, so you can relax and feel safe.",
    "Nothing to worry about, the way ahead looks clear.",
    "It's very distant, you are totally safe for now."
]

repeat_phrases = [
    "Let me repeat that so you really understand: {meaning}",
    "Yes, I will say it again because it is important: {meaning}",
    "And once more, just so it sinks in: {meaning}"
]


def narration_for_distance(dist):
    cm = dist / 10
    m = dist / 1000

    if dist < 500:
        meaning = random.choice(meaning_phrases_close)
    elif dist < 1200:
        meaning = random.choice(meaning_phrases_mid)
    else:
        meaning = random.choice(meaning_phrases_far)

    narration = " ".join([
        random.choice(intro_phrases),
        meaning,
        random.choice(repeat_phrases).format(meaning=meaning)
    ])

    return narration


# Voice feedback state
voice_lock = threading.Lock()
voice_active = False
last_voice_time = 0
VOICE_INTERVAL = 3.0  # Speak every 3 seconds


def voice_feedback_thread(distance_value):
    global voice_active
    try:
        narration = narration_for_distance(distance_value)
        engine.say(narration)
        engine.runAndWait()
    finally:
        with voice_lock:
            voice_active = False


def trigger_voice_feedback(distance_value):
    global voice_active, last_voice_time
    current_time = time.time()

    with voice_lock:
        if not voice_active and (current_time - last_voice_time) >= VOICE_INTERVAL:
            voice_active = True
            last_voice_time = current_time
            thread = threading.Thread(target=voice_feedback_thread, args=(distance_value,))
            thread.daemon = True
            thread.start()


# ============================================================================
# MAIN LOOP
# ============================================================================
def run_integrated_system():
    # Initialize all systems
    sensor = setup_sensor()
    audio_stream = setup_audio()

    image_resolution = sensor.get_resolution()
    image_width = int(sqrt(image_resolution))

    print("\n=== Integrated Distance Feedback System ===")
    print("Audio feedback: Continuous tone (50-100 Hz)")
    print("Voice feedback: Periodic narration every 3 seconds")
    print("Press Ctrl+C to exit\n")

    try:
        while True:
            if sensor.check_data_ready():
                measurement_data = sensor.get_ranging_data()

                # Get center pixel distance
                center_index = (image_width // 2) * image_width + (image_width // 2)
                distance_value = measurement_data.distance_mm[center_index]

                # Update audio feedback (continuous)
                update_audio_frequency(distance_value)

                # Trigger voice feedback (periodic)
                trigger_voice_feedback(distance_value)

                # Print to console
                print(f"Distance: {distance_value} mm → Audio: {current_freq:.1f} Hz")

            time.sleep(0.005)

    except KeyboardInterrupt:
        print("\n\nShutting down...")
        audio_stream.stop()
        audio_stream.close()
        print("System stopped.")


if __name__ == '__main__':
    try:
        run_integrated_system()
    except (KeyboardInterrupt, SystemExit) as exErr:
        print("\nEnding Example")
        sys.exit(0)
