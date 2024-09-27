document.addEventListener('DOMContentLoaded', function() {
    var markdownButton = document.createElement('button');
    markdownButton.innerHTML = '<i class="fas fa-code"></i> Markdown';
    markdownButton.className = 'bg-gray-500 text-white py-2 px-4 rounded-lg hover:bg-gray-600 transition-colors';
    markdownButton.style.position = 'absolute';
    markdownButton.style.top = '10px';
    markdownButton.style.right = '150px';
    document.body.appendChild(markdownButton);

    markdownButton.addEventListener('click', function() {
        var markdownContent = prompt('Enter Markdown content:');
        if (markdownContent) {
            var htmlContent = marked(markdownContent);
            var quill = Quill.find(document.querySelector('#editor'));
            quill.clipboard.dangerouslyPasteHTML(htmlContent);
        }
    });
});