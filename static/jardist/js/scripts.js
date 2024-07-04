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

$(document).ready(function () {
  $('.form-select').select2({
    theme: 'bootstrap-5',
    width: '100%',
  });
});

window.onscroll = function () {
  scrollFunction();
};
function scrollFunction() {
  if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
    document.getElementById('backToTopBtn').style.display = 'block';
  } else {
    document.getElementById('backToTopBtn').style.display = 'none';
  }
}

document.getElementById('backToTopBtn').addEventListener('click', function () {
  document.body.scrollTop = 0;
  document.documentElement.scrollTop = 0;
});
