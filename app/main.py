from flask import Flask, request, jsonify
from gcs_utils import upload_to_gcs
from extract import extract_insurance_insights
import datetime

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze_audio():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    audio_file = request.files['file']
    filename = f"call_{datetime.datetime.now().isoformat()}.mp3"
    gcs_uri = upload_to_gcs(audio_file, "health-insurance-call-audio", filename)

    insights = extract_insurance_insights(gcs_uri)
    return jsonify(insights)
