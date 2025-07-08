from flask import Flask, request, jsonify
from vosk import Model, KaldiRecognizer
import wave
import os
import json

app = Flask(__name__)

model = Model(lang="it")  # italiano

@app.route("/transcribe", methods=["POST"])
def transcribe():
    if 'file' not in request.files:
        return jsonify({"error": "Nessun file inviato"}), 400

    file = request.files['file']
    file_path = "audio.wav"
    file.save(file_path)

    wf = wave.open(file_path, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        return jsonify({"error": "Formato WAV non valido (serve: mono PCM16)"}), 400

    rec = KaldiRecognizer(model, wf.getframerate())

    results = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            results.append(json.loads(rec.Result())["text"])
    results.append(json.loads(rec.FinalResult())["text"])

    return jsonify({"text": " ".join(results)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
