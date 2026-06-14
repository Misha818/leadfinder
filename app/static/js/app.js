// Company Finder Unified Client-Side Engine

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

    // ----------------------------------------------------
    // 3. Automated Search Execution Background Crawler (results page only)
    // ----------------------------------------------------
    // If we are on the search results view page and the status is pending
    const resultsPageCheck = document.getElementById('leads-table');
    if (resultsPageCheck && window.location.pathname.includes('/search/results/')) {
        const pathSegments = window.location.pathname.split('/');
        const searchId = pathSegments[pathSegments.length - 1];

        // We check if the database has 0 leads and search needs execution
        // We trigger the execute API call automatically!
        const rows = document.querySelectorAll('.lead-row');
        if (rows.length === 0) {
            triggerSearchCrawl(searchId);
        }
    }
});

// ----------------------------------------------------
// 4. Billing Approval Modal AJAX Interceptor
// ----------------------------------------------------
let pendingSearchRequest = null; // Stash search ID during modal auth flows

function triggerSearchCrawl(searchId, userApproved = false) {
    toggleLoader(true, "Initializing Google Places B2B Crawls & Real Website Scrapes...");

    const headers = { 'Content-Type': 'application/json' };
    if (userApproved) {
        headers['X-User-Approved'] = 'true';
    }

    fetch(`/search/execute/${searchId}`, {
        method: 'POST',
        headers: headers
    })
    .then(response => {
        if (response.status === 402) {
            // Credit Exhausted! Intercept payment required and launch modal
            pendingSearchRequest = searchId;
            launchBillingModal();
            return null;
        } else if (!response.ok) {
            return response.json().then(err => { throw new Error(err.error || "Crawl transaction failed.") });
        }
        return response.json();
    })
    .then(data => {
        if (data && data.success) {
            toggleLoader(false);
            showToast("Scan Complete", `Successfully crawled and scored ${data.count} leads inside SQLite!`, "success");
            // Reload page to render table leads cleanly
            setTimeout(() => window.location.reload(), 1500);
        }
    })
    .catch(err => {
        console.error(err);
        toggleLoader(false);
        showToast("Crawler Error", err.message || "Network error launching B2B lead crawling services.", "danger");
    });
}

function launchBillingModal() {
    toggleLoader(false); // Hide spinner during prompt modal

    const modalEl = document.getElementById('billingApprovalModal');
    const modal = new bootstrap.Modal(modalEl);

    // Fetch live prices to show estimated cost
    fetch('/search/api/billing/prices')
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                // Calculation: sum worst case cost
                const basic = parseFloat(data.prices.basic || 0.017);
                const contact = parseFloat(data.prices.contact || 0.003);
                const atmosphere = parseFloat(data.prices.atmosphere || 0.005);
                const totalCost = (basic + contact + atmosphere).toFixed(3);

                document.getElementById('modal-estimated-cost').textContent = `$${totalCost} USD`;
            }
        })
        .catch(err => {
            console.error("Failed to load live price tooltips:", err);
            document.getElementById('modal-estimated-cost').textContent = "$0.025 USD"; // Fallback estimation
        })
        .finally(() => {
            modal.show();

            // Handle Cancel and Approve buttons
            document.getElementById('btn-billing-cancel').onclick = () => {
                modal.hide();
                showToast("Crawl Aborted", "Lead discovery canceled by user.", "warning");
                pendingSearchRequest = null;
            };

            document.getElementById('btn-billing-approve').onclick = () => {
                modal.hide();
                if (pendingSearchRequest) {
                    triggerSearchCrawl(pendingSearchRequest, true); // Re-run search with approved flag!
                    pendingSearchRequest = null;
                }
            };
        });
}

// ----------------------------------------------------
// 5. Helper Utility Functions (Toasts and Loader)
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
