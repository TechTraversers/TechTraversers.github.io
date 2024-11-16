from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__, template_folder='.')  # Set the template folder to the current directory

# Create database and table if it doesn't exist
def init_db():
    conn = sqlite3.connect('ips.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS visitor_ips
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, ip_address TEXT, visit_time DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# Insert IP into database
def log_ip(ip):
    conn = sqlite3.connect('ips.db')
    c = conn.cursor()
    c.execute("INSERT INTO visitor_ips (ip_address) VALUES (?)", (ip,))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    user_ip = request.remote_addr  # Get the user's IP address
    log_ip(user_ip)  # Store the IP address in the database
    return render_template('index.html')  # Render the index.html template

@app.route('/view_ips')
def view_ips():
    conn = sqlite3.connect('ips.db')
    c = conn.cursor()
    c.execute("SELECT id, ip_address, visit_time FROM visitor_ips")
    ips = c.fetchall()
    conn.close()

    # Format the IPs in a simple table
    return '<br>'.join([f"ID: {ip[0]}, IP: {ip[1]}, Time: {ip[2]}" for ip in ips])

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)
