# server.py

from flask import Flask, request, jsonify
import requests
import openai
import time
import os

app = Flask(__name__)

# It's safer to use environment variables for API keys
ASSEMBLYAI_API_KEY = os.getenv("7a22e0c8cbb746f485613ae64f1dbdf9")
OPENAI_API_KEY = os.getenv("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")
openai.api_key = OPENAI_API_KEY

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    data = request.get_json()
    audio_url = data.get('audio_url')

    if not audio_url:
        return jsonify({"error": "audio_url is required"}), 400

    # 1. Send audio to AssemblyAI
    headers = {'authorization': ASSEMBLYAI_API_KEY}
    transcript_response = requests.post(
        'https://api.assemblyai.com/v2/transcript',
        json={"audio_url": audio_url},
        headers=headers
    )

    if transcript_response.status_code != 200:
        return jsonify({"error": "Failed to start transcription"}), 500

    transcript_id = transcript_response.json()['id']

    # 2. Poll until transcription completes
    while True:
        status_response = requests.get(
            f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
            headers=headers
        )
        status_data = status_response.json()
        status = status_data.get('status')

        if status == 'completed':
            text = status_data.get('text')
            break
        elif status == 'failed':
            return jsonify({"error": "Transcription failed"}), 400

        time.sleep(3)  # Wait 3 seconds before checking again

    # 3. Summarize text with OpenAI
    summary_prompt = f"Summarize this podcast and list 5 key learnings:\n\n{text}"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": summary_prompt}]
        )
        summary = response['choices'][0]['message']['content']
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"summary": summary})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
