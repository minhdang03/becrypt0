// Khởi tạo Quill editor với Bubble theme
const quill = new Quill('#editor', {
    theme: 'bubble',
    placeholder: 'Viết nội dung bài viết ở đây...',
    modules: {
      toolbar: false  // Không sử dụng toolbar mặc định
    }
  });
  
  // Xây dựng một module tùy chỉnh để xử lý tooltip
  class CustomTooltipModule {
    constructor(quill, options) {
      this.quill = quill;
      this.container = document.createElement('div');
      this.container.classList.add('custom-tooltip');
      this.container.style.display = 'none';
      this.container.innerHTML = `
        <button class="ql-bold">Bold</button>
        <button class="ql-italic">Italic</button>
        <button class="ql-underline">Underline</button>
      `;
      document.body.appendChild(this.container);
  
      this.quill.on('selection-change', (range) => {
        if (range) {
          const bounds = this.quill.getBounds(range.index);
          this.showTooltip(bounds);
        } else {
          this.hideTooltip();
        }
      });
  
      // Bắt sự kiện từ các nút trong tooltip
      this.container.querySelector('.ql-bold').addEventListener('click', () => {
        this.quill.format('bold', true);
      });
      this.container.querySelector('.ql-italic').addEventListener('click', () => {
        this.quill.format('italic', true);
      });
      this.container.querySelector('.ql-underline').addEventListener('click', () => {
        this.quill.format('underline', true);
      });
    }
  
    showTooltip(bounds) {
      this.container.style.top = `${bounds.top + window.scrollY}px`;
      this.container.style.left = `${bounds.left + window.scrollX}px`;
      this.container.style.display = 'block';
    }
  
    hideTooltip() {
      this.container.style.display = 'none';
    }
  }
  
  // Đăng ký module tùy chỉnh
  Quill.register('modules/customTooltip', CustomTooltipModule);
  
  // Khởi tạo module tooltip khi nhấn vào nút toolbar-button
  document.getElementById('toolbar-button').addEventListener('click', () => {
    quill.getModule('customTooltip').showTooltip({ top: 50, left: 100 });
  });
  