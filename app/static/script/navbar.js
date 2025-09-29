const toggleButtons = document.querySelectorAll('.open-modal');

toggleButtons.forEach(button => {
    button.addEventListener('click', () => {
        const modalId = button.getAttribute('data-modal');
        const modal = document.getElementById(modalId);

        if (modal.open) {
           return modal.close(); 
        } 
        return modal.show(); 
    });
});
