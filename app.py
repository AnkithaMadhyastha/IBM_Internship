from flask import Flask, render_template, request, jsonify, url_for
import speech_recognition as sr
from googletrans import Translator, LANGUAGES
import os
import gtts
import pyttsx3

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/audio'


# Home page
@app.route('/')
def index():
    return render_template('index.html')


# Voice Translator
@app.route('/voice_translator', methods=['GET', 'POST'])
def voice_translator():
    languages = LANGUAGES
    if request.method == 'POST':
        input_lang_name = request.form['input_language']
        output_lang_name = request.form['output_language']

        # Find the language codes
        input_lang = next((code for code, name in LANGUAGES.items() if name.lower() == input_lang_name.lower()), None)
        output_lang = next((code for code, name in LANGUAGES.items() if name.lower() == output_lang_name.lower()), None)

        if not input_lang or not output_lang:
            return jsonify({'error': 'Invalid language selection'})

        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio, language=input_lang)
            translator = Translator()
            translation = translator.translate(text, dest=output_lang)
            converted_audio = gtts.gTTS(text=translation.text, lang=output_lang)
            audio_path = os.path.join(app.config['UPLOAD_FOLDER'], 'translated_voice.mp3')
            converted_audio.save(audio_path)
            return jsonify(
                {'text': translation.text, 'audio_url': url_for('static', filename='audio/translated_voice.mp3')})
        except sr.UnknownValueError:
            return jsonify({'error': 'Google Speech Recognition could not understand your audio'})
        except sr.RequestError as e:
            return jsonify({'error': f'Could not request results from Google Speech Recognition service; {e}'})

    return render_template('voice_transl.html', languages=languages)


# Text to Speech Translator

@app.route('/text_to_speech', methods=['GET', 'POST'])
def text_to_speech():
    if request.method == 'POST':
        text = request.form['text']
        voice = request.form.get('voice', 'female')

        # Initialize text-to-speech engine
        engine = pyttsx3.init()

        # Set properties for the engine
        voices = engine.getProperty('voices')
        if voice == 'male':
            engine.setProperty('voice', voices[0].id)  # Male voice
        else:
            engine.setProperty('voice', voices[1].id)  # Female voice

        # Convert text to speech
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], 'tts_output.mp3')
        engine.save_to_file(text, audio_path)
        engine.runAndWait()

        return jsonify({'message': 'Text to speech conversion successful!', 'audio_url': url_for('static', filename='audio/tts_output.mp3')})

    return render_template('text_speech.html')
# Language Translator
@app.route('/language_translator', methods=['GET', 'POST'])
def language_translator():
    languages = LANGUAGES
    if request.method == 'POST':
        input_text = request.form.get('input_text')
        dest_lang = request.form.get('dest_language')
        if input_text and dest_lang:
            try:
                translator = Translator()
                lang_code = [code for code, lang in LANGUAGES.items() if lang == dest_lang][0]
                translated = translator.translate(text=input_text, dest=lang_code)
                return jsonify({'translated_text': translated.text})
            except Exception as e:
                return jsonify({'error': str(e)})
    return render_template('lang_transl.html', languages=languages)


if __name__ == '__main__':
    app.run(debug=True)