
// import { renderNavbar, renderFooter } from './components.js';

document.addEventListener('DOMContentLoaded', () => {
    // Determine active page based on URL
    const path = window.location.pathname;
    let activePage = 'home';
    if (path.includes('dashboard.html')) {
        activePage = 'dashboard';
    } else if (path.includes('solutions.html')) {
        activePage = 'solutions';
    } else if (path.includes('pricing.html')) {
        activePage = 'pricing';
    } else if (path.includes('impact.html')) {
        activePage = 'impact';
    } else if (path.includes('contact.html')) {
        activePage = 'contact';
    }

    renderNavbar(activePage);
    renderFooter();

    // Scroll Animation Observer
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target); // Only animate once
            }
        });
    }, observerOptions);

    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });
});
