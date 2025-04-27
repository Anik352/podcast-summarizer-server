# server.py

from flask import Flask, request, jsonify
import requests
import openai

app = Flask(__name__)

# Insert your API keys here
ASSEMBLYAI_API_KEY = 'your-assemblyai-api-key'
OPENAI_API_KEY = 'your-openai-api-key'

openai.api_key = OPENAI_API_KEY

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    data = request.json
    audio_url = data.get('audio_url')

    # 1. Send audio to AssemblyAI for transcription
    headers = {'authorization': ASSEMBLYAI_API_KEY}
    response = requests.post('https://api.assemblyai.com/v2/transcript', json={"audio_url": audio_url}, headers=headers)
    transcript_id = response.json()['id']

    # 2. Wait for transcription to complete
    while True:
        status_response = requests.get(f"https://api.assemblyai.com/v2/transcript/{transcript_id}", headers=headers)
        status = status_response.json()['status']
        if status == 'completed':
            text = status_response.json()['text']
            break
        elif status == 'failed':
            return jsonify({"error": "Transcription failed"}), 400

    # 3. Send text to OpenAI for summarization
    summary_prompt = f"Summarize this podcast and give me 5 key learnings:\n\n{text}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": summary_prompt}
        ]
    )

    summary = response['choices'][0]['message']['content']

    return jsonify({"summary": summary})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
