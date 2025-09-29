import time
import random
import pyttsx3

# Initialize the TTS engine
engine = pyttsx3.init()
engine.setProperty("rate", 170)
engine.setProperty("volume", 0.1)
print(engine.getProperty('voices'))
# engine.setProperty('voice', engine.getProperty('voices')[1].id)

def say(text):
    engine.say(text)
    engine.runAndWait()

# Pools of overexplaining phrases
intro_phrases = [
    "Okay, listen carefully, I will explain this very clearly.",
    "Attention please, I will now describe what is happening.",
    "Let me hold your hand verbally and walk you through this.",
    "This is really important, so I will explain it step by step."
]

distance_phrases = [
    "The distance I measured is {dist} millimeters.",
    "Right now, the object is {dist} millimeters away.",
    "What I see is {dist} millimeters, and I am telling you.",
    "I just checked and it is exactly {dist} millimeters."
]

conversion_phrases = [
    "That equals about {cm:.0f} centimeters, which is like a ruler and a half.",
    "In meters, that would be around {m:.2f}. Yes, meters.",
    "If you like numbers, that is {cm:.0f} centimeters, or {m:.2f} meters.",
    "For comparison, {cm:.0f} centimeters is like the length of your arm."
]

meaning_phrases_close = [
    "Oh no! That is super close. Please stop immediately.",
    "That is dangerously near. You should really be careful now.",
    "Wow, that is right in front of you. Don’t move further!"
]

meaning_phrases_mid = [
    "That is kind of close, so please slow down a little.",
    "It’s in your personal space bubble—be aware of it.",
    "You are doing fine, but just watch out in front."
]

meaning_phrases_far = [
    "That is far away, so you can relax and feel safe.",
    "Nothing to worry about, the way ahead looks clear.",
    "It’s very distant, you are totally safe for now."
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
        random.choice(distance_phrases).format(dist=dist),
        random.choice(conversion_phrases).format(cm=cm, m=m),
        meaning,
        random.choice(repeat_phrases).format(meaning=meaning)
    ])

    return narration

def loop():
    distances = [300, 1200, 600, 1800, 450, 2000]
    i = 0
    while True:
        distance_value = distances[i % len(distances)]
        narration = narration_for_distance(distance_value)

        print(f"Distance: {distance_value} mm → speaking")
        say(narration)

        i += 1
        time.sleep(0.3)

if __name__ == "__main__":
    loop()
