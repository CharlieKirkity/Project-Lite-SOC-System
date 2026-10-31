"""
Task 3.6 - Event Correlation Engine Script
Người thực hiện: Võ Quang Minh Tuấn
Chức năng: Truy vấn Elasticsearch 8.11.0 API (Query DSL) để phát hiện chuỗi tấn công:
SSH Brute-force -> Đăng nhập thành công -> Leo thang đặc quyền (đọc /etc/shadow).
"""

import time
import requests
from datetime import datetime, timezone, timedelta

ES_URL = "http://localhost:9200/siem-logs-*/_search"
BRUTE_FORCE_THRESHOLD = 5
TIME_WINDOW_MINUTES = 60

def es_query(payload):
    resp = requests.post(ES_URL, json=payload, headers={"Content-Type": "application/json"}, timeout=10)
    if resp.status_code == 200:
        return resp.json()
    return {}

def detect_attack_chains():
    alerts = []
    now = datetime.now(timezone.utc)
    time_from = (now - timedelta(minutes=TIME_WINDOW_MINUTES)).isoformat()

    # 1. Truy vấn các IP đăng nhập SSH thất bại >= 5 lần
    bf_payload = {
        "size": 0,
        "query": {
            "bool": {
                "filter": [
                    {"range": {"@timestamp": {"gte": time_from}}},
                    {"term": {"ssh_event.keyword": "SSH_LOGIN_FAILED"}}
                ]
            }
        },
        "aggs": {
            "suspicious_ips": {
                "terms": {
                    "field": "src_ip.keyword",
                    "min_doc_count": BRUTE_FORCE_THRESHOLD
                },
                "aggs": {
                    "target_users": {"terms": {"field": "user.keyword", "size": 5}},
                    "last_pid": {"terms": {"field": "pid.keyword", "size": 1}}
                }
            }
        }
    }

    res = es_query(bf_payload)
    ip_buckets = res.get("aggregations", {}).get("suspicious_ips", {}).get("buckets", [])

    for bucket in ip_buckets:
        src_ip = bucket["key"]
        fail_count = bucket["doc_count"]
        user_buckets = bucket["target_users"]["buckets"]
        target_user = user_buckets[0]["key"] if user_buckets else "unknown"
        pid_buckets = bucket["last_pid"]["buckets"]
        pid = pid_buckets[0]["key"] if pid_buckets else "0"

        # 2. Kiểm tra IP này có đăng nhập thành công sau đó không
        success_payload = {
            "query": {
                "bool": {
                    "filter": [
                        {"range": {"@timestamp": {"gte": time_from}}},
                        {"term": {"src_ip.keyword": src_ip}},
                        {"term": {"ssh_event.keyword": "SSH_LOGIN_SUCCESS"}}
                    ]
                }
            }
        }
        success_hits = es_query(success_payload).get("hits", {}).get("total", {}).get("value", 0)

        # 3. Kiểm tra hành vi leo thang đặc quyền (Sudo / đọc /etc/shadow)
        priv_payload = {
            "query": {
                "bool": {
                    "filter": [
                        {"range": {"@timestamp": {"gte": time_from}}},
                        {"term": {"ssh_event.keyword": "PRIVILEGE_ESCALATION"}}
                    ]
                }
            }
        }
        priv_hits = es_query(priv_payload).get("hits", {}).get("total", {}).get("value", 0)

        if success_hits > 0 and priv_hits > 0:
            severity = "CRITICAL"
            description = (
                f"Phát hiện chuỗi tấn công từ IP {src_ip}: "
                f"Brute-force ({fail_count} lần) -> Chiếm quyền User '{target_user}' -> Leo thang đặc quyền (sudo/shadow)."
            )
        elif success_hits > 0:
            severity = "CRITICAL"
            description = f"IP {src_ip} đã Brute-force thành công vào user '{target_user}' sau {fail_count} lần thử sai!"
        else:
            severity = "HIGH"
            description = f"Phát hiện SSH Brute-force từ IP {src_ip} vào user '{target_user}' ({fail_count} lần thất bại)."

        alerts.append({
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "severity": severity,
            "src_ip": src_ip,
            "user": target_user,
            "pid": pid,
            "failed_attempts": fail_count,
            "description": description
        })

    return alerts

if __name__ == "__main__":
    print("[*] Khởi động SIEM Event Correlation Engine (Võ Quang Minh Tuấn)...")
    while True:
        try:
            for alert in detect_attack_chains():
                print(f"[{alert['timestamp']}] [{alert['severity']}] {alert['description']}")
        except Exception as err:
            print(f"[!] Đang chờ kết nối Elasticsearch: {err}")
        time.sleep(10)
