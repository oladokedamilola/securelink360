# SecureLink 360 - Multi-Tenant Network Scanning as a Service

<img src="static/images/securelink.jpeg" alt="SecureLink 360 Logo" width="200"/>

## 🚀 Project Overview

**SecureLink 360** is a **Network Scanning as a Service (SaaS)** platform that empowers companies to protect their internal networks by detecting **unauthorized devices** and **intrusion attempts** in real time.  

It provides **multi-tenant isolation**, **role-based dashboards**, and **live visualizations** so companies can monitor, manage, and secure their networks at scale.  

The system enforces **seat-based licensing**, provides **real-time notifications**, and integrates **employee onboarding** flows for seamless adoption.  

---

## ✅ Core Features

### 🔐 Multi-Tenant & Licensing
- Isolated workspaces for each company.
- Enforced license expiry and seat limits.
- Admin onboarding for employees with secure invite links.

### 👥 Role-Based Dashboards
- **Admins**: Company-wide control → manage networks, employees, unauthorized attempts, intruder logs.
- **Managers**: Team-level oversight → monitor networks under their supervision.
- **Employees**: Self-service → view their networks, request access, see their own attempt history.

### 📝 Access Management
- Employees can **request access** to networks.
- Managers/Admins can **approve/deny join requests**.
- Users get **real-time notifications** when requests are handled.

### 🛡 Intrusion Detection & Logging
- Unauthorized connection attempts auto-detected and logged.
- Intruder logs include MAC, IP, timestamp, and reason.
- Export logs to **CSV/PDF** for compliance.

### 🔔 Real-Time Notifications
- Built on **Django Channels** (WebSockets).
- In-app + sound alerts for:
  - Intruder detection.
  - Join request approvals/denials.
- Notifications scoped by role (admin, manager, employee).

### 🌐 Shared Network Discovery
- Searchable **company-wide directory of networks**.
- Employees can discover & request access.
- Unauthorized outsiders → auto-log attempts.

### 📡 Live Network Visualization
- **Real-time animated graph** using **D3.js / Cytoscape.js**.
- Nodes:
  - 🟢 Users
  - 🖥 Devices
  - 🔴 Intruders (blink until acknowledged)
- Events streamed live via WebSockets.
- Admin/Managers can acknowledge or escalate alerts.

### 🎨 UI & UX
- Responsive sidebar with **mobile-first design**.
- **Light/Dark mode toggle**.
- Company dashboards with clean charts and tables.

---

## ⚙ Installation

### Requirements
- Python 3.10+
- Django 4.x+
- Django Channels 4.x
- Redis (for WebSockets layer)
- Bootstrap 5.x
- PostgreSQL/MySQL (production)

### Local Setup

```bash
# Clone the repository
git clone https://github.com/oladokedamilola/securelink360.git
cd securelink360

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
````

Access the platform at `http://127.0.0.1:8000/`.

---

## 🖥 Usage by Role

### Admin

* Manage **networks, employees, licenses**.
* View **unauthorized attempts & intruder logs**.
* Approve/Deny **join requests**.
* Receive **real-time intrusion alerts**.

### Manager

* Monitor **team networks** only.
* View **team-specific unauthorized attempts**.
* Approve/Deny **employee join requests**.
* Receive **real-time notifications** scoped to their networks.

### Employee

* View **my networks**.
* Submit **join requests**.
* See **join attempt history**.
* Get notified when requests are **approved/denied**.

---

## 🛠 Tech Stack

* **Backend**: Django + Django Channels (Python)
* **Frontend**: Bootstrap 5, D3.js / Cytoscape.js
* **Database**: SQLite (dev), PostgreSQL/MySQL (prod)
* **Real-Time Layer**: Redis + WebSockets
* **Network Scanning**: Python Nmap, Scapy
* **Notifications**: WebSockets + Email
* **Payments**: Stripe/PayPal (SaaS subscriptions)

---

## 📊 System Flow

1. Employees attempt to join → unauthorized attempts logged if not permitted.
2. Join requests are routed to **Manager/Admin** for approval.
3. Unauthorized devices auto-generate **intruder alerts**.
4. Notifications are pushed live via **Django Channels**.
5. Admins & Managers monitor via **real-time network visualization dashboard**.

---

## 📄 License

MIT License

---

