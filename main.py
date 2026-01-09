import requests
import json
import time
import threading
import os
from flask import Flask, request

app = Flask(__name__)

# --- SETTINGS ---
# अगर फाइल नहीं मिली तो ये डिफ़ॉल्ट यूज़ होंगे
VERIFY_TOKEN = 'आपका_वेरिफाई_टोकन' 

# --- HELPER FUNCTION: TOKEN READING ---
def get_access_token():
    try:
        with open('token.txt', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print("Error: token.txt file nahi mili!")
        return None

# --- HELPER FUNCTION: SEND MESSAGE ---
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

# --- PART 1: FLASK WEBHOOK (Server) ---
@app.route('/', methods=['GET'])
def home():
    return "Server is Running... <br> Go to <a href='/start'>/start</a> to run sender tool."

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get('hub.mode') == 'subscribe' and request.args.get('hub.verify_token') == VERIFY_TOKEN:
            return request.args.get('hub.challenge')
        return 'Invalid verification token'
    else:
        # यहाँ आने वाले मैसेज को हैंडल किया जा सकता है
        return 'Message Received', 200

# --- PART 2: BULK SENDER LOGIC (Background Task) ---
def run_sender_tool():
    print("\n--- Tool Started ---")
    
    # 1. Check Password
    try:
        with open('password.txt', 'r') as f:
            password = f.read().strip()
            if password != 'akash@1234':
                print("❌ Galat Password!")
                return
    except FileNotFoundError:
        print("❌ password.txt file nahi mili.")
        return

    # 2. Load Data
    try:
        token = get_access_token()
        if not token: return

        with open('file.txt', 'r') as f:
            messages = f.readlines()
            
        with open('hatername.txt', 'r') as f:
            hater_names = f.readlines()

        with open('convo.txt', 'r') as f:
            uids = f.readlines()
            
    except FileNotFoundError as e:
        print(f"❌ File missing: {e}")
        return

    # 3. Sending Loop
    print(f"✅ {len(uids)} IDs par message bhejna shuru...")
    
    for uid in uids:
        uid = uid.strip()
        if not uid: continue
        
        for message in messages:
            message = message.strip()
            if not message: continue
            
            for hater in hater_names:
                hater = hater.strip()
                final_message = f"{hater} {message}"
                
                print(f"Sending to {uid}: {final_message}")
                resp = send_graph_message(uid, final_message, token)
                
                # Response Check
                if 'error' in resp:
                    print(f"  --> Failed: {resp['error']['message']}")
                else:
                    print("  --> Sent Successfully")

                # Time sleep to prevent ID Ban
                time.sleep(5) 
    
    print("--- Task Completed ---")

# --- TRIGGER ROUTE ---
@app.route('/start', methods=['GET'])
def start_tool():
    # Threading ka use kar rahe hain taaki server hang na ho
    thread = threading.Thread(target=run_sender_tool)
    thread.start()
    return "<h1>Tool Started in Background!</h1><p>Check Pydroid logs for details.</p>"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
