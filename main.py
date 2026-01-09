import requests
import json
import time
import threading
import os
from flask import Flask, request

app = Flask(__name__)

# --- SETTINGS ---
VERIFY_TOKEN = 'your_verify_token_here' 

# --- PATH FIX ---
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

# --- सर्वर होमपेज (बटन के साथ) ---
@app.route('/', methods=['GET'])
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Facebook Sender</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f0f2f5; margin: 0; }
            .container { text-align: center; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); width: 80%; max-width: 400px; }
            h1 { color: #1877f2; font-size: 24px; }
            p { color: #606770; margin-bottom: 20px; }
            button { background-color: #42b72a; color: white; border: none; padding: 15px 30px; font-size: 18px; border-radius: 8px; cursor: pointer; width: 100%; font-weight: bold; }
            button:hover { background-color: #36a420; }
            a { text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Server Active ✅</h1>
            <p>Tool chalane ke liye niche button dabayein.</p>
            <a href="/start"><button>START TOOL ▶️</button></a>
        </div>
    </body>
    </html>
    """

# --- टूल चालू करने का बटन ---
@app.route('/start', methods=['GET'])
def start_tool():
    # बैकग्राउंड में टूल चालू करें
    thread = threading.Thread(target=run_sender_tool)
    thread.start()
    return """
    <h1 style='color:green; text-align:center; margin-top:50px;'>
        ✅ Tool Started Successfully!
    </h1>
    <p style='text-align:center;'>Ab aap is page ko band kar sakte hain. Render Logs check karein.</p>
    """

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
