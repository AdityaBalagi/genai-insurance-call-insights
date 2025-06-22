import os
from flask import Flask, request, jsonify
from vertexai.generative_models import GenerativeModel, Part, GenerationConfig
import vertexai
import json
import datetime

app = Flask(__name__)

PROJECT_ID = "gcp-deployment-example-312025"
REGION = "us-central1"

vertexai.init(project=PROJECT_ID, location=REGION)

@app.route("/", methods=["POST"])
def extract_insights():
    data = request.get_json()
    gcs_uri = data.get("gcs_uri")

    if not gcs_uri:
        return jsonify({"error": "Missing 'gcs_uri' in request body"}), 400

    model = GenerativeModel("gemini-2.0-flash-001")

    prompt = """
You are a compliance and sales assistant analyzing an insurance sales call between an agent and a customer.
The conversation can be in any language.
From the conversation, extract and return the following in JSON format.
Ensure the output strictly adheres to the provided JSON schema. If a field cannot be extracted, return an empty string for string fields, an empty list for list fields, and false for boolean fields, but maintain the structure.

{
  "call_id": "string // Filename of the audio recording, e.g., 'call_20250622_001.wav'",
  "summary" : "Summary of call in 4 to 5 sentence coving all points, key conversation, customer or agent actions.",
  "timestamp": "string // ISO 8601 formatted timestamp when processing began, e.g., '2025-06-22T20:15:00+05:30'",
  "call_type": "string // 'inbound' or 'outbound', based on who initiated the call",

  "customer": {
    "name": "string // Extracted name from the conversation, return empty string if not available",
    "location": "string // Customer's city, state, or region if mentioned in the call"
  },

  "agent": {
    "name": "string // Agent's first name if stated, else empty string",
    "location": "string // Agent's base location if mentioned"
  },

  "product_discussed": {
    "name": "string // Name of the insurance plan discussed",
    "coverage_amount": "string // Coverage limit, e.g., '₹10 lakh'",
    "features": [
      "string // Key features mentioned in the conversation"
    ],
    "premium": {
      "monthly": "string // Approximate monthly premium, e.g., '₹1,950'",
      "annual_discount_offered": "boolean // True if any discount for annual payment is mentioned"
    },
    "pre_existing_condition_policy": "string // Summary of how pre-existing conditions are handled"
  },

  "sales_process": {
    "steps_followed": [
      "string // Steps completed during the call, e.g., 'screen sharing', 'form filling'"
    ],
    "application_completion_status": "string // 'Successful', 'Partial', or 'Not started'",
    "payment_mode": "string // e.g., 'Net Banking', 'UPI', 'Card', or empty string if not completed"
  },

  "agent_performance": {
    "clarity_of_explanation": "string // subjective rating: 'excellent', 'good', 'average', or ''",
    "closing_successfully": "boolean // True if customer completed purchase",
    "engagement_style": "string // Summary of agent’s approach: e.g., 'informative', 'pushy', 'patient'",
    "action_items" : "List // List of action items to the agent e.g. ['Agent will send confirmation email', 'Agent will follow-up call of 1 Jully'] return '' if no agent action"
  },

  "customer_engagement": {
    "query_topics": [
      "string // Customer's main concerns, e.g., 'premium', 'waiting period'"
    ],
    "satisfaction_level": "string // Inferred sentiment: 'positive', 'neutral', 'negative', or ''"
  },

  "insights": {
    "business_opportunity": "string // Suggested upsell or service improvement from conversation",
    "training_recommendation": "string // Notes for agent training or QA team"
  }
}

"""


    content = [
        prompt,
        Part.from_uri(gcs_uri, mime_type="audio/wav")  # Adjust MIME if .mp3 or .mp4
    ]

    generation_config = GenerationConfig(response_mime_type="application/json")

    response = model.generate_content(content, generation_config=generation_config)

    try:
        insights = json.loads(response.text)
        # Optionally add timestamp, call_id etc.
        insights["timestamp"] = datetime.datetime.now().isoformat()
        return jsonify(insights)
    except Exception as e:
        return jsonify({"error": str(e), "raw_response": response.text}), 500
