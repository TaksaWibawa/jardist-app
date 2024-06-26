document.addEventListener('DOMContentLoaded', (event) => {
  let toastElList = [].slice.call(document.querySelectorAll('.toast'));
  let toastList = toastElList.map(function (toastEl) {
    return new bootstrap.Toast(toastEl, { autohide: true });
  });
  toastList.forEach((toast) => toast.show());

  let menuItems = document.querySelectorAll('.menu');
  menuItems.forEach((menuItem) => {
    let submenuList = menuItem.querySelector('.submenu-list');
    submenuList.style.display = 'block';
  });
});
