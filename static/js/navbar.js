document.addEventListener('DOMContentLoaded', function() {
    const userMenuButton = document.getElementById('user-menu-button');
    const userDropdown = document.getElementById('user-dropdown');
    const navbarToggle = document.querySelector('[data-collapse-toggle="navbar-user"]');
    const navbarMenu = document.getElementById('navbar-user');

    userMenuButton?.addEventListener('click', function() {
      userDropdown?.classList.toggle('hidden');
    });

    navbarToggle?.addEventListener('click', function() {
      navbarMenu?.classList.toggle('hidden');
    });

    document.addEventListener('click', function(event) {
      if (!userMenuButton?.contains(event.target) && !userDropdown?.contains(event.target)) {
        userDropdown?.classList.add('hidden');
      }
      if (!navbarToggle?.contains(event.target) && !navbarMenu?.contains(event.target)) {
        navbarMenu?.classList.add('hidden');
      }
    });
  });