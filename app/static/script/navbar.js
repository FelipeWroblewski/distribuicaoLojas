// ARQUIVO: navbar.js

const sideBar = document.getElementById('sidebar');
const toogleBtn = document.getElementById('toogleSidebar');
const content = document.getElementById("content");

// O Dark Mode já foi inicializado pelo homepage.js.

document.addEventListener('DOMContentLoaded', function() {
    const darkBtn = document.querySelector('#dark-mode'); 

    // Lógica do Dark Mode
    if (darkBtn) {
        darkBtn.addEventListener('click', function() {
            // Usa a variável global 'htmlElement' (declarada em homepage.js)
            htmlElement.classList.toggle('dark');

            const isDark = htmlElement.classList.contains('dark');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');

            // Chama a função global 'aplicarTemaHighcharts' (declarada em homepage.js)
            if (typeof aplicarTemaHighcharts === 'function') {
                aplicarTemaHighcharts(isDark);
            }
        });
    }

    // Lógica de alternância da Navbar
    toogleBtn.addEventListener("click", () => {
        if (sideBar.classList.contains("w-0")) {
            sideBar.classList.replace("w-0", "w-96");
            content.classList.add("ml-64"); 
        } else {
            sideBar.classList.replace("w-96", "w-0");
            content.classList.remove("ml-96");
        }
    });
});


function toogleSidebar() {
    const isOpen = !sidebar.classList.contains('-translate-x-full');
    if (isOpen) {
        sidebar.classList.add('-translate-x-full');
    } else {
        sidebar.classList.remove('-translate-x-full');
    }
}

toogleBtn.addEventListener('click', toogleSidebar);