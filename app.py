from flask import Flask, render_template_string, request, jsonify, redirect
import yt_dlp

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
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Cairo', sans-serif;
        }
        body {
            background-color: #0c0915;
            background-image: radial-gradient(circle at 10% 20%, rgba(90, 45, 130, 0.25) 0%, transparent 40%),
                              radial-gradient(circle at 90% 80%, rgba(40, 20, 70, 0.3) 0%, transparent 40%);
            color: #ffffff;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 40px 20px;
        }
        h1 {
            font-size: 2.2rem;
            font-weight: 800;
            margin-bottom: 30px;
            text-align: center;
            background: linear-gradient(45deg, #ffffff, #c4b5fd);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .container {
            width: 100%;
            max-width: 650px;
            background: rgba(22, 18, 35, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(16px);
            border-radius: 24px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
        }
        .input-group {
            position: relative;
            margin-bottom: 30px;
        }
        .input-group input {
            width: 100%;
            padding: 16px 20px;
            background: rgba(15, 12, 25, 0.8);
            border: 2px solid rgba(168, 85, 247, 0.4);
            border-radius: 16px;
            color: #fff;
            font-size: 1rem;
            outline: none;
            transition: all 0.3s ease;
            box-shadow: 0 0 15px rgba(168, 85, 247, 0.15);
        }
        .input-group input:focus {
            border-color: #a855f7;
            box-shadow: 0 0 25px rgba(168, 85, 247, 0.3);
        }
        .section-title {
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 15px;
            color: #e2e8f0;
            text-align: center;
        }
        .formats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 30px;
        }
        @media(max-width: 500px) {
            .formats-grid { grid-template-columns: 1fr; }
        }
        .format-card {
            background: rgba(30, 25, 48, 0.6);
            border: 2px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 18px 15px;
            cursor: pointer;
            display: flex;
            flex-direction: column;
            align-items: center;
            transition: all 0.25s ease;
            position: relative;
        }
        .format-card:hover {
            background: rgba(45, 35, 75, 0.7);
            border-color: rgba(168, 85, 247, 0.4);
        }
        .format-card.selected {
            border-color: #22c55e;
            background: rgba(34, 197, 94, 0.08);
            box-shadow: 0 0 15px rgba(34, 197, 94, 0.15);
        }
        .format-card input[type="radio"] {
            display: none;
        }
        .format-icon {
            font-size: 2rem;
            margin-bottom: 8px;
        }
        .format-name {
            font-weight: 700;
            font-size: 0.95rem;
            margin-bottom: 4px;
        }
        .format-desc {
            font-size: 0.75rem;
            color: #94a3b8;
        }
        .badge {
            position: absolute;
            top: 10px;
            left: 10px;
            font-size: 0.65rem;
            background: rgba(34, 197, 94, 0.2);
            color: #4ade80;
            padding: 2px 6px;
            border-radius: 6px;
        }
        .download-btn {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #9333ea, #c084fc);
            color: white;
            border: none;
            border-radius: 16px;
            font-size: 1.1rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 10px 25px rgba(147, 51, 234, 0.4);
        }
        .download-btn:hover {
            opacity: 0.95;
            transform: translateY(-2px);
            box-shadow: 0 15px 30px rgba(147, 51, 234, 0.6);
        }
        .loading {
            display: none;
            text-align: center;
            margin-top: 15px;
            color: #c084fc;
            font-weight: 600;
        }
        .footer {
            margin-top: 40px;
            font-size: 0.85rem;
            color: #64748b;
        }
    </style>
</head>
<body>

    <h1>تنزيل فيديوهات تيك توك بجميع الصيغ</h1>

    <div class="container">
        <form id="downloadForm" action="/download" method="POST">
            <div class="input-group">
                <input type="url" name="url" placeholder="ضع رابط فيديو تيك توك هنا..." required autocomplete="off">
            </div>

            <div class="section-title">اختر صيغة التنزيل</div>

            <div class="formats-grid">
                <label class="format-card selected" onclick="selectCard(this)">
                    <input type="radio" name="format" value="hd" checked>
                    <span class="badge">بدون علامة مائية</span>
                    <div class="format-icon">🎬</div>
                    <div class="format-name">MP4 - جودة عالية (HD)</div>
                    <div class="format-desc">أفضل جودة فيديو متوفرة</div>
                </label>

                <label class="format-card" onclick="selectCard(this)">
                    <input type="radio" name="format" value="sd">
                    <span class="badge">بدون علامة مائية</span>
                    <div class="format-icon">🎞️</div>
                    <div class="format-name">MP4 - جودة عادية (SD)</div>
                    <div class="format-desc">حجم خفيف وسريع</div>
                </label>

                <label class="format-card" onclick="selectCard(this)">
                    <input type="radio" name="format" value="mp3">
                    <span class="badge">صوت نقي</span>
                    <div class="format-icon">🎵</div>
                    <div class="format-name">MP3 - صوت فقط (Audio)</div>
                    <div class="format-desc">استخراج الصوت بصيغة MP3</div>
                </label>

                <label class="format-card" onclick="selectCard(this)">
                    <input type="radio" name="format" value="webm">
                    <span class="badge">متصفح</span>
                    <div class="format-icon">🌐</div>
                    <div class="format-name">WEBM - جودة ويب (WebM)</div>
                    <div class="format-desc">متوافقة مع متصفحات الويب</div>
                </label>
            </div>

            <button type="submit" class="download-btn">تنزيل الفيديو الآن</button>
            <div class="loading" id="loadingText">جاري معالجة الرابط وتحضير الملف...</div>
        </form>
    </div>

    <div class="footer">تصميم وتطوير خاص</div>

    <script>
        function selectCard(card) {
            document.querySelectorAll('.format-card').forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            card.querySelector('input').checked = true;
        }

        document.getElementById('downloadForm').addEventListener('submit', function() {
            document.getElementById('loadingText').style.display = 'block';
        });
    </script>
</body>
</html>
"""

@app.route('/')
chno = None
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    fmt = request.form.get('format', 'hd')

    if not url:
        return redirect('/')

    ydl_opts = {}
    if fmt == 'hd':
        ydl_opts = {'format': 'bestvideo+bestaudio/best', 'merge_output_format': 'mp4'}
    elif fmt == 'sd':
        ydl_opts = {'format': 'best[height<=480]', 'merge_output_format': 'mp4'}
    elif fmt == 'mp3':
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
    elif fmt == 'webm':
        ydl_opts = {'format': 'bestvideo[ext=webm]+bestaudio[ext=m4a]/best[ext=webm]/best'}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url') or info.get('requested_formats')[0].get('url')
            return redirect(video_url)
    except Exception as e:
        return f"<h3 style='color:white; text-align:center; margin-top:50px;'>عذراً، حدث خطأ أثناء جلب الرابط. تأكد من صحة الرابط وحاول مجدداً.</h3><br><div style='text-align:center;'><a href='/' style='color:#c084fc;'>العودة للصفحة الرئيسية</a></div>"

if __name__ == '__main__':
    app.run(debug=True)