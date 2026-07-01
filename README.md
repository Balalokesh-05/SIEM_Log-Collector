# 🛡️ SIEM Log Collector Tool

A lightweight Security Information and Event Management (SIEM) log collection tool developed to centralize, process, and monitor security logs from multiple sources. This project demonstrates how log collection and basic security monitoring can be implemented using Python.

---

## 📖 Overview

The SIEM Log Collector Tool collects security logs from different systems and prepares them for centralized monitoring and analysis. It helps security analysts detect suspicious activities, investigate incidents, and monitor system events through an easy-to-use interface.

This project was developed as part of **T-Hub Project Space 7.0**.

---

## ✨ Features

- 📥 Collects logs from multiple sources
- 🔍 Parses and processes security events
- 📊 Displays logs through a simple dashboard
- 👥 User authentication support
- 🗄️ SQLite database integration
- ⚙️ Configurable log collection
- 📈 Supports SIEM workflow demonstrations

---

## 🏗️ Project Architecture

```text
Log Sources
     │
     ▼
Configuration Files
(rsyslog / nxlog)
     │
     ▼
Python SIEM Collector
     │
     ▼
SQLite Database
     │
     ▼
Web Dashboard
     │
     ▼
Security Monitoring
```

---

## 📂 Project Structure

```
SIEMLogCollectorTool/
│
├── SIEMProject.py
├── README.md
├── siem_users.db
├── jq.txt
├── nxlog.conf
├── krsyslog.conf
├── ursyslog.conf
├── siemposter.html
└── Screenshot images
```

---

## 🛠️ Technologies Used

- Python
- SQLite
- HTML
- CSS
- JavaScript
- NXLog
- RSyslog
- Windows Event Logs
- Linux System Logs

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/Balalokesh-05/SIEM_Log-Collector.git
```

### Navigate to the project

```bash
cd SIEM_Log-Collector
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

*(If your project does not include a `requirements.txt`, install the required Python libraries manually.)*

### Run the Project

```bash
python SIEMProject.py
```

---

## 📸 Screenshots

Add screenshots here.

Example:

```
screenshots/
├── dashboard.png
├── login.png
└── log-monitor.png
```

---

## 🔐 Security Monitoring Workflow

1. Collect logs from endpoints.
2. Parse incoming log events.
3. Store logs in SQLite database.
4. Display logs through the dashboard.
5. Monitor suspicious activities.
6. Support basic incident investigation.

---

## 🎯 Learning Outcomes

- SIEM fundamentals
- Log collection
- Security monitoring
- Event management
- Python application development
- Configuration of NXLog and RSyslog
- Database integration

---

## 🚀 Future Enhancements

- Elasticsearch integration
- Kibana Dashboard
- Real-time alerts
- Email notifications
- Threat Intelligence Integration
- MITRE ATT&CK Mapping
- Multi-user Role Management
- Cloud Log Collection

---

## 👨‍💻 Team Project

This project was developed collaboratively during **T-Hub Project Space 7.0**.

This repository is maintained as **my personal portfolio copy** to showcase my learning, contributions, and the final implementation.

---

## 👤 Author

**Lutukurthi Bala Lokesh**

🎓 MCA Graduate

🛡️ Cybersecurity Enthusiast

💻 Python | SIEM | Ethical Hacking | Machine Learning

GitHub: https://github.com/Balalokesh-05

---

## ⭐ If you like this project

Please consider giving the repository a ⭐ on GitHub.

---

## 📄 License

This project is intended for educational and portfolio purposes.
