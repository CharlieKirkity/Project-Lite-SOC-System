import requests

def trigger_luan_bot(ip, user, pid):
    bot_token = "8725786598:AAHDxLC-DCtg5m84YK6S_VHHqxPIQJ6QU4w"
    chat_id = "-5078049080"
    
    # Định dạng tin nhắn và Nút bấm y hệt chuẩn của Luân
    text = f"🚨 <b>[CRITICAL ALERT DETECTED]</b> 🚨\n\n<b>Source IP:</b> {ip}\n<b>Target User:</b> {user}\n<b>Process ID:</b> {pid}"
    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "🚫 Block IP", "callback_data": f"block_ip|{ip}"},
                {"text": "💀 Kill Process", "callback_data": f"kill_pid|{pid}"}
            ],
            [
                {"text": "🔒 Lock User", "callback_data": f"lock_user|{user}"},
                {"text": "❌ Ignore Alert", "callback_data": "ignore"}
            ]
        ]
    }
    
    # Bắn tín hiệu lên API của Telegram
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML", "reply_markup": reply_markup})

# Ví dụ khi Script của Tuấn bắt được hacker:
# trigger_luan_bot("192.168.1.99", "root", "5678")
