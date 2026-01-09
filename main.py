import requests
import json
import time
import threading
import os
from flask import Flask, request

app = Flask(__name__)

# --- SETTINGS ---
VERIFY_TOKEN = 'your_verify_token_here' 

# --- PATH FIX (यही सबसे ज़रूरी है) ---
# यह लाइन सर्वर को बताती है कि फाइलें कहाँ रखी हैं
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_file_path(filename):
    return os.path.join(BASE_DIR, filename)

# --- टोकन पढ़ना ---
def get_access_token():
    try:
        with open(get_file_path('token.txt'), 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print("❌ Error: token.txt फाइल नहीं मिली!")
        return None

# --- मैसेज भेजने का फंक्शन ---
def send_graph_message(uid, message_text, access_token):
    url = f"https://graph.facebook.com/v16.0/{uid}/messages"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    payload = {
        'recipient': {'id': uid},
        'message': {'text': message_text}
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# --- सर्वर होमपेज ---
@app.route('/', methods=['GET'])
def home():
    return "Server चल रहा है... टूल चलाने के लिए /start पर जाएं।"

# --- टूल चालू करने का बटन ---
@app.route('/start', methods=['GET'])
def start_tool():
    # बैकग्राउंड में टूल चालू करें
    thread = threading.Thread(target=run_sender_tool)
    thread.start()
    return "<h1>टूल चालू हो गया है! Render Logs चेक करें।</h1>"

# --- असली काम (मैसेज भेजना) ---
def run_sender_tool():
    print("\n--- Tool Started ---")
    
    # 1. पासवर्ड चेक
    try:
        with open(get_file_path('password.txt'), 'r') as f:
            password = f.read().strip()
            if password != 'akash@1234':
                print("❌ गलत पासवर्ड!")
                return
    except FileNotFoundError:
        print("❌ password.txt फाइल नहीं मिली।")
        return

    # 2. डेटा लोड करना
    token = get_access_token()
    if not token: return

    try:
        with open(get_file_path('file.txt'), 'r') as f:
            messages = f.readlines()
        with open(get_file_path('hatername.txt'), 'r') as f:
            hater_names = f.readlines()
        with open(get_file_path('convo.txt'), 'r') as f:
            uids = f.readlines()
        with open(get_file_path('time.txt'), 'r') as f:
            delay = int(f.read().strip())
    except FileNotFoundError as e:
        print(f"❌ फाइल नहीं मिली: {e}")
        return
    except ValueError:
        delay = 5 # अगर time.txt खाली हो तो 5 सेकंड
        
    print(f"✅ Loaded {len(uids)} IDs. Speed: {delay} seconds.")

    # 3. भेजने का लूप
    while True:
        try:
            for uid in uids:
                uid = uid.strip()
                if not uid: continue
                
                for message in messages:
                    message = message.strip()
                    if not message: continue
                    
                    for hater in hater_names:
                        hater = hater.strip()
                        final_message = f"{hater} {message}"
                        
                        # लॉग्स में प्रिंट करें ताकि आप देख सकें
                        print(f"Sending to {uid}: {final_message}")
                        
                        resp = send_graph_message(uid, final_message, token)
                        
                        if 'error' in resp:
                            print(f"  --> Failed: {resp['error']['message']}")
                        else:
                            print("  --> Sent Successfully")

                        time.sleep(delay)
        except Exception as e:
            print(f"Error in loop: {e}")
            time.sleep(10)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
