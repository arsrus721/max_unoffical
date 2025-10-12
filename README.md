# WebSocket Chat Client Example

This example demonstrates how to connect to a WebSocket chat server, subscribe to a chat, receive messages, handle **ping-pong/keepalive**, and send messages interactively, all in one script **without using additional functions**.  

It is written in Python and can be used as a template for future projects where you want to receive and send messages simultaneously.

---

## Requirements

Install the `websocket-client` library:

```bash
pip install websocket-client
```

```python

import json
import time
from websocket import create_connection, WebSocketConnectionClosedException

# WebSocket server URL
url = "wss://ws-api.oneme.ru/websocket"

# Token (replace with your own)
token = "YOUR_TOKEN_HERE"

# Chat to watch
WATCH_CHAT_ID = -68322721120347

# Connect to the WebSocket
ws = create_connection(url)
print("✅ Connection established")

# Send initial handshake
init_payload = {
    "ver": 11,
    "cmd": 0,
    "seq": 1,
    "opcode": 19,
    "payload": {
        "interactive": True,
        "token": token,
        "chatsCount": 40,
        "chatsSync": 0,
        "contactsSync": 0,
        "presenceSync": 0,
        "draftsSync": 0
    }
}
ws.send(json.dumps(init_payload))
response = ws.recv()
print("Handshake response:", response)

# Subscribe to the chat
subscribe_payload = {
    "ver": 11,
    "cmd": 0,
    "seq": 2,
    "opcode": 65,
    "payload": {"chatId": WATCH_CHAT_ID, "type": "TEXT"}
}
ws.send(json.dumps(subscribe_payload))
print(f"✅ Subscribed to chat {WATCH_CHAT_ID}")

# Keep track of last ping time
last_ping = time.time()

print("⚡ Ready to receive and send messages")
while True:
    # Ping-pong every 30 seconds
    if time.time() - last_ping > 30:
        ping_payload = {"ver": 11, "cmd": 0, "seq": 999, "opcode": 1, "payload": {"interactive": False}}
        ws.send(json.dumps(ping_payload))
        print("⏳ Sent ping")
        last_ping = time.time()

    # Receive messages
    try:
        message = ws.recv()
    except WebSocketConnectionClosedException as e:
        print(f"❌ WebSocket closed: {e}")
        break
    except Exception as e:
        print(f"⚠ Error receiving message: {e}")
        continue

    if not message:
        continue

    data = json.loads(message)
    opcode = data.get("opcode")
    if opcode in (128, 64):
        payload = data.get("payload", {})
        chat_id = payload.get("chatId")
        if chat_id != WATCH_CHAT_ID:
            continue

        msg = payload.get("message", {})
        sender = msg.get("sender")
        text = msg.get("text", "")

        # Change sender name for a specific ID
        if sender == 49048155:
            sender_name = "Ilmira Akhmetovna"
        else:
            sender_name = str(sender)

        print(f"💬 New message in chat {chat_id} from {sender_name}: {text}")

    # Interactive sending
    user_input = input("Enter message to send (or 'exit' to quit): ")
    if user_input.lower() == "exit":
        break
    send_payload = {
        "ver": 11,
        "cmd": 0,
        "seq": 1000,
        "opcode": 64,
        "payload": {
            "chatId": WATCH_CHAT_ID,
            "message": {"text": user_input, "cid": int(time.time() * 1000), "elements": [], "attaches": []},
            "notify": True
        }
    }
    ws.send(json.dumps(send_payload))
    print(f"📤 Sent message: {user_input}")

# Close WebSocket gracefully
ws.close()
print("🛑 WebSocket closed")
