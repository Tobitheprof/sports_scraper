import requests

# Replace with your actual bot token from BotFather
TOKEN = "8084219997:AAFG3_uGNP-UjvFpsN_W1CN45g8ntw3ZVUM"

def get_updates():
    """
    Calls the /getUpdates endpoint of the Telegram Bot API and
    returns the JSON response as a Python dictionary.
    """
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    response = requests.get(url)
    print(response.json())
    # Convert the response to a dictionary
    return response.json()

def find_chat_ids(updates):
    """
    Parses the 'updates' dictionary and collects unique chat IDs
    from messages and/or channel posts.
    """
    chat_ids = set()
    
    for item in updates.get("result", []):
        # Some updates have 'message', some have 'channel_post', etc.
        if "message" in item:
            chat = item["message"]["chat"]
            chat_ids.add(chat["id"])
        elif "channel_post" in item:
            chat = item["channel_post"]["chat"]
            chat_ids.add(chat["id"])
        elif "edited_message" in item:
            chat = item["edited_message"]["chat"]
            chat_ids.add(chat["id"])
        # Add more conditions if you expect other types of updates
    
    return chat_ids

def main():
    data = get_updates()
    
    # Print the entire update data for debugging (optional)
    # import json
    # print(json.dumps(data, indent=2))
    
    chat_ids = find_chat_ids(data)
    if chat_ids:
        for cid in chat_ids:
            print(f"Found Chat ID: {cid}")
    else:
        print("No chat IDs found. Make sure someone sent a message in the group/channel.")

if __name__ == "__main__":
    main()
