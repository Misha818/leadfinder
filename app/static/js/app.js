// Company Finder UI Management

document.addEventListener('DOMContentLoaded', () => {
    // ----------------------------------------------------
    // 1. Light/Dark Theme Switch Logic
    // ----------------------------------------------------
    const themeToggle = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;

    // Load theme from localStorage, strictly defaulting to 'light' (No auto-system detection)
    const storedTheme = localStorage.getItem('theme') || 'light';
    htmlElement.setAttribute('data-bs-theme', storedTheme);
    updateToggleIcon(storedTheme);

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = htmlElement.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            htmlElement.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateToggleIcon(newTheme);
            showToast('Theme Changed', `Switched to ${newTheme} mode!`, 'info');
        });
    }

    function updateToggleIcon(theme) {
        const icon = document.querySelector('#theme-toggle i');
        if (icon) {
            if (theme === 'dark') {
                icon.className = 'bi bi-sun-fill text-warning';
                icon.title = 'Switch to Light Mode';
            } else {
                icon.className = 'bi bi-moon-stars-fill text-secondary';
                icon.title = 'Switch to Dark Mode';
            }
        }
    }

    // ----------------------------------------------------
    // 2. Responsive Mobile Sidebar Toggles
    // ----------------------------------------------------
    const sidebar = document.getElementById('sidebar');
    const sidebarToggleBtn = document.getElementById('sidebar-toggle-btn');
    const sidebarMobileBtn = document.getElementById('sidebar-mobile-btn');

    if (sidebarMobileBtn && sidebar) {
        sidebarMobileBtn.addEventListener('click', () => {
            sidebar.classList.add('show');
        });
    }

    if (sidebarToggleBtn && sidebar) {
        sidebarToggleBtn.addEventListener('click', () => {
            sidebar.classList.remove('show');
        });
    }
});

// ----------------------------------------------------
// 3. Helper Utility Functions (Toasts and Loader)
// ----------------------------------------------------

/**
 * Trigger loading overlay spinner with customizable text.
 * @param {boolean} show - Set to true to show, false to hide.
 * @param {string} [text] - Text to display under spinner.
 */
function toggleLoader(show, text = 'Processing Lead Scan...') {
    const loader = document.getElementById('loading-overlay');
    if (!loader) return;

    if (show) {
        const textElement = loader.querySelector('p');
        if (textElement) textElement.textContent = text;
        loader.classList.remove('d-none');
    } else {
        loader.classList.add('d-none');
    }
}

/**
 * Show a Bootstrap Toast notification.
 * @param {string} title - Title of notification.
 * @param {string} message - Content body of notification.
 * @param {string} [type='primary'] - 'primary', 'success', 'warning', 'danger', 'info'
 */
function showToast(title, message, type = 'primary') {
    const toastEl = document.getElementById('app-toast');
    if (!toastEl) return;

    // Set header and body text
    document.getElementById('toast-title').textContent = title;
    document.getElementById('toast-body').textContent = message;

    // Set icon and colors depending on notification type
    const icon = document.getElementById('toast-icon');
    icon.className = 'bi me-2 ';

    if (type === 'success') {
        icon.classList.add('bi-check-circle-fill', 'text-success');
    } else if (type === 'danger') {
        icon.classList.add('bi-exclamation-triangle-fill', 'text-danger');
    } else if (type === 'warning') {
        icon.classList.add('bi-exclamation-circle-fill', 'text-warning');
    } else if (type === 'info') {
        icon.classList.add('bi-info-circle-fill', 'text-info');
    } else {
        icon.classList.add('bi-info-circle-fill', 'text-primary');
    }

    // Initialize and trigger Bootstrap Toast
    const toast = new bootstrap.Toast(toastEl, { delay: 4000 });
    toast.show();
}
