import json
import threading
import time
from websocket import create_connection, WebSocketConnectionClosedException

class ChatClient:
    def __init__(self, url, token, watch_chats=None, user_agent=None):
        self.url = url
        self.token = token
        self.watch_chats = watch_chats or []
        self.user_agent = user_agent or "PythonWebSocketClient/1.0"
        self.ws = None
        self.seq = 0
        self.running = False

    def connect(self):
        headers = [
            ("Origin", "https://web.max.ru"),
            ("User-Agent", self.user_agent)
        ]
        self.ws = create_connection(self.url, header=[f"{h[0]}: {h[1]}" for h in headers])
        print("✅ Соединение установлено")
        self.running = True
        # Можно сразу отправить handshake
        self.send_handshake()

    def send_handshake(self):
        self.seq += 1
        payload = {
            "ver": 11,
            "cmd": 0,
            "seq": self.seq,
            "opcode": 19,
            "payload": {
                "interactive": True,
                "token": self.token,
                "chatsCount": len(self.watch_chats),
                "chatsSync": 0,
                "contactsSync": 0,
                "presenceSync": 0,
                "draftsSync": 0
            }
        }
        self.send(payload)

    def subscribe_chat(self, chat_id):
        """Подписка на чат для получения сообщений"""
        self.seq += 1
        payload = {"ver": 11, "cmd": 0, "seq": self.seq, "opcode": 65, "payload": {"chatId": chat_id, "type": "TEXT"}}
        self.send(payload)
        print(f"✅ Подписка на чат ID {chat_id}")

    def send_message(self, chat_id, text):
        """Отправка сообщения в чат"""
        self.seq += 1
        payload = {
            "ver": 11,
            "cmd": 0,
            "seq": self.seq,
            "opcode": 64,
            "payload": {
                "chatId": chat_id,
                "message": {
                    "text": text,
                    "cid": int(time.time()*1000),
                    "elements": [],
                    "attaches": []
                },
                "notify": True
            }
        }
        self.send(payload)
        print(f"💬 Сообщение отправлено в чат {chat_id}: {text}")

    def send(self, data):
        """Отправка произвольного JSON payload"""
        if self.ws:
            self.ws.send(json.dumps(data))

    def receive_loop(self, callback):
        """Бесконечный цикл для обработки входящих сообщений"""
        try:
            while self.running:
                try:
                    message = self.ws.recv()
                except WebSocketConnectionClosedException:
                    print("❌ WebSocket закрыт сервером")
                    break
                except Exception as e:
                    print(f"⚠ Ошибка при получении сообщения: {e}")
                    continue

                if not message:
                    continue

                data = json.loads(message)
                callback(data)

        finally:
            self.ws.close()

    def start_keepalive(self, interval=30):
        """Отправка ping/pong каждые interval секунд"""
        def keepalive():
            while self.running:
                self.seq += 1
                ping_payload = {"ver": 11, "cmd": 0, "seq": self.seq, "opcode": 1, "payload": {"interactive": False}}
                try:
                    self.send(ping_payload)
                except:
                    break
                time.sleep(interval)
        threading.Thread(target=keepalive, daemon=True).start()

    def stop(self):
        self.running = False
        if self.ws:
            self.ws.close()
