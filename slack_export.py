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
    if not response.ok or not response.json().get("ok", False):
        print(f"Something went wrong {response.text} - {url}")
        exit(1)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error interacting with Slack API: {e}")
        exit(1)


# Create output directory
output_dir = "slack_export"
emojis_dir = os.path.join(output_dir, "emojis")
os.makedirs(output_dir, exist_ok=True)
os.makedirs(emojis_dir, exist_ok=True)

# Function to download custom emojis (New Addition)


def download_emoji(emoji_url, destination_folder):
    filename = os.path.basename(emoji_url.rsplit(
        '?', 1)[0])  # Handle potential query params
    file_path = os.path.join(destination_folder, filename)

    response = requests.get(emoji_url, stream=True)
    response.raise_for_status()

    with open(file_path, "wb") as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)

# Function for handling emojis (New Addition)
def handle_emojis(text, output_data, current_message):
    # You might need to refine this pattern
    emoji_pattern = r":([a-zA-Z0-9+_-]+):"
    emojis_found = re.findall(emoji_pattern, text)

    if emojis_found:
        # Get list of available emoji URLs
        emoji_urls = call_slack_api("emoji.list")["emoji"].keys()

        for emoji_name in emojis_found:
            if emoji_name in emoji_urls:
                emoji_url = emoji_urls[emoji_name]
                if emoji_url.startswith("alias:"):  # Exclude alias emojis
                    continue

                emoji_filename = download_emoji(emoji_url, emojis_dir)
                emoji_path = os.path.join(emojis_dir, emoji_filename)

                # Replace emoji in text with a placeholder (could be an <img> tag if desired)
                text = text.replace(f":{emoji_name}:", f"[EMOJI:{emoji_path}]")

        current_message["text"] = text


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
    # Check for and potentially modify text
    handle_emojis(text, output_data, message)

    # Handle images
    if "files" in message:
        for file in message["files"]:
            if file.get("mimetype", "").startswith("image"):
                image_url = file["url_private_download"]
                headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
                try:
                    response = requests.get(image_url, headers=headers)
                    response.raise_for_status()  # Check for successful download

                    image_filename = os.path.basename(file["url_private"])
                    with open(os.path.join(output_dir, image_filename), "wb") as f:
                        f.write(response.content)  # Save image locally

                    # Keep track of the local image filename in your JSON for reference
                    image_path = os.path.join(output_dir, image_filename)
                except requests.exceptions.RequestException as e:
                    print(f"Error downloading image: {e}")

    # Build output structure for JSON (Modified with local image reference)
    output_line = {
        "user": username,
        "timestamp": timestamp,
        "text": text,
        "image_path": image_path if "image_path" in locals() else None
    }
    output_data.append(output_line)

# Write to JSON file
with open(os.path.join(output_dir, "conversation.json"), "w") as f:
    json.dump(output_data, f)
