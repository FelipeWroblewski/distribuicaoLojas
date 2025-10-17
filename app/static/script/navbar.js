const sideBar = document.getElementById('sidebar');
const toogleBtn = document.getElementById('toogleSidebar');
const content = document.getElementById("content");

const btn = document.querySelector('#dark-mode');
const html = document.querySelector('html');

btn.addEventListener('click', function() {
    html.classList.toggle('dark');
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

toogleBtn.addEventListener("click", () => {
  if (sideBar.classList.contains("w-0")) {
    sideBar.classList.replace("w-0", "w-96");
    content.classList.add("ml-64"); // empurra o conteúdo
  } else {
    sideBar.classList.replace("w-96", "w-0");
    content.classList.remove("ml-96");
  }
});
