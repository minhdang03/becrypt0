document.addEventListener('DOMContentLoaded', function() {
    const quill = Quill.find(document.querySelector('#editor'));

    quill.getModule('toolbar').addHandler('image', function() {
        document.getElementById('image-upload').click();
    });

    document.getElementById('image-upload').addEventListener('change', function() {
        const files = this.files;
        if (files.length > 0) {
            const formData = new FormData();
            for (let i = 0; i < files.length; i++) {
                formData.append('images', files[i]);
            }

            fetch('/blogs_user/user_upload_image', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.urls) {
                    data.urls.forEach(url => {
                        const range = quill.getSelection();
                        quill.insertEmbed(range.index, 'image', url);
                        const img = quill.container.querySelector(`img[src="${url}"]`);
                        if (img) {
                            img.style.maxWidth = '50%';
                            img.style.height = 'auto';
                        }
                    });
                } else {
                    console.error('Failed to upload image:', data.error);
                }
            })
            .catch(error => console.error('Error:', error));
        }
    });

    quill.clipboard.addMatcher(Node.ELEMENT_NODE, function(node, delta) {
        if (node.tagName === 'IMG') {
            delta.ops = [{
                insert: {
                    image: node.src
                }
            }];
        }
        return delta;
    });
});