document.addEventListener('DOMContentLoaded', function() {
    var isFullscreen = false;
    var editorContainer = document.querySelector('.container');
    var fullscreenButton = document.createElement('button');
    fullscreenButton.innerHTML = '<i class="fas fa-expand"></i> Fullscreen';
    fullscreenButton.className = 'bg-gray-500 text-white py-2 px-4 rounded-lg hover:bg-gray-600 transition-colors';
    fullscreenButton.style.position = 'absolute';
    fullscreenButton.style.top = '10px';
    fullscreenButton.style.right = '10px';
    document.body.appendChild(fullscreenButton);

    fullscreenButton.addEventListener('click', function() {
        if (isFullscreen) {
            editorContainer.classList.remove('fullscreen');
            fullscreenButton.innerHTML = '<i class="fas fa-expand"></i> Fullscreen';
        } else {
            editorContainer.classList.add('fullscreen');
            fullscreenButton.innerHTML = '<i class="fas fa-compress"></i> Exit Fullscreen';
        }
        isFullscreen = !isFullscreen;
    });
});