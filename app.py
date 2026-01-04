from flask import Flask, render_template, request, send_file
import zipfile
import io

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/seal', methods=['POST'])
def seal_envelope():
    # アップロードされたファイルを取得
    uploaded_files = request.files.getlist("files")
    
    if not uploaded_files:
        return "No files uploaded", 400

    # メモリ上でZIPファイルを作成
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in uploaded_files:
            # ファイルをZIPに追加
            zf.writestr(file.filename, file.read())
    
    memory_file.seek(0)
    
    # "pochibukuro.zip" としてダウンロードさせる
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name='pochibukuro.zip'
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')