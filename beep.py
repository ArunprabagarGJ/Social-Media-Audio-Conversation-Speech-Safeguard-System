from flask import Flask, render_template, request, jsonify,send_file
import speech_recognition as sr
import re
from gtts import gTTS
import os
from io import BytesIO
#from playsound import playsound

app = Flask(__name__)

# Predefined list of bad words
bad_words = ["shit", "bastard", "fuck", "asshole","bastard","bitch","bloody",
"bollocks","brotherfucker","brother fucker","motherfucker","bugger","bullshit","mother fucker","fuckingbeast"]  # Add more bad words as needed

def beep_bad_words(text):
    for word in bad_words:
        if word in text:
            # Replace bad word with beeps
            text = re.sub(r'\b' + re.escape(word) + r'\b', "*BEEP*", text, flags=re.IGNORECASE)
    return text

def text_to_speech(text_with_beeps):
    tts = gTTS(text=text_with_beeps, lang='en', slow=False)
    tts.save("output.mp3")
    os.system("start output.mp3")  # Open the MP3 file with the default audio player

def censor_text(text):
    for word in bad_words:
        text = re.sub(r'\b{}\b'.format(word), 'beep', text, flags=re.IGNORECASE)
    return text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/speech-to-text', methods=['POST'])
def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Please speak something...")
        audio = recognizer.listen(source)
    
    try:
        text = recognizer.recognize_google(audio)
        text_with_beeps = beep_bad_words(text)
        text_to_speech("You said: " + text_with_beeps)
        return jsonify({"result": text_with_beeps})
    except sr.UnknownValueError:
        return jsonify({"result": "Could not understand audio."})
    except sr.RequestError as e:
        return jsonify({"result": "Could not request results; {0}".format(e)})

@app.route('/convert', methods=['POST'])
def convert_to_speech():
    data = request.json
    input_text = data.get('text', '')
    censored_text = censor_text(input_text)
    tts = gTTS(text=censored_text, lang='en', slow=False)
    audio_stream = BytesIO()
    tts.write_to_fp(audio_stream)
    audio_stream.seek(0)
    return send_file(audio_stream, mimetype='audio/wav')

if __name__ == "__main__":
    app.run(debug=True)
