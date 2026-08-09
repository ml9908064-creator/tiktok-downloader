from flask import Flask, render_template_string, request
import requests

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تنزيل فيديوهات تيك توك بجميع الصيغ</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Cairo', sans-serif; }
        body {
            background-color: #0c0915;
            background-image: radial-gradient(circle at 10% 20%, rgba(90, 45, 130, 0.25) 0%, transparent 40%),
                              radial-gradient(circle at 90% 80%, rgba(40, 20, 70, 0.3) 0%, transparent 40%);
            color: #ffffff; min-height: 100vh; display: flex; flex-direction: column; align-items: center; padding: 40px 20px;
        }
        h1 { font-size: 2rem; font-weight: 800; margin-bottom: 25px; text-align: center; background: linear-gradient(45deg, #ffffff, #c4b5fd); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .container { width: 100%; max-width: 600px; background: rgba(22, 18, 35, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); backdrop-filter: blur(16px); border-radius: 24px; padding: 30px; box-shadow: 0 20px 40px rgba(0,0,0,0.5); }
        .input-group input { width: 100%; padding: 16px; background: rgba(15, 12, 25, 0.8); border: 2px solid rgba(168, 85, 247, 0.4); border-radius: 16px; color: #fff; font-size: 1rem; outline: none; margin-bottom: 20px; }
        .formats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 25px; }
        @media(max-width: 500px) { .formats-grid { grid-template-columns: 1fr; } }
        .format-card { background: rgba(30, 25, 48, 0.6); border: 2px solid rgba(255, 255, 255, 0.05); border-radius: 16px; padding: 15px; cursor: pointer; display: flex; flex-direction: column; align-items: center; text-align: center; }
        .format-card.selected { border-color: #22c55e; background: rgba(34, 197, 94, 0.1); }
        .format-card input { display: none; }
        .download-btn { width: 100%; padding: 16px; background: linear-gradient(135deg, #9333ea, #c084fc); color: white; border: none; border-radius: 16px; font-size: 1.1rem; font-weight: 700; cursor: pointer; text-align: center; display: block; text-decoration: none; }
        .result-box { margin-top: 25px; text-align: center; background: rgba(30, 25, 48, 0.8); padding: 20px; border-radius: 16px; border: 1px solid #22c55e; }
        .error-box { margin-top: 25px; text-align: center; background: rgba(50, 20, 20, 0.8); padding: 15px; border-radius: 16px; border: 1px solid #ef4444; color: #f87171; }
    </style>
</head>
<body>
    <h1>تنزيل فيديوهات تيك توك بجميع الصيغ</h1>
    <div class="container">
        <form action="/download" method="POST">
            <div class="input-group">
                <input type="url" name="url" placeholder="ضع رابط فيديو تيك توك هنا..." value="{{ original_url or '' }}" required>
            </div>
            <div class="formats-grid">
                <label class="format-card {{ 'selected' if fmt != 'mp3' else '' }}" onclick="selectCard(this)">
                    <input type="radio" name="format" value="hd" {{ 'checked' if fmt != 'mp3' else '' }}>
                    <div style="font-size: 1.5rem;">🎬</div>
                    <div style="font-weight:700;">MP4 - فيديو بدون علامة مائية</div>
                </label>
                <label class="format-card {{ 'selected' if fmt == 'mp3' else '' }}" onclick="selectCard(this)">
                    <input type="radio" name="format" value="mp3" {{ 'checked' if fmt == 'mp3' else '' }}>
                    <div style="font-size: 1.5rem;">🎵</div>
                    <div style="font-weight:700;">MP3 - صوت فقط</div>
                </label>
            </div>
            <button type="submit" class="download-btn">جلب رابط التحميل</button>
        </form>

        {% if download_url %}
        <div class="result-box">
            <p style="margin-bottom: 15px; font-weight:700; color:#4ade80;">✅ تم تجهيز الملف بنجاح!</p>
            <a href="{{ download_url }}" target="_blank" download class="download-btn" style="background: #22c55e;">
                اضغط هنا لتنزيل {{ 'الصوت (MP3)' if fmt == 'mp3' else 'الفيديو (MP4)' }}
            </a>
        </div>
        {% endif %}

        {% if error %}
        <div class="error-box">
            {{ error }}
        </div>
        {% endif %}
    </div>

    <script>
        function selectCard(card) {
            document.querySelectorAll('.format-card').forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            card.querySelector('input').checked = true;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, download_url=None, error=None, fmt='hd', original_url='')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url', '').strip()
    fmt = request.form.get('format', 'hd')

    if not url:
        return render_template_string(HTML_TEMPLATE, download_url=None, error="يرجى إدخال رابط صحيح.", fmt=fmt, original_url=url)

    try:
        # استخدام API سريع وموثوق
        api_endpoint = f"https://www.tikwm.com/api/?url={url}"
        response = requests.get(api_endpoint, timeout=10).json()

        if response.get('code') == 0 and 'data' in response:
            data = response['data']
            if fmt == 'mp3':
                file_url = data.get('music')
            else:
                file_url = data.get('play') or data.get('wmplay')

            if file_url:
                # التأكد من صحة الرابط
                if not file_url.startswith('http'):
                    file_url = 'https://www.tikwm.com' + file_url
                return render_template_string(HTML_TEMPLATE, download_url=file_url, error=None, fmt=fmt, original_url=url)

        return render_template_string(HTML_TEMPLATE, download_url=None, error="لم نتمكن من جلب هذا الفيديو. تأكد من أن الحساب غير خاص وأن الرابط صحيح.", fmt=fmt, original_url=url)

    except Exception as e:
        return render_template_string(HTML_TEMPLATE, download_url=None, error="حدث خطأ في الاتصال بالسيرفر. حاول مرة أخرى.", fmt=fmt, original_url=url)

if __name__ == '__main__':
    app.run()
