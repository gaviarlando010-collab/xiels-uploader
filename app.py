from flask import Flask, request, render_template_string, jsonify
import requests
import re

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>👑 Royal Uploader - Railway</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; font-family:'Segoe UI',sans-serif; }
        body { background:linear-gradient(145deg,#0a0e1a,#141b2b); min-height:100vh; display:flex; justify-content:center; align-items:center; padding:20px; }
        .card { background:rgba(22,28,46,0.9); backdrop-filter:blur(12px); border-radius:32px; padding:40px 35px; max-width:550px; width:100%; border:1px solid rgba(255,215,0,0.2); box-shadow:0 25px 50px -8px rgba(0,0,0,0.8); }
        h1 { text-align:center; font-weight:700; font-size:28px; background:linear-gradient(135deg,#f9d976,#f39c12); -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:8px; }
        .sub { text-align:center; color:#aab; font-size:14px; margin-bottom:28px; border-bottom:1px dashed #2a3350; padding-bottom:16px; }
        .sub strong { color:#f1c40f; }
        label { display:block; color:#ccd; font-size:13px; font-weight:500; margin-top:18px; margin-bottom:5px; }
        input[type="text"], input[type="file"] { width:100%; padding:12px 16px; border-radius:14px; border:none; background:#262d44; color:#fff; font-size:14px; outline:1px solid #3e4764; transition:0.2s; }
        input:focus { outline:2px solid #f1c40f; background:#1e2438; }
        input[type="file"] { padding:10px; background:#1f253b; cursor:pointer; }
        .btn { width:100%; margin-top:24px; padding:14px; border:none; border-radius:40px; font-weight:700; font-size:18px; color:#0b0e1a; background:linear-gradient(135deg,#f1c40f,#f39c12); cursor:pointer; transition:0.25s; box-shadow:0 6px 0 #b37b0e; }
        .btn:hover { transform:translateY(-2px); box-shadow:0 10px 0 #b37b0e; }
        .btn:active { transform:translateY(4px); box-shadow:0 2px 0 #b37b0e; }
        .btn:disabled { opacity:0.5; transform:translateY(4px); box-shadow:0 2px 0 #b37b0e; pointer-events:none; }
        #log { margin-top:24px; background:#0b0e1a; border-radius:16px; padding:16px; max-height:200px; overflow-y:auto; font-family:'Courier New',monospace; font-size:13px; color:#8cf; border:1px solid #2a3350; white-space:pre-wrap; line-height:1.6; }
        .success { color:#2ecc71; }
        .warn { color:#f1c40f; }
        .error { color:#e74c3c; }
        .info { color:#85c1e9; }
        .footer { margin-top:20px; text-align:center; color:#445; font-size:12px; }
        .footer span { color:#f1c40f; }
        ::-webkit-scrollbar { width:4px; }
        ::-webkit-scrollbar-thumb { background:#f1c40f; border-radius:10px; }
    </style>
</head>
<body>
<div class="card">
    <h1>🚀 ROYAL UPLOADER</h1>
    <div class="sub">⚡ Hosting di <strong>Railway</strong> — Upload langsung ke Creator Store</div>

    <label>👑 Cookie .ROBLOSECURITY (WAJIB!)</label>
    <input type="text" id="cookie" placeholder="_|WARNING:-DO-NOT-SHARE..." />

    <label>🔑 CSRF Token (isi jika otomatis gagal)</label>
    <input type="text" id="csrf" placeholder="Kosongkan jika otomatis, isi manual jika perlu" />

    <label>📁 Pilih File Model (.rbxm / .obj / .fbx / .glb)</label>
    <input type="file" id="fileInput" accept=".rbxm,.obj,.fbx,.glb,.stl" />

    <label>🏷️ Nama Aset (Publik)</label>
    <input type="text" id="assetName" placeholder="Misal: Istana Emas" value="RoyalAsset_{{timestamp}}" />

    <button class="btn" id="uploadBtn">⬆️ PUBLISH KE CREATOR STORE</button>

    <div id="log">⟳ Menunggu perintah, Yang Mulia...</div>
    <div class="footer">🛡️ Setelah berhasil, ID aset muncul → semua orang bisa pakai</div>
</div>
<script>
document.getElementById('uploadBtn').addEventListener('click', async function() {
    const log = document.getElementById('log');
    const cookie = document.getElementById('cookie').value.trim();
    const csrf = document.getElementById('csrf').value.trim();
    const fileInput = document.getElementById('fileInput');
    const name = document.getElementById('assetName').value || 'RoyalAsset_' + Date.now();

    if (!cookie) {
        log.innerHTML = '<span class="error">❌ Cookie wajib diisi, Yang Mulia!</span>';
        return;
    }
    if (!fileInput.files[0]) {
        log.innerHTML = '<span class="error">❌ Pilih file dulu!</span>';
        return;
    }

    const formData = new FormData();
    formData.append('cookie', cookie);
    formData.append('csrf', csrf);
    formData.append('file', fileInput.files[0]);
    formData.append('name', name);

    log.innerHTML = '<span class="warn">⏳ Mengirim ke server Railway...</span>';
    this.disabled = true;
    this.textContent = '⏳ PROSES...';

    try {
        const res = await fetch('/upload', { method: 'POST', body: formData });
        const data = await res.json();
        if (data.status === 'success') {
            log.innerHTML = `<span class="success">✅ BERHASIL!</span>\n` +
                            `<span class="info">📌 Asset ID: ${data.assetId}</span>\n` +
                            `<span class="success">🔗 https://www.roblox.com/library/${data.assetId}/</span>\n` +
                            `<span class="warn">🌍 Aset kini PUBLIK untuk semua pengguna!</span>`;
        } else {
            log.innerHTML = `<span class="error">❌ Gagal: ${data.message || 'Cek cookie atau format file'}</span>`;
        }
    } catch(e) {
        log.innerHTML = `<span class="error">❌ Error: ${e.message}</span>`;
    }
    this.disabled = false;
    this.textContent = '⬆️ PUBLISH KE CREATOR STORE';
});
</script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/upload', methods=['POST'])
def upload_to_roblox():
    try:
        cookie = request.form.get('cookie')
        csrf_manual = request.form.get('csrf', '').strip()
        name = request.form.get('name', 'RoyalAsset')
        file = request.files.get('file')
        
        if not cookie or not file:
            return jsonify({'status': 'error', 'message': 'Cookie atau file kosong'}), 400
        
        file_data = file.read()
        filename = file.filename

        # Buat session dengan header lengkap
        session = requests.Session()
        session.cookies.set('.ROBLOSECURITY', cookie, domain='.roblox.com')
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.roblox.com/',
            'Origin': 'https://www.roblox.com'
        })

        # Jika CSRF manual diberikan, langsung pakai
        csrf_token = csrf_manual if csrf_manual else None

        if not csrf_token:
            # Coba ambil CSRF dengan mengakses halaman upload
            try:
                csrf_resp = session.get('https://www.roblox.com/asset/upload', timeout=10)
                csrf_token = csrf_resp.headers.get('x-csrf-token')
                if not csrf_token:
                    # Coba dari cookie
                    csrf_token = session.cookies.get('XSRF-TOKEN')
            except:
                pass

        if not csrf_token:
            return jsonify({'status': 'error', 'message': 'CSRF token tidak ditemukan. Silakan isi manual di form atau periksa cookie.'}), 401

        # Kirim POST
        files = {'file': (filename, file_data, 'application/octet-stream')}
        data = {'name': name, 'assetType': 1}
        headers = {
            'X-CSRF-TOKEN': csrf_token,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.roblox.com/asset/upload',
            'Origin': 'https://www.roblox.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }

        upload_resp = session.post('https://www.roblox.com/asset/upload', data=data, files=files, headers=headers)
        
        # Ekstrak Asset ID
        asset_id = None
        if upload_resp.headers.get('Location'):
            match = re.search(r'/library/(\d+)/', upload_resp.headers.get('Location'))
            if match:
                asset_id = match.group(1)
        if not asset_id:
            match = re.search(r'assetId["\']?\s*[:=]\s*["\']?(\d+)', upload_resp.text)
            if match:
                asset_id = match.group(1)
        
        if asset_id:
            return jsonify({'status': 'success', 'assetId': asset_id})
        elif upload_resp.status_code in [200, 302]:
            return jsonify({'status': 'success', 'assetId': 'SUKSES (cek dashboard Creator Store)'})
        else:
            return jsonify({'status': 'error', 'message': f'HTTP {upload_resp.status_code}', 'detail': upload_resp.text[:200]})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
