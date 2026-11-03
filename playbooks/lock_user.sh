SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="$SCRIPT_DIR/../logs/soc_audit.log"
mkdir -p "$(dirname "$LOG_FILE")"

TARGET_USER=$1
if [ -z "$TARGET_USER" ]; then
    echo "[ERROR] Vui lòng nhập Username cần khóa! Ví dụ: ./lock_user.sh test_victim"
    exit 1
fi

sudo usermod -L "$TARGET_USER" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    sudo pkill -9 -u "$TARGET_USER" > /dev/null 2>&1
    echo "[SUCCESS] Đã khóa thành công tài khoản: $TARGET_USER"
    echo "$(date '+%Y-%m-%d %H:%M:%S') | ACTION: LOCK_USER | TARGET: $TARGET_USER | STATUS: SUCCESS" >> "$LOG_FILE"
else
    echo "[ERROR] Không thể khóa tài khoản: $TARGET_USER"
    exit 1
fi
