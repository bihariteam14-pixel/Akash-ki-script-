import requests
import json
import time
import threading
import os
from flask import Flask, request

app = Flask(__name__)

# --- SETTINGS ---
VERIFY_TOKEN = 'आपका_वेरिफाई_टोकन' 

# --- HELPER FUNCTION: SEND MESSAGE ---
def send_graph_message(uid, message_text, access_token):
    # Code 2 के अनुसार API URL (me/messages) का उपयोग किया गया है
    url = f"https://graph.facebook.com/v16.0/me/messages?access_token={access_token}"
    
    headers = {
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
    return "Server is Running... <br> Go to <a href='/start'>/start</a> to run the sender tool."

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get('hub.mode') == 'subscribe' and request.args.get('hub.verify_token') == VERIFY_TOKEN:
            return request.args.get('hub.challenge')
        return 'Invalid verification token'
    else:
        # यहाँ आने वाले मैसेज को हैंडल किया जा सकता है
        return 'Message Received', 200

# --- PART 2: BULK SENDER LOGIC (Merged Code) ---
def run_sender_tool():
    print("\n--- Tool Started in Background ---")
    
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

    # 2. Load Data Files
    try:
        # Token Load
        with open('token.txt', 'r') as f:
            token = f.read().strip()

        # Messages Load
        with open('file.txt', 'r', encoding='utf-8') as f:
            messages = f.readlines()
            
        # Hater Names Load
        with open('hatername.txt', 'r', encoding='utf-8') as f:
            hater_names = f.readlines()

        # UIDs Load
        with open('convo.txt', 'r') as f:
            uids = f.readlines()
        
        # Time Delay Load (Code 2 se)
        with open('time.txt', 'r') as f:
            delay = int(f.read().strip())

    except FileNotFoundError as e:
        print(f"❌ File missing: {e}")
        return
    except ValueError:
        print("❌ time.txt me sirf number hona chahiye!")
        return

    print(f"✅ Loaded: {len(uids)} UIDs, Speed: {delay} seconds")

    # 3. Main Loop (Code 2 ka Logic)
    # यह लूप लगातार चलता रहेगा (While True)
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
                        
                        # मैसेज तैयार करना
                        final_message = f"{hater} {message}"
                        
                        print(f"Sending to {uid}: {final_message}")
                        
                        # मैसेज भेजना
                        resp = send_graph_message(uid, final_message, token)
                        
                        # रिजल्ट प्रिंट करना
                        if 'error' in resp:
                            print(f"  --> Failed: {resp['error']['message']}")
                        else:
                            print("  --> Sent Successfully")

                        # Code 2 वाला टाइमर
                        time.sleep(delay)

            print("--- One Loop Completed, Restarting... ---")
            
        except Exception as e:
            print(f"Error in loop: {e}")
            time.sleep(10) # एरर आने पर 10 सेकंड रुकेगा फिर चलेगा

# --- TRIGGER ROUTE ---
@app.route('/start', methods=['GET'])
def start_tool():
    # Threading का उपयोग ताकि सर्वर और लूप दोनों साथ चलें
    thread = threading.Thread(target=run_sender_tool)
    thread.start()
    return f"<h1>Tool Started!</h1><p>Check logs. Messages will be sent every X seconds from time.txt.</p>"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)                    
