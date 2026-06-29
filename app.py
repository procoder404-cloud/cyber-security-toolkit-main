# ======================================================
# Cyber Security Toolkit
# app.py - Complete & Unified
# ======================================================

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

import sqlite3
import os
import hashlib
import socket
import secrets
import string
import ipaddress
import cv2
import numpy as np
import ssl

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

# ======================================================
# Flask Configuration
# ======================================================

app = Flask(__name__)

print("Current Folder:", os.getcwd())
print("Templates Folder:", app.template_folder)

# In production, change this to a secure random string
app.secret_key = "CHANGE_THIS_TO_A_RANDOM_SECRET_KEY"

DATABASE = "database.db"

# ======================================================
# Database Helper
# ======================================================

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ======================================================
# Save Scan History
# ======================================================

def save_scan(username, tool_name, result):
    conn = get_db_connection()
    conn.execute(
        """
        INSERT INTO scan_history (username, tool_name, result)
        VALUES (?,?,?)
        """,
        (username, tool_name, result)
    )
    conn.commit()
    conn.close()

# ======================================================
# Home
# ======================================================

@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

# ======================================================
# Register
# ======================================================

@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""
    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]

        if username == "" or email == "" or password == "":
            message = "All fields are required."
        else:
            conn = get_db_connection()
            existing = conn.execute(
                "SELECT * FROM users WHERE username=? OR email=?",
                (username, email)
            ).fetchone()

            if existing:
                message = "Username or Email already exists."
            else:
                hashed_password = generate_password_hash(password)
                conn.execute(
                    """
                    INSERT INTO users (username, email, password)
                    VALUES (?,?,?)
                    """,
                    (username, email, hashed_password)
                )
                conn.commit()
                conn.close()

                flash("Registration Successful! Please Login.")
                return redirect(url_for("login"))
            conn.close()

    return render_template("register.html", message=message)

# ======================================================
# Login
# ======================================================

@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))
        else:
            message = "Invalid Username or Password"

    return render_template("login.html", message=message)

# ======================================================
# Logout
# ======================================================

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ======================================================
# Dashboard
# ======================================================

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", username=session["username"])

# ======================================================
# Tools Directory
# ======================================================

@app.route("/tools")
def tools():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("tools.html")

# ======================================================
# About
# ======================================================

@app.route("/about")
def about():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("about.html")

# ======================================================
# Reports Dashboard
# ======================================================

@app.route("/reports")
def reports():
    if "user_id" not in session:
        return redirect(url_for("login"))

    report = {
        "password_tools": 2,
        "network_tools": 7,
        "hash_tools": 1,
        "total_tools": 11
    }
    return render_template("reports.html", report=report)

# ======================================================
# Password Checker
# ======================================================

@app.route("/password-checker", methods=["GET", "POST"])
def password_checker():
    if "user_id" not in session:
        return redirect(url_for("login"))

    result = None
    if request.method == "POST":
        password = request.form.get("password", "")

        length = len(password) >= 8
        uppercase = any(ch.isupper() for ch in password)
        lowercase = any(ch.islower() for ch in password)
        number = any(ch.isdigit() for ch in password)
        special = any(ch in "!@#$%^&*()-_=+[]{};:,.<>?/|" for ch in password)

        score = 0
        if length: score += 1
        if uppercase: score += 1
        if lowercase: score += 1
        if number: score += 1
        if special: score += 1

        if score == 5:
            strength = "🟢 Strong Password"
        elif score >= 3:
            strength = "🟡 Medium Password"
        else:
            strength = "🔴 Weak Password"

        result = {
            "strength": strength,
            "length": length,
            "uppercase": uppercase,
            "lowercase": lowercase,
            "number": number,
            "special": special
        }
        save_scan(session["username"], "Password Checker", strength)

    return render_template("password_checker.html", result=result)

# ======================================================
# Password Generator
# ======================================================

@app.route("/password-generator", methods=["GET", "POST"])
def password_generator():
    if "user_id" not in session:
        return redirect(url_for("login"))

    password = ""
    if request.method == "POST":
        length = int(request.form["length"])
        chars = ""

        if "uppercase" in request.form: chars += string.ascii_uppercase
        if "lowercase" in request.form: chars += string.ascii_lowercase
        if "numbers" in request.form: chars += string.digits
        if "symbols" in request.form: chars += "!@#$%^&*()_+-=[]{}"

        if chars:
            password = "".join(secrets.choice(chars) for _ in range(length))
            save_scan(session["username"], "Password Generator", "Password Generated")

    return render_template("password_generator.html", password=password)

