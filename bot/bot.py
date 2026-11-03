import os
import time
import threading
import subprocess
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from correlation_engine import detect_attack_chains

BOT_TOKEN = "8725786598:AAHDxLC-DCtg5m84YK6S_VHHqxPIQJ6QU4w"
CHAT_ID = "7051361855" 
SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../playbooks"))

bot = telebot.TeleBot(BOT_TOKEN)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "ignore":
        try:
            bot.edit_message_text("✅ Đã bỏ qua cảnh báo.", chat_id=call.message.chat.id, message_id=call.message.message_id)
        except:
            pass
        return

    action, target = call.data.split('|')
    script_map = {
        "block_ip": "block_ip.sh", 
        "kill_pid": "kill_process.sh", 
        "lock_user": "lock_user.sh"
    }
    
    script_name = script_map.get(action)
    if script_name:
        script_path = os.path.join(SCRIPT_DIR, script_name)
        
        # Bỏ qua lỗi nút bấm quá hạn
        try:
            bot.answer_callback_query(call.id, "Đang thực thi lệnh trên Ubuntu...")
        except:
            pass

        try:
            res = subprocess.run(["sudo", "bash", script_path, target], capture_output=True, text=True)
            output = res.stdout.strip() or res.stderr.strip()
            
            # CẮT NGẮN KẾT QUẢ SOAR TỪ UBUNTU TRẢ VỀ NẾU NÓ QUÁ DÀI
            if len(output) > 2000:
                output = output[:2000] + "\n\n... [KẾT QUẢ ĐÃ BỊ CẮT BỚT DO QUÁ DÀI]"
            
            bot.edit_message_text(f"⚡ *KẾT QUẢ SOAR:*\n`{output}`", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="Markdown")
        except Exception as e:
            pass

def alert_scanner():
    alerted_keys = set()
    while True:
        try:
            alerts = detect_attack_chains()
            for alert in alerts:
                if alert['severity'] == "CRITICAL":
                    alert_key = f"{alert['src_ip']}_{alert['timestamp']}"
                    
                    if alert_key not in alerted_keys:
                        alerted_keys.add(alert_key)
                        
                        desc = str(alert['description'])
                        if len(desc) > 2000:
                            desc = desc[:2000] + "\n\n... [CẢNH BÁO ĐÃ BỊ CẮT BỚT DO VƯỢT QUÁ GIỚI HẠN]"

                        text = (f"🚨 <b>[CRITICAL ALERT DETECTED]</b>\n\n"
                                f"🌐 <b>Source IP:</b> {alert['src_ip']}\n"
                                f"🎯 <b>Target User:</b> {alert['user']}\n"
                                f"⚙️ <b>Process ID:</b> {alert['pid']}\n\n"
                                f"⚠️ <b>{desc}</b>")
                        
                        markup = InlineKeyboardMarkup()
                        markup.add(
                            InlineKeyboardButton("🛡️ Block IP", callback_data=f"block_ip|{alert['src_ip']}"),
                            InlineKeyboardButton("💀 Kill Process", callback_data=f"kill_pid|{alert['pid']}")
                        )
                        markup.add(
                            InlineKeyboardButton("🔒 Lock User", callback_data=f"lock_user|{alert['user']}"),
                            InlineKeyboardButton("❌ Ignore Alert", callback_data="ignore")
                        )
                        bot.send_message(CHAT_ID, text, parse_mode="HTML", reply_markup=markup)
        except Exception as e:
            pass
        time.sleep(10)

if __name__ == "__main__":
    print("🚀 Telegram Bot SOC đang chạy và liên kết với SIEM...")
    threading.Thread(target=alert_scanner, daemon=True).start()
    # skip_pending=True giúp dọn dẹp các lệnh cũ bị kẹt, tránh crash bot
    bot.infinity_polling(skip_pending=True)
