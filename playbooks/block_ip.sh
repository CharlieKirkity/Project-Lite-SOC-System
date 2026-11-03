SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="$SCRIPT_DIR/../logs/soc_audit.log"
mkdir -p "$(dirname "$LOG_FILE")"

IP_TO_BLOCK=$1
if [ -z "$IP_TO_BLOCK" ]; then
    echo "[ERROR] Vui lòng nhập IP cần chặn! Ví dụ: ./block_ip.sh 192.168.1.100"
    exit 1
fi

sudo ufw status | grep -q "$IP_TO_BLOCK"
if [ $? -eq 0 ]; then
    echo "[INFO] IP $IP_TO_BLOCK đã có trong danh sách chặn của UFW."
    exit 0
fi

sudo ufw insert 1 deny from "$IP_TO_BLOCK" to any > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "[SUCCESS] Đã chặn thành công IP: $IP_TO_BLOCK"
    echo "$(date '+%Y-%m-%d %H:%M:%S') | ACTION: BLOCK_IP | TARGET: $IP_TO_BLOCK | STATUS: SUCCESS" >> "$LOG_FILE"
else
    echo "[ERROR] Không thể chặn IP: $IP_TO_BLOCK"
    exit 1
fi
