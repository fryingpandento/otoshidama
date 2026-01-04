const envelope = document.getElementById('pochi-zone');
const statusDiv = document.getElementById('status');

// ドラッグ中
envelope.addEventListener('dragover', (e) => {
    e.preventDefault();
    envelope.classList.add('dragover');
});

// ドラッグが外れた時
envelope.addEventListener('dragleave', () => {
    envelope.classList.remove('dragover');
});

// ドロップされた時
envelope.addEventListener('drop', (e) => {
    e.preventDefault();
    envelope.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFiles(files);
    }
});

function handleFiles(files) {
    statusDiv.textContent = "袋詰め中...";

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }

    // Pythonバックエンドへ送信
    fetch('/seal', {
        method: 'POST',
        body: formData
    })
        .then(response => {
            if (response.ok) {
                return response.blob();
            }
            throw new Error('Network response was not ok.');
        })
        .then(blob => {
            // 1. 封を閉じるアニメーション
            envelope.classList.add('sealed');
            document.querySelector('.message').textContent = "準備完了！";

            // 2. 少し待ってからダウンロード開始
            setTimeout(() => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = 'otoshidama.zip'; // ダウンロードファイル名
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                statusDiv.textContent = "ダウンロードしました";
            }, 1000); // 1秒後にダウンロード
        })
        .catch(error => {
            console.error('Error:', error);
            statusDiv.textContent = "エラーが発生しました";
        });
}