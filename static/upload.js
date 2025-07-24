document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.querySelector('.file-input');
    const uploadArea = document.querySelector('.file-upload-area');
    const uploadText = document.querySelector('.file-upload-text');

    // ファイル名表示用要素を追加
    let fileNameElem = document.createElement('div');
    fileNameElem.className = 'selected-file';
    uploadArea.appendChild(fileNameElem);

    // ファイル選択時
    fileInput.addEventListener('change', function(e) {
        if (fileInput.files.length > 0) {
            fileNameElem.textContent = "選択ファイル: " + fileInput.files[0].name;
            uploadArea.classList.add('file-selected');
        } else {
            fileNameElem.textContent = "";
            uploadArea.classList.remove('file-selected');
        }
    });

    // ドラッグ＆ドロップ対応
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });
    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            fileInput.files = e.dataTransfer.files;
            fileInput.dispatchEvent(new Event('change'));
        }
    });
});