# ======================================================
# URL Scanner
# ======================================================

@app.route("/url-scanner", methods=["GET", "POST"])
def url_scanner():
    if "user_id" not in session:
        return redirect(url_for("login"))

    result = ""
    if request.method == "POST":
        url = request.form["url"].strip()

        if url.startswith("https://"):
            result = "🟢 Secure HTTPS Website"
        elif url.startswith("http://"):
            result = "🟡 Warning: HTTP Website (Not Secure)"
        else:
            result = "❌ Invalid URL"

        save_scan(session["username"], "URL Scanner", result)

    return render_template("url_scanner.html", result=result)

# ======================================================
# IP Lookup
# ======================================================

@app.route("/ip-lookup", methods=["GET", "POST"])
def ip_lookup():
    if "user_id" not in session:
        return redirect(url_for("login"))

    result = None
    if request.method == "POST":
        ip = request.form["ip"]
        try:
            obj = ipaddress.ip_address(ip)
            result = {
                "address": ip,
                "version": obj.version,
                "type": "Private IP Address" if obj.is_private else "Public IP Address"
            }
        except ValueError:
            result = {"error": "Invalid IP Address"}

    return render_template("ip_lookup.html", result=result)

# ======================================================
# File Hash Checker
# ======================================================

@app.route("/file-hash", methods=["GET", "POST"])
def file_hash():
    if "user_id" not in session:
        return redirect(url_for("login"))

    hashes = None
    if request.method == "POST":
        uploaded_file = request.files.get("file")
        if uploaded_file and uploaded_file.filename:
            data = uploaded_file.read()
            hashes = {
                "md5": hashlib.md5(data).hexdigest(),
                "sha1": hashlib.sha1(data).hexdigest(),
                "sha256": hashlib.sha256(data).hexdigest()
            }
    return render_template("file_hash.html", hashes=hashes)

# ======================================================
# Port Scanner
# ======================================================

@app.route("/port-scanner", methods=["GET", "POST"])
def port_scanner():
    if "user_id" not in session:
        return redirect(url_for("login"))

    results = []
    if request.method == "POST":
        host = request.form["host"]
        common_ports = [20, 21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3389]

        for port in common_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            try:
                status = sock.connect_ex((host, port))
                if status == 0:
                    results.append(f"{port}:OPEN")
                else:
                    results.append(f"{port}:CLOSED")
            except Exception:
                results.append(f"{port}:ERROR")
            finally:
                sock.close()

    return render_template("port_scanner.html", results=results)

# ======================================================
# QR Code Scanner
# ======================================================

@app.route("/qr-scanner", methods=["GET", "POST"])
def qr_scanner():
    if "user_id" not in session:
        return redirect(url_for("login"))

    decoded = ""
    status = ""
    if request.method == "POST":
        file = request.files.get("qrfile")
        if file and file.filename != "":
            image_bytes = np.frombuffer(file.read(), np.uint8)
            image = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)
            detector = cv2.QRCodeDetector()
            data, _, _ = detector.detectAndDecode(image)

            if data:
                decoded = data
                if data.startswith("https://"):
                    status = "🟢 Safe - Secure HTTPS Website"
                elif data.startswith("http://"):
                    status = "🟡 Warning - HTTP Website"
                elif data.startswith("mailto:"):
                    status = "📧 Email QR Code"
                elif data.startswith("tel:"):
                    status = "📞 Phone Number QR Code"
                else:
                    status = "ℹ Valid QR Code"
            else:
                decoded = "No QR Code Found"
                status = "❌ Invalid QR Image"

    return render_template("qr_scanner.html", decoded=decoded, status=status)

# ======================================================
# DNS Lookup
# ======================================================

@app.route("/dns-lookup", methods=["GET", "POST"])
def dns_lookup():
    if "user_id" not in session:
        return redirect(url_for("login"))

    result = ""
    if request.method == "POST":
        domain = request.form["domain"].strip()
        try:
            ip = socket.gethostbyname(domain)
            result = f"Domain : {domain}<br>IP Address : {ip}<br>Status : 🟢 Active"
        except Exception:
            result = "❌ Unable to resolve domain."

    return render_template("dns_lookup.html", result=result)

