@app.route('/upload', methods=['POST'])
def upload_to_roblox():
    try:
        cookie = request.form.get('cookie')
        name = request.form.get('name', 'RoyalAsset')
        file = request.files.get('file')
        
        if not cookie or not file:
            return jsonify({'status': 'error', 'message': 'Cookie atau file kosong'}), 400
        
        file_data = file.read()
        filename = file.filename

        # Buat session dengan header browser
        session = requests.Session()
        session.cookies.set('.ROBLOSECURITY', cookie, domain='.roblox.com')
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://www.roblox.com/',
            'Origin': 'https://www.roblox.com'
        })

        # Ambil CSRF token dengan GET ke halaman upload
        csrf_resp = session.get('https://www.roblox.com/asset/upload')
        csrf_token = csrf_resp.headers.get('x-csrf-token')
        
        # Jika tidak dapat token, coba ambil dari cookie atau header lain
        if not csrf_token:
            # Coba ambil dari cookie 'XSRF-TOKEN'
            csrf_token = session.cookies.get('XSRF-TOKEN')
        
        if not csrf_token:
            return jsonify({'status': 'error', 'message': 'CSRF token tidak ditemukan. Cookie mungkin kadaluarsa.'}), 401

        # Kirim POST dengan CSRF token
        files = {'file': (filename, file_data, 'application/octet-stream')}
        data = {'name': name, 'assetType': 1}
        headers = {
            'X-CSRF-TOKEN': csrf_token,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.roblox.com/asset/upload',
            'Origin': 'https://www.roblox.com'
        }

        upload_resp = session.post('https://www.roblox.com/asset/upload', data=data, files=files, headers=headers)
        
        # Ekstrak Asset ID
        asset_id = None
        if upload_resp.headers.get('Location'):
            match = re.search(r'/library/(\d+)/', upload_resp.headers.get('Location'))
            if match: asset_id = match.group(1)
        if not asset_id:
            match = re.search(r'assetId["\']?\s*[:=]\s*["\']?(\d+)', upload_resp.text)
            if match: asset_id = match.group(1)
        
        if asset_id:
            return jsonify({'status': 'success', 'assetId': asset_id})
        elif upload_resp.status_code in [200, 302]:
            return jsonify({'status': 'success', 'assetId': 'SUKSES (cek dashboard Creator Store)'})
        else:
            return jsonify({'status': 'error', 'message': f'HTTP {upload_resp.status_code}', 'detail': upload_resp.text[:200]})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
