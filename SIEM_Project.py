import os
import threading
import socketserver
from flask import Flask, render_template_string, jsonify, make_response
from datetime import datetime
import json
import socket

app = Flask(__name__)

# Shared log storage
logs = []
log_lock = threading.Lock()

class SyslogUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data, socket_ = self.request
        try:
            try:
                message = data.decode('utf-8')
            except UnicodeDecodeError:
                message = data.decode('latin1', errors='replace')
        except Exception as e:
            message = f"<Error decoding message: {str(e)}>"

        ssh_failed_patterns = [
            "failed password",
            "authentication failure",
            "invalid user",
            "connection closed by authenticating user"
        ]
        ssh_success_patterns = [
            "accepted password",
            "accepted publickey",
            "session opened",
            "authentication accepted"
        ]
        ftp_failed_patterns = [
            "login failed",
            "authentication failed",
            "530 login incorrect"
        ]
        

        message_lower = message.lower()
        is_ssh_fail = any(p in message_lower for p in ssh_failed_patterns)
        is_ssh_success = any(p in message_lower for p in ssh_success_patterns)
        is_ftp_fail = any(p in message_lower for p in ftp_failed_patterns)
        is_critical = is_ssh_fail or is_ftp_fail

        log_entry = {
            "source_ip": self.client_address[0],
            "source_port": self.client_address[1],
            "received_at": datetime.utcnow().isoformat() + "Z",
            "message": message,
            "is_alert": is_critical,
            "is_success": is_ssh_success,
            "alert_type": "SSH Failed" if is_ssh_fail else ("FTP Failed" if is_ftp_fail else ("SSH Success" if is_ssh_success else None))
        }

        with log_lock:
            logs.append(log_entry)
            if len(logs) > 500000:
                logs.pop(0)

