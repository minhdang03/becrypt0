document.addEventListener('DOMContentLoaded', function() {
    const toolbarButton = document.getElementById('toolbar-button');

    // Sử dụng instance Quill đã được tạo từ blogs_user_forms.js
    const quill = window.quill;

    quill.on('selection-change', function(range, oldRange, source) {
        if (range) {
            if (range.length > 0) {
                const bounds = quill.getBounds(range.index, range.length);
                positionToolbarButton(bounds);
            } else {
                hideToolbarButton();
            }
        } else {
            hideToolbarButton();
        }
    });

    function positionToolbarButton(bounds) {
        const editorRect = quill.container.getBoundingClientRect();
        const buttonRect = toolbarButton.getBoundingClientRect();

        const left = editorRect.left + bounds.left + (bounds.width / 2) - (buttonRect.width / 2);
        const top = editorRect.top + bounds.top - buttonRect.height - 5;

        toolbarButton.style.left = `${left}px`;
        toolbarButton.style.top = `${top}px`;
        toolbarButton.style.display = 'block';
    }

    function hideToolbarButton() {
        toolbarButton.style.display = 'none';
    }

    // Tạo tooltip bằng Tippy.js
    tippy('#toolbar-button', {
        content: `<div class="toolbar-options">
                    <button class="ql-bold">B</button>
                    <button class="ql-italic">I</button>
                    <button class="ql-underline">U</button>
                  </div>`,
        allowHTML: true,
        trigger: 'click',  // Hiển thị khi bấm vào
        interactive: true, // Cho phép tương tác với tooltip
        onShow(instance) {
            console.log('Tooltip hiển thị');
        },
        onHide(instance) {
            console.log('Tooltip bị ẩn');
        }
    });

    // Kết nối các nút định dạng với Quill
    document.addEventListener('click', function(event) {
        if (event.target.matches('.ql-bold')) {
            quill.format('bold', true);
        }
        if (event.target.matches('.ql-italic')) {
            quill.format('italic', true);
        }
        if (event.target.matches('.ql-underline')) {
            quill.format('underline', true);
        }
    });
});