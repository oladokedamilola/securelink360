// Switch between light and dark mode
const themeToggleButton = document.getElementById('themeToggle');
const body = document.body;

// Check if the user has set a theme in localStorage
const currentTheme = localStorage.getItem('theme') || 'light-mode';
body.classList.add(currentTheme);

// Toggle theme on button click
themeToggleButton.addEventListener('click', () => {
    // Toggle between light and dark
    if (body.classList.contains('light-mode')) {
        body.classList.replace('light-mode', 'dark-mode');
        localStorage.setItem('theme', 'dark-mode');
    } else {
        body.classList.replace('dark-mode', 'light-mode');
        localStorage.setItem('theme', 'light-mode');
    }
});

// Sidebar toggle functionality for small screens
const sidebar = document.getElementById('sidebar');
if (sidebar) {
    const toggleBtn = document.createElement('button');
    toggleBtn.classList.add('sidebar-toggle-btn', 'btn', 'btn-primary');
    toggleBtn.innerHTML = '<i class="bi bi-arrow-right-circle"></i>';
    toggleBtn.style.display = 'none';
    document.body.appendChild(toggleBtn);

    toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('d-none');
    });

    // Show sidebar toggle button on smaller screens
    window.addEventListener('resize', () => {
        if (window.innerWidth < 768) {
            toggleBtn.style.display = 'block';
        } else {
            toggleBtn.style.display = 'none';
        }
    });
}
