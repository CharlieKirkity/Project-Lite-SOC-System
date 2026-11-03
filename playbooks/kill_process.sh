SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="$SCRIPT_DIR/../logs/soc_audit.log"
mkdir -p "$(dirname "$LOG_FILE")"

TARGET_PID=$1
if [ -z "$TARGET_PID" ]; then
    echo "[ERROR] Vui lòng nhập PID hoặc tên tiến trình cần diệt! Ví dụ: ./kill_process.sh 1234"
    exit 1
fi

if [[ "$TARGET_PID" =~ ^[0-9]+$ ]]; then
    sudo kill -9 "$TARGET_PID" > /dev/null 2>&1
else
    sudo pkill -9 -f "$TARGET_PID" > /dev/null 2>&1
fi

if [ $? -eq 0 ]; then
    echo "[SUCCESS] Đã tiêu diệt thành công tiến trình: $TARGET_PID"
    echo "$(date '+%Y-%m-%d %H:%M:%S') | ACTION: KILL_PROCESS | TARGET: $TARGET_PID | STATUS: SUCCESS" >> "$LOG_FILE"
else
    echo "[ERROR] Không tìm thấy hoặc không thể diệt tiến trình: $TARGET_PID"
    exit 1
fi
