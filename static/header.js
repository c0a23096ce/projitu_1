function startVoiceSearch() {
    if ('webkitSpeechRecognition' in window) {
        const recognition = new webkitSpeechRecognition();
        recognition.lang = 'ja-JP';
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onresult = function(event) {
            const result = event.results[0][0].transcript;
            document.querySelector('.search-input').value = result;
            document.querySelector('.search-form').submit();
        };

        recognition.onerror = function(event) {
            console.error('音声認識エラー:', event.error);
        };

        recognition.start();
    } else {
        alert('お使いのブラウザは音声認識に対応していません');
    }
}

document.addEventListener('DOMContentLoaded', function() {
  const btn = document.getElementById('adminMenuBtn');
  const dropdown = btn.parentElement;

  btn.addEventListener('click', function(e) {
    e.stopPropagation();
    dropdown.classList.toggle('show');
  });

  // メニュー外クリックで閉じる
  document.addEventListener('click', function(e) {
    dropdown.classList.remove('show');
  });
});