from flask import Flask, render_template_string, request
import requests

app = Flask(__name__)

# واجهة الموقع
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مُنزل فيديوهات تيك توك</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #121212; color: white; text-align: center; padding: 50px; }
        input { width: 60%; padding: 12px; border-radius: 8px; border: none; font-size: 16px; margin-bottom: 10px; }
        button { padding: 12px 25px; background-color: #fe2c55; color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 16px; }
        .result { margin-top: 30px; }
        a { color: #25f4ee; text-decoration: none; font-weight: bold; font-size: 18px; }
    </style>
</head>
<body>
    <h2>تنزيل فيديو تيك توك بدون علامة مائية</h2>
    <form method="POST">
        <input type="text" name="url" placeholder="ضع رابط فيديو تيك توك هنا..." required>
        <br>
        <button type="submit">جلب رابط التحميل</button>
    </form>

    {% if download_url %}
        <div class="result">
            <p>تم تجهيز الفيديو بنجاح!</p>
            <a href="{{ download_url }}" target="_blank">اضغط هنا لتحميل الفيديو مباشرة</a>
        </div>
    {% endif %}

    {% if error %}
        <div class="result" style="color: red;">
            <p>{{ error }}</p>
        </div>
    {% endif %}
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    download_url = None
    error = None
    
    if request.method == 'POST':
        video_url = request.form.get('url')
        
        # استدعاء API مجاني لتنزيل الفيديو
        api_url = f"https://tikwm.com/api/?url={video_url}"
        
        try:
            response = requests.get(api_url).json()
            if response.get('code') == 0:
                download_url = response['data']['play']
            else:
                error = "عذراً، لم نتمكن من جلب الفيديو. تأكد من صحة الرابط."
        except Exception:
            error = "حدث خطأ أثناء الاتصال بالسيرفر."

    return render_template_string(HTML_TEMPLATE, download_url=download_url, error=error)

if __name__ == '__main__':
    app.run(debug=True)