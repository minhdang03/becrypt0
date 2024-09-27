document.addEventListener('DOMContentLoaded', function() {
    const quill = new Quill('#editor', {
        theme: 'bubble',
        placeholder: 'Viết nội dung bài viết ở đây...',
        modules: {
            toolbar: [
                [{ 'header': ['1', '2', '3', '4', '5', '6', false] }],  // Chọn tiêu đề
                ['bold', 'italic'],
                [{ 'list': 'ordered'}, { 'list': 'bullet' }],     // Danh sách thứ tự và không thứ tự

            ]
        }
    });
    
//                 ['image', 'clean']
    // Lấy form và trường content
    const blogForm = document.getElementById('blog-form');
    const categoryForm = document.getElementById('categoryForm');
    const contentField = document.getElementById('content');
    const categoryModal = document.getElementById('categoryModal');
    const cancelButton = document.getElementById('cancelButton');
    const submitButton = document.getElementById('submitButton');
    const confirmButton = document.getElementById('ConfirmButton');

    // Hiển thị modal khi nhấn nút "Confirm"
    confirmButton.addEventListener('click', function() {
        categoryModal.classList.remove('hidden2');
    });

    // Hủy modal
    cancelButton.addEventListener('click', function() {
        categoryModal.classList.add('hidden2');
    });

    // Xác nhận danh mục và gửi form
    submitButton.addEventListener('click', function(event) {
        event.preventDefault();
        categoryModal.classList.add('hidden2');
        contentField.value = quill.root.innerHTML;

        // Tạo một form data mới để gửi
        const formData = new FormData(blogForm);

        // Thêm dữ liệu từ categoryForm vào formData
        new FormData(categoryForm).forEach((value, key) => {
            formData.append(key, value);
        });

        // Tạo một form tạm thời để gửi dữ liệu
        const tempForm = document.createElement('form');
        tempForm.method = 'POST';
        tempForm.action = blogForm.action;

        // Thêm các trường từ formData vào form tạm thời
        formData.forEach((value, key) => {
            const input = document.createElement('input');
            input.type = 'hidden2';
            input.name = key;
            input.value = value;
            tempForm.appendChild(input);
        });

        // Thêm form tạm thời vào body và gửi form
        document.body.appendChild(tempForm);
        tempForm.submit();
    });


    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('fileElem');

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    // Highlight drop area when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.add('highlight'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.remove('highlight'), false);
    });

    // Handle dropped files
    dropArea.addEventListener('drop', handleDrop, false);

    // Handle file selection via click
    dropArea.addEventListener('click', () => fileInput.click(), false);
    fileInput.addEventListener('change', handleFiles, false);

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles({ target: { files } });
    }

    function handleFiles(e) {
        const files = e.target.files;
        if (files.length) {
            const file = files[0];
            const formData = new FormData();
            formData.append('thumbnail_url', file);

            // Upload the file via AJAX
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/blogs_user/upload-thumbnailurl-temp', true);
            xhr.onload = function() {
                if (xhr.status === 200) {
                    const response = JSON.parse(xhr.responseText);
                    console.log('File uploaded successfully');
                    console.log('Filename:', response.filename);
                    // Display the image from the temp directory
                    const tempImageUrl = `/static/img/blogs/temp/${response.filename}`;
                    dropArea.innerHTML = `<img src="${tempImageUrl}" alt="Preview" class="max-h-full max-w-full">`;
                    // Store the full URL in a hidden input field
                    const thumbnailUrlInput = document.getElementById('thumbnail_url');
                    if (thumbnailUrlInput) {
                        thumbnailUrlInput.value = tempImageUrl;
                        console.log('Thumbnail URL updated:', thumbnailUrlInput.value);
                    } else {
                        console.error('Thumbnail URL input field not found');
                    }
                } else {
                    console.error('File upload failed');
                    alert('Không thể tải lên hình ảnh. Vui lòng thử lại.');
                }
            };
            xhr.onerror = function() {
                console.error('Network error occurred');
                alert('Đã xảy ra lỗi mạng. Vui lòng kiểm tra kết nối và thử lại.');
            };
            xhr.send(formData);
        }
    }
});