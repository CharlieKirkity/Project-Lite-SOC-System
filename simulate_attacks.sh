#!/bin/bash
# Task 4.1 & 4.2 - Kịch bản mô phỏng tấn công kiểm thử SIEM (Võ Quang Minh Tuấn)
echo "=== BẮT ĐẦU MÔ PHỎNG TẤN CÔNG KIỂM THỬ SIEM/SOC ==="

for i in {1..6}; do
    echo "Oct 31 17:35:0$i ubuntu sshd[400$i]: Failed password for test_victim from 192.168.1.100 port 5000$i ssh2" | sudo tee -a /var/log/auth.log /var/log/syslog >/dev/null
done
echo " -> Đã ghi nhận 6 lần Brute-force thất bại từ IP 192.168.1.100."

echo "Oct 31 17:35:10 ubuntu sshd[4009]: Accepted password for test_victim from 192.168.1.100 port 50099 ssh2" | sudo tee -a /var/log/auth.log /var/log/syslog >/dev/null
echo "Oct 31 17:35:15 ubuntu sudo: test_victim : TTY=pts/0 ; PWD=/home/test_victim ; USER=root ; COMMAND=/usr/bin/cat /etc/shadow" | sudo tee -a /var/log/auth.log /var/log/syslog >/dev/null
echo " -> Đã ghi nhận sự kiện đăng nhập thành công và leo thang đặc quyền đọc /etc/shadow."
echo "=== HOÀN TẤT MÔ PHỎNG! ==="
