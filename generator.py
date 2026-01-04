import base64
import os
import sys

def get_template(data_type, content, filename=""):
    """
    Returns the complete HTML string with embedded content.
    data_type: 'file' or 'url'
    content: Base64 string (if file) or URL string
    filename: Original filename (if file)
    """
    
    # CSS for the envelope
    css = """
    body {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        background-color: #f8f8f8;
        font-family: 'Yu Mincho', 'Hiragino Mincho ProN', serif;
        margin: 0;
        overflow: hidden;
    }
    .container { text-align: center; perspective: 1000px; }
    h1 { color: #333; margin-bottom: 20px; font-weight: normal; letter-spacing: 2px; }
    
    .envelope {
        width: 220px;
        height: 340px;
        background-color: #fbfaf5;
        position: relative;
        margin: 0 auto;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        cursor: pointer;
        transition: transform 0.3s;
        border-radius: 2px;
    }
    .envelope:hover { transform: translateY(-5px); }
    
    /* Decoration: Red borders on sides to look like Japanese envelope folded paper */
    .envelope::after {
        content: ''; position: absolute; top: 0; bottom: 0; left: 0; width: 4px;
        background: rgba(0,0,0,0.02);
    }
    
    /* Flap (Lid) */
    .flap {
        position: absolute;
        top: 0; left: 0;
        width: 0; height: 0;
        border-left: 110px solid transparent;
        border-right: 110px solid transparent;
        border-top: 90px solid #fbfaf5; /* Same color as body */
        transform-origin: top;
        transition: transform 0.8s cubic-bezier(0.4, 0, 0.2, 1);
        z-index: 10;
        filter: drop-shadow(0 2px 3px rgba(0,0,0,0.1));
        transform: rotateX(0deg); /* Initially closed */
    }
    
    /* Open state */
    .envelope.open .flap {
        transform: rotateX(180deg);
        z-index: 1; /* Move behind body when open */
    }
    
    /* Pocket / Message area Inside */
    .content-area {
        position: absolute;
        top: 20px; left: 10px; right: 10px; bottom: 10px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 5;
        opacity: 0;
        transition: opacity 0.5s 0.5s; /* Fade in after flap opens */
    }
    .envelope.open .content-area { opacity: 1; }
    
    .message { font-size: 1.2rem; color: #d93d3d; margin-bottom: 20px; }
    
    button.download-btn {
        background-color: #d93d3d;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 20px;
        cursor: pointer;
        font-family: inherit;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        transition: background 0.3s;
    }
    button.download-btn:hover { background-color: #b52b2b; }
    
    /* Mizuhiki (The knot) - sits on top of everything when closed */
    .mizuhiki {
        position: absolute;
        top: 35%; left: 0; width: 100%; height: 60px;
        pointer-events: none;
        z-index: 15;
        transition: opacity 0.3s;
    }
    .envelope.open .mizuhiki { opacity: 0; } /* Hide when opened */
    
    .mizuhiki-line {
        position: absolute; top: 50%; left: 0; right: 0; height: 2px;
        background: linear-gradient(to bottom, #d93d3d 50%, #fff 50%);
    }
    .not-mizu { /* Knot */
        position: absolute; top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        width: 40px; height: 20px;
    }
    .not-mizu::before, .not-mizu::after {
        content: ''; position: absolute; top: -10px;
        width: 20px; height: 20px;
        border: 3px solid #d93d3d; border-radius: 50%;
    }
    .not-mizu::before { left: 0; transform: rotate(-45deg); border-right-color: transparent; border-bottom-color: transparent; }
    .not-mizu::after { right: 0; transform: rotate(45deg); border-left-color: transparent; border-bottom-color: transparent; }
    
    /* Instruction text under envelope */
    .hint { margin-top: 30px; color: #888; font-size: 0.9rem; }
    """

    # JavaScript logic
    js_data_type = f"'{data_type}'"
    js_content = f"'{content}'"
    js_filename = f"'{filename}'"
    
    script = f"""
    const envelope = document.querySelector('.envelope');
    const type = {js_data_type};
    const content = {js_content};
    const filename = {js_filename};
    
    let isOpened = false;
    
    envelope.addEventListener('click', () => {{
        if (isOpened) return;
        isOpened = true;
        
        // Open animation
        envelope.classList.add('open');
        document.getElementById('hint-text').innerText = "中身を確認しています...";
        
        // Wait for animation to finish then act
        setTimeout(() => {{
            if (type === 'url') {{
                document.getElementById('msg').innerText = "右のボタンから\\n移動してください";
                const btn = document.getElementById('action-btn');
                btn.innerText = "ページを開く";
                btn.onclick = (e) => {{
                    e.stopPropagation();
                    window.open(content, '_blank');
                }};
            }} else {{
                document.getElementById('msg').innerText = "ダウンロード\\n準備完了";
                const btn = document.getElementById('action-btn');
                btn.innerText = "受け取る";
                btn.onclick = (e) => {{
                    e.stopPropagation();
                    downloadFile(content, filename);
                }};
                
                // Auto trigger download attempt? Maybe too aggressive. Let user click.
            }}
        }}, 800);
    }});
    
    function downloadFile(base64Data, fileName) {{
        const byteCharacters = atob(base64Data);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {{
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }}
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], {{type: "application/octet-stream"}});
        
        const link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = fileName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }}
    """

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>お届けものです</title>
<style>{css}</style>
</head>
<body>

<div class="container">
    <h1>心ばかりの品です</h1>
    
    <div class="envelope">
        <div class="flap"></div>
        <div class="mizuhiki">
            <div class="mizuhiki-line"></div>
            <div class="not-mizu"></div>
        </div>
        
        <!-- Content revealed after opening -->
        <div class="content-area">
            <div class="message" id="msg"></div>
            <button id="action-btn" class="download-btn">...</button>
        </div>
    </div>
    
    <p class="hint" id="hint-text">ポチ袋をクリックして開けてください</p>
</div>

<script>
{script}
</script>
</body>
</html>
    """
    return html

def main():
    print("=== デジタルポチ袋ジェネレーター ===")
    target = input("埋め込みたいファイルパス または URLを入力してください: ").strip()
    
    # Check if URL
    if target.startswith("http://") or target.startswith("https://"):
        print(f"URLとして認識しました: {target}")
        html_content = get_template('url', target)
    else:
        # Assume File
        if not os.path.exists(target):
            # Remove quotes if user dragged and dropped
            target = target.replace('"', '').replace("'", "")
        
        if not os.path.exists(target):
            print("エラー: ファイルが見つかりません。")
            return
            
        print(f"ファイルを読み込んでいます: {target}")
        filename = os.path.basename(target)
        
        try:
            with open(target, "rb") as f:
                data = f.read()
                b64_data = base64.b64encode(data).decode('utf-8')
                html_content = get_template('file', b64_data, filename)
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            return

    output_path = "otoshidama.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"\n生成完了！ -> {os.path.abspath(output_path)}")
    print("このHTMLファイルをブラウザで開いて確認してください。")

if __name__ == "__main__":
    main()
