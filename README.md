# Provotype

An interactive distance feedback system that uses a VL53L5CX distance sensor to provide multimodal feedback through haptic vibration, voice output, and visual display.

<p align="center">
  <img src="https://github.com/user-attachments/assets/e7aa00f7-026a-464f-b19f-601e3c6a5ac6" alt="Full" width="30%" />
  <img src="https://github.com/user-attachments/assets/8e0ad438-421b-40bd-997d-32c8e8591e40" alt="Batteries_Closeup" width="30%" />
  <img src="https://github.com/user-attachments/assets/b91eee2c-4bc4-4059-87d7-0ffacf074a5e" alt="Display_Closeup" width="30%" />
</p>

## Features

- **Distance Sensing**: Uses Qwiic VL53L5CX sensor with 8×8 resolution (64 pads)
- **Three Modes**: Switch between HAPTIC, VOICE, and PAUSE modes by tapping the screen
- **Haptic Feedback**: Audio-based vibration (70-180 Hz) mapped to distance
- **Voice Output**: Humorous over-explained distance descriptions using text-to-speech
- **Visual Display**: Real-time on-screen feedback with pygame interface

## Files

- `index.py` – Main program integrating all components
- `distance.py` – Distance sensor module
- `haptic.py` – Haptic feedback via audio frequencies
- `audio.py` – Voice output with TTS

## Requirements

- Python 3.x
- Qwiic VL53L5CX sensor
- Dependencies: `qwiic_vl53l5cx`, `sounddevice`, `pyttsx3`, `pygame`, `numpy`

## Usage

```bash
python index.py
```

Tap the screen to cycle through modes: HAPTIC → VOICE → PAUSE


