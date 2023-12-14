from flask import Flask, request, render_template
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import ImageMessage
from linebot.models import StickerMessage, ImageSendMessage, StickerSendMessage, FollowEvent
from linebot.v3.messaging import (
    TextMessage
)
from datetime import datetime
from flask_socketio import SocketIO, emit
import json, threading, websocket, gateway, random

CHANNEL_ACCESS_TOKEN = "ZRo+y6LRWSWIC3rD0s+gvOITs02zQf6DzmoLtTYA0pLPo6eDHbji0EbwtNkXWiz87n3XRyauo04L78QjcgJtupeuxd0O5il0Pm4fNEvhW4ZYhP7rfXeGTuzNftEddZe5zRnPCBmyVErXGsNAS0CjpQdB04t89/1O/w1cDnyilFU="
CHANNEL_SECRET = "aa907fb7f6f152760bf7742a15a73856"
today_date = datetime.now()
formatted_date = today_date.strftime("%Y-%m-%d")
data = []
 
line_bot = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# 建立 Flask Instance
app = Flask("LineBot")
socketIO = SocketIO(app)

# 定義路由
@app.route("/")
def home():
    return render_template('home.html')
 
@app.post("/callback")
def callback():
    signature: str = request.headers["X-Line-Signature"]
    body: str = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return "Invalid signature.", 400
    return "OK"

@handler.add(FollowEvent)
def handle_join(event):
    user_id = event.source.user_id
    user_profile = line_bot.get_profile(user_id)
    user_name = user_profile.display_name
    welcome_message = f"歡迎 {user_name} 加入！\n"
    welcome_message += "這是個神奇的網站，可以用來製作整人連結\n"
    welcome_message += "https://liff.line.me/2000964921-pXkanzYw"
    line_bot.push_message(user_id, TextSendMessage(text=welcome_message))
    welcome_message = f"點點看這個連結，會發生什麼事呢？\n"
    welcome_message += f"https://liff.line.me/2000964921-pXkanzYw/messages?text=%E8%B3%87%E5%AE%89%E9%80%B1%E5%A5%BD%E5%A5%BD%E7%8E%A9"
    line_bot.push_message(user_id, TextSendMessage(text=welcome_message))
 
# 處理文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event: MessageEvent):
    global formatted_date
    msg: str = event.message.text
    if msg == '資安週好好玩':
        line_bot.reply_message(event.reply_token, TextSendMessage(text=f"對啊對啊，我們還有很多好玩的小遊戲，可以學到很多有趣的資安知識，趕快去體驗巴拉巴拉巴拉巴拉"))
    elif '有趣' in msg or '遊戲' in msg:
        line_bot.reply_message(event.reply_token, TextSendMessage(text=f"我們還有 wi-fi 綿羊牆、翻牌遊戲、密碼學解謎、Dos 展示、藍芽炸屏、Kahoot 搶答等等有趣的小遊戲與技術展示，不要問那麼多了，趕快去瞧瞧吧"))
    elif '喵' in msg:
        line_bot.reply_message(event.reply_token, TextSendMessage(text=f"喵"))
    else:
        words = ["確實", "笑死", "真假", "冷靜", "亂講", "蛤?", "哪有", "沒錯", "虧了", "OuO"]
        word = words[random.randrange(len(words))]
        line_bot.reply_message(event.reply_token, TextSendMessage(text=f"{word}"))
    cur_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for d in data:
        if d["date"] == formatted_date:
            d["msg"].append(msg)
    print(cur_time, msg)

    with open("data.json", "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

    print(f"\033[92mFrom Line Bot Listener：\033[0m", msg)
    socketIO.emit('update_messages', {'data': msg})
    return "OK"


line_bot = LineBotApi(CHANNEL_ACCESS_TOKEN)
 
@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker(event:MessageEvent):
    user_id: str = event.source.user_id
    user = line_bot.get_profile(user_id)
 
    line_bot.reply_message(
        event.reply_token,
        [
            TextSendMessage(text=f"你好 {user.display_name}"),
            ImageSendMessage(original_content_url="https://i.postimg.cc/SNYTkrZy/morning.jpg", preview_image_url="https://i.postimg.cc/SNYTkrZy/morning.jpg"),
        ],
    )
    return "OK"
 
@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event: MessageEvent):
    message_id: str = event.message.id    
    image = line_bot.get_message_content(message_id).content
    with open(f"{message_id}.png", "wb+") as f:
        f.write(image)
    line_bot.reply_message(event.reply_token, TextSendMessage(text=f"以儲存至 {message_id}.png"))
    return "OK"

def run_gateway():
    ws = websocket.WebSocket()
    ws.connect('wss://gateway.discord.gg/?v=6&encording=json')
    event = gateway.recieve_json_response(ws)

    heartbeat_interval = event['d']['heartbeat_interval'] / 1000
    threading._start_new_thread(gateway.heartbeat, (heartbeat_interval, ws))
    gateway.send_json_request(ws, gateway.payload)

    while True:
        event = gateway.recieve_json_response(ws)

        try:
            msg = f"{event['d']['author']['global_name']}: {event['d']['content']}"
            print(f"\033[95mFrom discord Bot Listener：\033[0m", msg)
            socketIO.emit('update_discord_messages', {'data': msg})
            op_code = event("op")
            if op_code == 11:
                print('heartbeat received')
        except:
            pass

# 打開本地對話紀錄
def open_local_data():
    with open ("data.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    for d in data:
        if d["date"] == formatted_date: break
    else:
        data.append({"date": formatted_date, "msg":[]})

# 程式執行時啟動伺服器
if __name__ == "__main__":
    open_local_data()
    # thread1 = threading.Thread(target=run_gateway) # 建立 discord_gateway websocket
    # thread1.start()
    socketIO.run(app, host='127.0.0.1', port=1257) # 建立 line bot websocket