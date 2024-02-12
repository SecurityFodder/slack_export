import os
import requests
import datetime
import json

# Replace with your actual tokens
SLACK_BOT_TOKEN = "xoxb-your-bot-token"
CONVERSATION_ID = "C12345678"

# Function to call Slack API endpoints


def call_slack_api(method, data=None, params=None):
    url = f"https://slack.com/api/{method}"
    headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
    response = requests.post(url, headers=headers, data=data, params=params)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error interacting with Slack API: {e}")
        exit(1)


# Create output directory
output_dir = "slack_export"
os.makedirs(output_dir, exist_ok=True)

# Get conversation history in batches
params = {"channel": CONVERSATION_ID, "limit": 200}
has_more = True
all_messages = []
while has_more:
    history = call_slack_api("conversations.history", params=params)
    all_messages.extend(history["messages"])
    has_more = history["has_more"]
    if has_more:
        params["cursor"] = history["response_metadata"]["next_cursor"]

# Process messages and save as JSON
output_data = []
for message in all_messages:
    # Fetch username
    user_info = call_slack_api("users.info", data={"user": message["user"]})
    username = user_info["user"]["profile"].get("real_name", "username")

    # Extract timestamp
    timestamp_ts = message.get("ts")
    timestamp = datetime.datetime.fromtimestamp(
        float(timestamp_ts)).strftime("%Y-%m-%d %H:%M:%S")

    text = message.get("text", "")

    # Handle images
    if "files" in message:
        for file in message["files"]:
            if file.get("mimetype", "").startswith("image"):
                image_url = file["url_private_download"]
                headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
                try:
                    response = requests.get(image_url, headers=headers)
                    response.raise_for_status()

                    image_filename = os.path.basename(file["url_private"])
                    with open(os.path.join(output_dir, image_filename), "wb") as f:
                        f.write(response.content)
                except requests.exceptions.RequestException as e:
                    print(f"Error downloading image: {e}")

    # Build output structure for JSON
    output_line = {
        "user": username,
        "timestamp": timestamp,
        "text": text,
        "image_url": image_url if "image_url" in locals() else None
    }
    output_data.append(output_line)

# Write to JSON file
with open(os.path.join(output_dir, "conversation.json"), "w") as f:
    json.dump(output_data, f)
