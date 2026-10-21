import requests

TOKEN = "8725786598:AAHDxLC-DCtg5m84YK6S_VHHqxPIQJ6QU4w"
CHAT_ID = "-5078049080"

def send_soc_alert():
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    message = (
        "🚨 *CẢNH BÁO BẢO MẬT SOC* 🚨\n\n"
        "• *Sự kiện:* Phát hiện đăng nhập SSH sai liên tục từ IP lạ.\n"
        "• *IP:* `192.168.1.100`\n"
        "• *Mức độ:* Nghiêm trọng!"
    )
    
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": [
                [
                    {"text": "🚫 Block IP", "callback_data": "block_ip"},
                    {"text": "💀 Kill Process", "callback_data": "kill_process"}
                ],
                [
                    {"text": "🔒 Lock User", "callback_data": "lock_user"}
                ]
            ]
        }
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Đã gửi tin nhắn cảnh báo thành công!")
    else:
        print("Lỗi khi gửi tin nhắn:", response.text)

if __name__ == "__main__":
    send_soc_alert()
