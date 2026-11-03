echo "=== BẮT ĐẦU MÔ PHỎNG TẤN CÔNG KIỂM THỬ SIEM/SOC ==="

CURRENT_HOST=$(hostname)
TODAY_INDEX="siem-logs-$(date -u +%Y.%m.%d)"

echo "[Test Case 1] Mô phỏng tấn công SSH Brute-force (6 lần sai mật khẩu)..."
for i in {1..6}; do
    NOW_ISO=$(date --iso-8601=seconds)
    NOW_UTC=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    LOG_LINE="$NOW_ISO $CURRENT_HOST sshd[500$i]: Failed password for test_victim from 192.168.1.100 port 5000$i ssh2"
    echo "$LOG_LINE" | sudo tee -a /var/log/auth.log >/dev/null
    curl -s -X POST "http://localhost:9200/$TODAY_INDEX/_doc" -H "Content-Type: application/json" -d "{
      \"@timestamp\": \"$NOW_UTC\",
      \"message\": \"$LOG_LINE\",
      \"src_ip\": \"192.168.1.100\",
      \"user\": \"test_victim\",
      \"pid\": \"500$i\",
      \"ssh_event\": \"SSH_LOGIN_FAILED\",
      \"event_category\": \"brute_force\",
      \"log_source\": \"ubuntu_target_server\"
    }" >/dev/null
done
echo " -> Đã ghi nhận 6 lần Brute-force thất bại từ IP 192.168.1.100."

echo "[Test Case 2] Mô phỏng chuỗi tấn công: Chiếm quyền thành công + Đọc /etc/shadow..."
NOW_ISO=$(date --iso-8601=seconds)
NOW_UTC=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
LOG_ACCEPT="$NOW_ISO $CURRENT_HOST sshd[5009]: Accepted password for test_victim from 192.168.1.100 port 50099 ssh2"
LOG_SUDO="$NOW_ISO $CURRENT_HOST sudo: test_victim : TTY=pts/0 ; PWD=/home/test_victim ; USER=root ; COMMAND=/usr/bin/cat /etc/shadow"
echo "$LOG_ACCEPT" | sudo tee -a /var/log/auth.log >/dev/null
echo "$LOG_SUDO" | sudo tee -a /var/log/auth.log >/dev/null

curl -s -X POST "http://localhost:9200/$TODAY_INDEX/_doc" -H "Content-Type: application/json" -d "{
  \"@timestamp\": \"$NOW_UTC\",
  \"message\": \"$LOG_ACCEPT\",
  \"src_ip\": \"192.168.1.100\",
  \"user\": \"test_victim\",
  \"pid\": \"5009\",
  \"ssh_event\": \"SSH_LOGIN_SUCCESS\",
  \"event_category\": \"authentication\",
  \"log_source\": \"ubuntu_target_server\"
}" >/dev/null

curl -s -X POST "http://localhost:9200/$TODAY_INDEX/_doc" -H "Content-Type: application/json" -d "{
  \"@timestamp\": \"$NOW_UTC\",
  \"message\": \"$LOG_SUDO\",
  \"user\": \"test_victim\",
  \"target_user\": \"root\",
  \"command\": \"/usr/bin/cat /etc/shadow\",
  \"ssh_event\": \"PRIVILEGE_ESCALATION\",
  \"event_category\": \"privilege_abuse\",
  \"log_source\": \"ubuntu_target_server\"
}" >/dev/null

curl -s -X POST "http://localhost:9200/$TODAY_INDEX/_refresh" >/dev/null
echo " -> Đã ghi nhận sự kiện đăng nhập thành công và leo thang đặc quyền đọc /etc/shadow."
echo "=== HOÀN TẤT MÔ PHỎNG! ==="
