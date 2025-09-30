import qwiic_vl53l5cx
import sys
from math import sqrt
import time
import numpy as np
import sounddevice as sd
import pyttsx3
import random
import threading
import pygame


# ============================================================================
# MODE MANAGEMENT
# ============================================================================
MODES = ["HAPTIC", "VOICE", "PAUSE"]
mode = 2  # start in PAUSE mode

def switch_mode():
    global mode
    mode = (mode + 1) % len(MODES)
    print(f"Switched mode → {MODES[mode]}")


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
    if distance_value > 2000:  # over 2 meters → silent
        current_freq = 0
    else:
        # Map distance 2000 → 0 mm to 0–50 Hz
        # closer = higher frequency
        freq = 50 * (1 - distance_value / 2000)
        current_freq = freq


# ============================================================================
# VOICE FEEDBACK SETUP
# ============================================================================
engine = pyttsx3.init()
engine.setProperty("rate", 170)
engine.setProperty("volume", 0.5)

# Phrase pools
intro_phrases = [
    "Okay, listen carefully, I will explain this very clearly.",
    "Attention please, I will now describe what is happening.",
    "Let me hold your hand verbally and walk you through this.",
    "This is really important, so I will explain it step by step."
]

distance_phrases = [
    "The distance I measured is {dist} meters.",
    "Right now, the object is {dist} meters away.",
    "What I see is {dist} meters, and I am telling you.",
    "I just checked and it is exactly {dist} meters."
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
    if dist < 500:
        meaning = random.choice(meaning_phrases_close)
    elif dist < 1200:
        meaning = random.choice(meaning_phrases_mid)
    else:
        meaning = random.choice(meaning_phrases_far)

    narration = " ".join([
        random.choice(intro_phrases),
        random.choice(distance_phrases).format(dist=dist/1000.0),
        meaning,
        random.choice(repeat_phrases).format(meaning=meaning)
    ])

    return narration


# Voice feedback state
voice_lock = threading.Lock()
voice_active = False
last_voice_time = 0
VOICE_INTERVAL = 1.0  # Speak every x seconds


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
# VISUAL FEEDBACK SETUP
# ============================================================================
def setup_display():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # Fullscreen
    pygame.display.set_caption("Distance Display")

    # Scale font size based on screen height
    screen_rect = screen.get_rect()
    font_size = int(screen_rect.height * 0.15)
    font_large = pygame.font.SysFont("Arial", font_size)
    font_small = pygame.font.SysFont("Arial", font_size // 2)

    return screen, font_large, font_small


def update_display(screen, font_large, font_small, distance_value):
    global mode
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            switch_mode()

    screen.fill((0, 0, 0))  # Black background

    # Distance text (large)
    distance_m = distance_value / 1000.0
    text_surface = font_large.render(f"{distance_m:.2f} m", True, (255, 255, 255))
    rect = text_surface.get_rect(center=(screen.get_rect().centerx, screen.get_rect().centery - 80))
    screen.blit(text_surface, rect)

    # Mode text (small)
    mode_surface = font_small.render(f"MODE: {MODES[mode]}", True, (0, 200, 255))
    mode_rect = mode_surface.get_rect(center=(screen.get_rect().centerx, screen.get_rect().centery + 80))
    screen.blit(mode_surface, mode_rect)

    pygame.display.flip()


# ============================================================================
# MAIN LOOP
# ============================================================================
def run_integrated_system():
    global mode, current_freq
    sensor = setup_sensor()
    audio_stream = setup_audio()
    screen, font_large, font_small = setup_display()

    image_resolution = sensor.get_resolution()
    image_width = int(sqrt(image_resolution))

    print("\n=== Integrated Distance Feedback System ===")
    print("Tap screen to switch modes: HAPTIC → VOICE → PAUSE")
    print("ESC to quit\n")

    try:
        while True:
            if sensor.check_data_ready():
                measurement_data = sensor.get_ranging_data()

                # Get center pixel distance
                center_index = (image_width // 2) * image_width + (image_width // 2)
                distance_value = measurement_data.distance_mm[center_index] / 4

                # Mode logic
                if MODES[mode] == "HAPTIC":
                    update_audio_frequency(distance_value)
                elif MODES[mode] == "VOICE":
                    current_freq = 0
                    trigger_voice_feedback(distance_value)
                elif MODES[mode] == "PAUSE":
                    current_freq = 0

                # Update screen
                update_display(screen, font_large, font_small, distance_value)

                # Debug console log
                print(f"Mode={MODES[mode]} | Distance={distance_value:.0f} mm | Freq={current_freq:.1f} Hz")

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n\nShutting down...")
        audio_stream.stop()
        audio_stream.close()
        pygame.quit()
        print("System stopped.")


if __name__ == '__main__':
    try:
        run_integrated_system()
    except (KeyboardInterrupt, SystemExit) as exErr:
        print("\nEnding Example")
        sys.exit(0)