def start_syslog_server():
    PORT = 514
    try:
        with socketserver.UDPServer(("0.0.0.0", PORT), SyslogUDPHandler) as server:
            print(f"[*] Starting Syslog server on UDP port {PORT}...")
            server.serve_forever()
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"[!] Port {PORT} already in use. Is another instance running?")
        else:
            print(f"[!] Server error: {e}")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SIEM Dashboard</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        body {
            background-color: #1a1a2e;
            color: #e6e6e6;
            line-height: 1.6;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        header {
            text-align: center;
            padding: 30px 0;
            margin-bottom: 30px;
            border-bottom: 3px solid #0f3460;
        }
        h1 {
            font-size: 3.5rem;
            color: #4ecca3;
            margin-bottom: 15px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }
        h2 {
            font-size: 2.2rem;
            color: #4ecca3;
            margin: 25px 0 15px;
        }
        .nav-links {
            display: flex;
            justify-content: center;
            gap: 25px;
            margin: 20px 0;
        }
        .nav-links a {
            font-size: 1.8rem;
            color: #f8b500;
            text-decoration: none;
            padding: 12px 25px;
            border: 2px solid #f8b500;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        .nav-links a:hover {
            background-color: #f8b500;
            color: #1a1a2e;
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(248, 181, 0, 0.4);
        }
        .card {
            background-color: #16213e;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
        }
        .log-entry {
            padding: 18px;
            margin-bottom: 15px;
            background-color: #0f3460;
            border-radius: 8px;
            border-left: 5px solid #4ecca3;
            font-size: 1.4rem;
        }
        .log-entry:nth-child(odd) {
            background-color: #1a3a5f;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            font-size: 1.8rem;
        }
        .stat-box {
            background: linear-gradient(135deg, #0f3460, #1a3a5f);
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }
        .stat-value {
            font-size: 3.5rem;
            font-weight: bold;
            color: #f8b500;
            margin: 15px 0;
        }
        .timestamp {
            color: #4ecca3;
            font-size: 1.2rem;
            margin-top: 5px;
        }
        .ip-address {
            color: #f8b500;
            font-weight: bold;
        }
        .log-message {
            font-size: 1.5rem;
            margin-top: 10px;
            padding: 12px;
            background-color: rgba(0, 0, 0, 0.2);
            border-radius: 6px;
            font-family: monospace;
            white-space: pre-wrap;
            word-break: break-all;
        }
        footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            font-size: 1.2rem;
            color: #4ecca3;
            border-top: 1px solid #0f3460;
        }
        .critical-alert {
            border-left: 5px solid #ff4d4d !important;
            background-color: #5c1a1a !important;
            animation: pulse 2s infinite;
        }
        .success-alert {
            border-left: 5px solid #4dff4d !important;
            background-color: #1a5c1a !important;
        }
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(255, 77, 77, 0.4); }
            70% { box-shadow: 0 0 0 10px rgba(255, 77, 77, 0); }
            100% { box-shadow: 0 0 0 0 rgba(255, 77, 77, 0); }
        }
        .alert-badge {
            background-color: #ff4d4d;
            color: white;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 1.4rem;
            margin-left: 15px;
            font-weight: bold;
        }
        .success-badge {
            background-color: #4dff4d;
            color: #1a1a2e;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 1.4rem;
            margin-left: 15px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>SIEM DASHBOARD</h1>
            <div class="nav-links">
                <a href="/">Dashboard</a>
                <a href="/logs">View Logs</a>
                <a href="/stats">Statistics</a>
            </div>
        </header>
        
        {% block content %}{% endblock %}
        
        <footer>
            <p>SIEM Log Collector | {{ current_year }} | Real-time Security Monitoring</p>
        </footer>
    </div>
</body>
</html>
"""       
DASHBOARD_CONTENT = """
<div class="card">
    <h2>SYSTEM OVERVIEW</h2>
    <p style="font-size: 1.8rem; margin-bottom: 20px;">
        Security Information and Event Management System collecting logs from multiple sources
    </p>
    
    <div class="stats-grid">
        <div class="stat-box">
            <div>Total Logs Collected</div>
            <div class="stat-value">{{ total_logs }}</div>
            <div>since startup</div>
        </div>
        
        <div class="stat-box">
            <div>Latest Log Received</div>
            <div class="timestamp">
                {% if last_log %}
                    {{ last_log.received_at }}
                {% else %}
                    No logs yet
                {% endif %}
            </div>
        </div>
    </div>
</div>

<div class="card">
    <h2>SECURITY ALERTS</h2>
    {% if security_alerts %}
        {% for alert in security_alerts %}
        <div class="log-entry {% if alert.is_alert %}critical-alert{% elif alert.is_success %}success-alert{% endif %}">
            <div>
                <span class="ip-address">{{ alert.source_ip }}</span>
                <span class="timestamp">{{ alert.received_at }}</span>
                {% if alert.is_alert %}
                <span class="alert-badge">{{ alert.alert_type }}</span>
                {% elif alert.is_success %}
                <span class="success-badge">{{ alert.alert_type }}</span>
                {% endif %}
            </div>
            <div class="log-message">{{ alert.message }}</div>
        </div>
        {% endfor %}
    {% else %}
        <div style="text-align:center; padding:20px; font-size:1.8rem;">
            No critical security alerts detected
        </div>
    {% endif %}
</div>

<div class="card">
    <h2>QUICK ACTIONS</h2>
    <div style="font-size: 1.8rem; margin-top: 20px;">
        <p>Send test log: <code>echo "&lt;14&gt;Test Message" | nc -4u -w1 localhost 514</code></p>
        <p style="margin-top: 15px;">Configure devices: <code>*.* @{{ local_ip }}:514</code></p>
        <p style="margin-top: 15px;">Test SSH failure: <code>echo "&lt;14&gt;Failed password for root from 192.168.1.1 port 22 ssh2" | nc -4u -w1 localhost 514</code></p>
        <p style="margin-top: 15px;">Test SSH success: <code>echo "&lt;14&gt;Accepted password for root from 192.168.1.1 port 22 ssh2" | nc -4u -w1 localhost 514</code></p>
    </div>
</div>
"""    
LOGS_CONTENT = """
<div class="card">
    <h2>LATEST SECURITY LOGS</h2>
    <p style="font-size: 1.8rem; margin-bottom: 25px;">
        Showing last 50000 log entries from connected systems
    </p>
    
    {% if logs %}
        {% for log in logs %}
            <div class="log-entry {% if log.is_alert %}critical-alert{% elif log.is_success %}success-alert{% endif %}">
                <div>
                    <span class="ip-address">{{ log.source_ip }}:{{ log.source_port }}</span>
                    <span class="timestamp">{{ log.received_at }}</span>
                    {% if log.is_alert %}
                    <span class="alert-badge">{{ log.alert_type }}</span>
                    {% elif log.is_success %}
                    <span class="success-badge">{{ log.alert_type }}</span>
                    {% endif %}
                </div>
                <div class="log-message">{{ log.message }}</div>
            </div>
        {% endfor %}
    {% else %}
        <div style="text-align: center; padding: 40px; font-size: 2rem;">
            No logs received yet. Waiting for incoming connections...
        </div>
    {% endif %}
</div>
<p>
  <a href="/logs/json" style="color: #f8b500; font-weight: bold; font-size: 1.6rem;">
    Download Logs as JSON
  </a>
</p>
"""         
STATS_CONTENT = """
<div class="card">
    <h2>SYSTEM STATISTICS</h2>
    
    <div class="stats-grid">
        <div class="stat-box">
            <div>Total Logs</div>
            <div class="stat-value">{{ total_logs }}</div>
        </div>
        
        <div class="stat-box">
            <div>Unique Sources</div>
            <div class="stat-value">{{ unique_sources }}</div>
        </div>
        
        <div class="stat-box">
            <div>Security Alerts</div>
            <div class="stat-value">{{ alert_count }}</div>
        </div>
    </div>
    
    {% if last_log %}
    <div style="margin-top: 30px;">
        <h3>Last Log Received</h3>
        <div class="log-entry {% if last_log.is_alert %}critical-alert{% elif last_log.is_success %}success-alert{% endif %}">
            <div>
                <span class="ip-address">{{ last_log.source_ip }}:{{ last_log.source_port }}</span>
                <span class="timestamp">{{ last_log.received_at }}</span>
                {% if last_log.is_alert %}
                <span class="alert-badge">{{ last_log.alert_type }}</span>
                {% elif last_log.is_success %}
                <span class="success-badge">{{ last_log.alert_type }}</span>
                {% endif %}
            </div>
            <div class="log-message">{{ last_log.message }}</div>
        </div>
    </div>
    {% endif %}
</div>
"""        

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "your-server-ip"

@app.route('/')
def dashboard():
    with log_lock:
        total_logs = len(logs)
        last_log = logs[-1] if logs else None
        security_alerts = [log for log in logs if log.get('is_alert') or log.get('is_success')][-5:]
    return render_template_string(
        HTML_TEMPLATE + DASHBOARD_CONTENT,
        total_logs=total_logs,
        last_log=last_log,
        security_alerts=security_alerts,
        current_year=datetime.now().year,
        local_ip=get_local_ip()
    )

@app.route('/logs')
def show_logs():
    with log_lock:
        recent_logs = logs[-10000:][::-1] if logs else []
    return render_template_string(
        HTML_TEMPLATE + LOGS_CONTENT,
        logs=recent_logs
    )

@app.route('/stats')
def show_stats():
    with log_lock:
        total_logs = len(logs)
        unique_sources = len(set(log['source_ip'] for log in logs)) if logs else 0
        last_log = logs[-1] if logs else None
        alert_count = sum(1 for log in logs if log.get('is_alert'))
    return render_template_string(
        HTML_TEMPLATE + STATS_CONTENT,
        total_logs=total_logs,
        unique_sources=unique_sources,
        alert_count=alert_count,
        last_log=last_log,
        current_year=datetime.now().year
    )

@app.route('/logs/json')
def download_logs_json():
    with log_lock:
        data = json.dumps(logs, indent=4)
    
    response = make_response(data)
    response.headers['Content-Type'] = 'application/json'
    response.headers['Content-Disposition'] = f'attachment; filename=siem_logs_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.json'
    return response

if __name__ == '__main__':
    syslog_thread = threading.Thread(target=start_syslog_server, daemon=True)
    syslog_thread.start()
    print("[*] Syslog server thread started")

    app.run(host='0.0.0.0', port=8080, debug=False)