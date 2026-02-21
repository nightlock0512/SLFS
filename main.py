import os
import socket
import threading
from flask import Flask, send_from_directory, request
import webbrowser

# ポート
PORT_PUBLIC = 5000
PORT_PRIVATE = 5001

# 共有ファイルのパスと名前
shared_file = {'name': None, 'path': None}

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except: ip = "127.0.0.1"
    finally: s.close()
    return ip

# ファイル送信側
admin_app = Flask("admin")

@admin_app.route('/', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            path = os.path.join(os.getcwd(), file.filename)
            file.save(path)
            shared_file['name'] = file.filename
            shared_file['path'] = path
    
    return f"""
    <h1>ファイルを送信</h1>
    <p>現在の共有: {shared_file['name'] or 'なし'}</p>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="file" onchange="this.form.submit()">
    </form>
    <hr>
    <p>相手に教えるURL: http://{get_ip()}:{PORT_PUBLIC}</p>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
    <div id="qrcode"></div>
    <script>
    new QRCode(document.getElementById("qrcode"), "http://{get_ip()}:{PORT_PUBLIC}");
    </script>
    """

# ファイル受信側
public_app = Flask("public")

@public_app.route('/')
def public_view():
    if not shared_file['name']:
        return "<h1>待機中...</h1><p>送信者が準備するまでお待ちください。</p>"
    
    return f"""
    <h1>ファイルが届いています</h1>
    <p>ファイル名: {shared_file['name']}</p>
    <a href="/download" style="padding:10px; background:green; color:white; text-decoration:none;">ダウンロード</a>
    """

# 送信ページ
@public_app.route('/download')
def download():
    if shared_file['path']:
        return send_from_directory(os.getcwd(), shared_file['name'], as_attachment=True)
    return "Not Found", 404


if __name__ == '__main__':
    t = threading.Thread(target=lambda: public_app.run(host='0.0.0.0', port=PORT_PUBLIC, debug=False, use_reloader=False))
    t.daemon = True
    t.start()


    print(f"--- 起動完了 ---")
    print(f"【ファイル送信】 http://localhost:{PORT_PRIVATE}")
    print(f"【ファイル受信】 http://{get_ip()}:{PORT_PUBLIC}")

    webbrowser.open(f"http://localhost:{PORT_PRIVATE}")
    
    admin_app.run(host='127.0.0.1', port=PORT_PRIVATE, debug=False)
