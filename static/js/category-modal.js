
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('blog-form');
    const categoryModal = document.getElementById('categoryModal');
    const cancelButton = document.getElementById('cancelButton');
    const ConfirmButton = document.getElementById('ConfirmButton');
    const categoryForm = document.getElementById('categoryForm');

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        categoryModal.classList.remove('hidden');
    });

    cancelButton.addEventListener('click', function() {
        categoryModal.classList.add('hidden');
    });

    form.addEventListener('submit', function(event) {
        contentField.value = quill.root.innerHTML;
    });

});
