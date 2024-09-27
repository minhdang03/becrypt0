document.addEventListener('DOMContentLoaded', function() {
    var quill = new Quill('#editor', {
        theme: 'bubble',
        modules: {
            toolbar: [
                ['bold', 'italic', 'underline', 'strike'],
                ['blockquote', 'code-block'],
                [{ 'header': 1 }, { 'header': 2 }],
                [{ 'list': 'ordered'}, { 'list': 'bullet' }],
                [{ 'script': 'sub'}, { 'script': 'super' }],
                [{ 'direction': 'rtl' }],
                [{ 'color': [] }, { 'background': [] }],
                [{ 'font': [] }],
                [{ 'align': [] }],
                ['clean'],
                ['link', 'image'],
                [{ 'size': ['small', false, 'large', 'huge'] }],
            ]
        }
    });

    // Phần còn lại của code giữ nguyên

    // Kiểm tra xem phần tử có tồn tại không
    var contentElement = document.getElementById('blog-content');
    if (contentElement) {
        var content = contentElement.value;
        var parser = new DOMParser();
        var doc = parser.parseFromString(content, 'text/html');
        var images = doc.querySelectorAll('img');
        images.forEach(img => {
            var src = img.getAttribute('src');
            if (src && src.startsWith('/blogs_user/edit/')) {
                // Loại bỏ phần tiền tố dư thừa
                src = src.replace('/blogs_user/edit/', '/');
            }
            // Thêm tiền tố từ tên miền đã định nghĩa trong .env
            if (src && !src.startsWith('http')) {
                src = `${location.origin}/${src}`;
            }
            img.setAttribute('src', src);
        });
        quill.clipboard.dangerouslyPasteHTML(doc.body.innerHTML);
    } else {
        console.warn('Không tìm thấy phần tử có id "blog-content"');
    }
});