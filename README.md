# MAX WebSocket Chat Client Example

## English

This example demonstrates how to interact with the MAX messenger via WebSocket.  
It is an **unofficial MAX client** that allows you to:

- Connect to the MAX WebSocket server
- Subscribe to a chat
- Receive and send messages interactively
- Handle ping-pong / keepalive to maintain the connection

It is written in Python and can be used as a template for projects where you want to receive and send messages simultaneously **without additional functions**.

### Requirements

Install the `websocket-client` library:

```bash
pip install websocket-client
```
# Пример WebSocket клиента для чата MAX

## Описание

Этот пример показывает, как работать с мессенджером **MAX** через WebSocket.  
Это **неофициальный клиент MAX**, который позволяет:

- Подключаться к WebSocket-серверу MAX
- Подписываться на чат
- Получать и отправлять сообщения интерактивно
- Обрабатывать ping-pong / поддерживать соединение

Код написан на Python и может служить шаблоном для проектов, где требуется одновременно получать и отправлять сообщения **без дополнительных функций**.

## Требования

Установите библиотеку `websocket-client`:

```bash
pip install websocket-client
```

## Пример кода

```python
import json
import time
from websocket import create_connection, WebSocketConnectionClosedException

# URL WebSocket сервера
url = "wss://ws-api.oneme.ru/websocket"

# Токен (замените на свой)
token = "YOUR_TOKEN_HERE"

# Чат для наблюдения
WATCH_CHAT_ID = -68322721120347

# Подключение к WebSocket
ws = create_connection(url)
print("✅ Подключение установлено")

# Отправка начального handshake
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
print("Ответ на handshake:", response)

# Подписка на чат
subscribe_payload = {
    "ver": 11,
    "cmd": 0,
    "seq": 2,
    "opcode": 65,
    "payload": {"chatId": WATCH_CHAT_ID, "type": "TEXT"}
}
ws.send(json.dumps(subscribe_payload))
print(f"✅ Подписка на чат {WATCH_CHAT_ID} выполнена")

# Отслеживание времени последнего ping
last_ping = time.time()

print("⚡ Готов к получению и отправке сообщений")
while True:
    # Отправка ping каждые 30 секунд
    if time.time() - last_ping > 30:
        ping_payload = {"ver": 11, "cmd": 0, "seq": 999, "opcode": 1, "payload": {"interactive": False}}
        ws.send(json.dumps(ping_payload))
        print("⏳ Отправлен ping")
        last_ping = time.time()

    # Получение сообщений
    try:
        message = ws.recv()
    except WebSocketConnectionClosedException as e:
        print(f"❌ WebSocket закрыт: {e}")
        break
    except Exception as e:
        print(f"⚠ Ошибка при получении сообщения: {e}")
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

        # Переименование отправителя для конкретного ID
        if sender == 49048155:
            sender_name = "Ilmira Akhmetovna"
        else:
            sender_name = str(sender)

        print(f"💬 Новое сообщение в чате {chat_id} от {sender_name}: {text}")

    # Интерактивная отправка
    user_input = input("Введите сообщение для отправки (или 'exit' для выхода): ")
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
    print(f"📤 Отправлено сообщение: {user_input}")

# Корректное закрытие WebSocket
ws.close()
print("🛑 WebSocket закрыт")
```
