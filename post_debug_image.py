import requests
fpath = 'static/uploads/debug/IMG-20251217-WA0007.jpg'
url = 'http://127.0.0.1:5000/api/predict'
with open(fpath, 'rb') as f:
    r = requests.post(url, files={'file': ('IMG.jpg', f, 'image/jpeg')}, timeout=10)
print('status', r.status_code)
print(r.text)