# ======================================================
# SSL Certificate Checker
# ======================================================

@app.route("/ssl-checker", methods=["GET", "POST"])
def ssl_checker():
    if "user_id" not in session:
        return redirect(url_for("login"))

    result = ""
    if request.method == "POST":
        domain = request.form["domain"].strip()
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as secure_sock:
                    cert = secure_sock.getpeercert()

            issuer = dict(x[0] for x in cert["issuer"]).get("organizationName", "Unknown")
            expiry = cert["notAfter"]

            result = f"""
            <b>🌐 Domain:</b> {domain}<br><br>
            <b>🛡 SSL Status:</b> ✅ Valid Certificate<br><br>
            <b>🏢 Issuer:</b> {issuer}<br><br>
            <b>📅 Expiry Date:</b> {expiry}
            """
        except Exception as e:
            result = f"❌ SSL certificate not found or website unreachable.<br><br><b>Error:</b> {e}"

    return render_template("ssl_checker.html", result=result)

# ======================================================
# Log File Analyzer
# ======================================================

@app.route("/log-analyzer", methods=["GET", "POST"])
def log_analyzer():
    if "user_id" not in session:
        return redirect(url_for("login"))

    result = ""
    if request.method == "POST":
        logfile = request.files.get("logfile")
        if logfile:
            content = logfile.read().decode("utf-8", errors="ignore").upper()

            errors = content.count("ERROR")
            warnings = content.count("WARNING")
            failed = content.count("FAILED")
            success = content.count("SUCCESS")

            risk = "🔴 HIGH RISK" if errors >= 10 else "🟡 MEDIUM RISK" if errors >= 5 else "🟢 LOW RISK"

            result = f"""
            <b>📊 Log Analysis Report</b><br><br>
            ❌ Errors : {errors}<br>
            ⚠ Warnings : {warnings}<br>
            🔐 Failed Logins : {failed}<br>
            ✅ Success Events : {success}<br><br>
            <b>Overall Security Status :</b> {risk}
            """
    return render_template("log_analyzer.html", result=result)

# ======================================================
# Scan History Directory
# ======================================================

@app.route("/history")
def history():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    history_data = conn.execute("SELECT * FROM scan_history ORDER BY id DESC").fetchall()
    conn.close()

    return render_template("history.html", history=history_data)

# ======================================================
# Admin Dashboard (SECURED - Main Admin Username Access Only)
# ======================================================

@app.route("/admin")
def admin():
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Only user registered with the unique username "admin" can enter this dashboard view
    if session.get("username") != "admin":
        flash("Access Denied: Only the main administrator can view backend registered user records.")
        return redirect(url_for("dashboard"))

    conn = get_db_connection()
    users = conn.execute("SELECT id, username, email FROM users ORDER BY id DESC").fetchall()
    total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    total_scans = conn.execute("SELECT COUNT(*) FROM scan_history").fetchone()[0]
    conn.close()

    return render_template(
        "admin.html",
        users=users,
        total_users=total_users,
        total_scans=total_scans
    )

# ======================================================
# Phishing Email Detector
# ======================================================

@app.route("/phishing-detector", methods=["GET", "POST"])
def phishing_detector():
    if "user_id" not in session:
        return redirect(url_for("login"))

    result = ""
    if request.method == "POST":
        email = request.form["email"].lower()
        score = 0

        suspicious_words = [
            "urgent", "verify", "click here", "bank", "password", "login",
            "limited time", "account suspended", "winner", "claim", "gift",
            "bitcoin", "crypto"
        ]

        for word in suspicious_words:
            if word in email:
                score += 1

        if "http://" in email:
            score += 2

        if score >= 5:
            result = "🔴 High Risk - This email contains multiple phishing indicators."
        elif score >= 2:
            result = "🟡 Suspicious - Be careful before clicking any links."
        else:
            result = "🟢 Safe - No obvious phishing indicators detected."

    return render_template("phishing_detector.html", result=result)

# ======================================================
# Custom 404 Error Handler
# ======================================================

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404

# ======================================================
# Run Flask App Server
# ======================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)