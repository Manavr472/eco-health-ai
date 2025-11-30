function renderNavbar(activePage = 'home') {
    const navbarHTML = `
        <div class="container flex justify-between items-center">
            <a href="index.html" class="flex items-center gap-sm">
                <h2 class="text-primary font-bold" style="font-size: 1.5rem;">Eco-Health AI</h2>
            </a>
            <nav class="flex gap-md items-center" style="display: none;" id="desktop-nav">
                <a href="index.html" class="nav-link ${activePage === 'home' ? 'active' : ''}">Home</a>
                <a href="solutions.html" class="nav-link ${activePage === 'solutions' ? 'active' : ''}">Solutions</a>
                <a href="dashboard.html" class="nav-link ${activePage === 'dashboard' ? 'active' : ''}">Dashboard</a>
                <a href="impact.html" class="nav-link ${activePage === 'impact' ? 'active' : ''}">Impact</a>
                <a href="pricing.html" class="nav-link ${activePage === 'pricing' ? 'active' : ''}">Pricing</a>
                <a href="contact.html" class="nav-link ${activePage === 'contact' ? 'active' : ''}">Contact</a>
            </nav>
            <button class="btn btn-primary" style="display: block; md:display: none;" id="mobile-menu-btn">Menu</button>
        </div>
        <div id="mobile-menu" style="display: none; padding: 1rem; border-top: 1px solid var(--border-color);">
             <div class="flex flex-col gap-sm">
                <a href="index.html" class="nav-link ${activePage === 'home' ? 'active' : ''}">Home</a>
                <a href="solutions.html" class="nav-link ${activePage === 'solutions' ? 'active' : ''}">Solutions</a>
                <a href="dashboard.html" class="nav-link ${activePage === 'dashboard' ? 'active' : ''}">Dashboard</a>
                <a href="impact.html" class="nav-link ${activePage === 'impact' ? 'active' : ''}">Impact</a>
                <a href="pricing.html" class="nav-link ${activePage === 'pricing' ? 'active' : ''}">Pricing</a>
                <a href="contact.html" class="nav-link ${activePage === 'contact' ? 'active' : ''}">Contact</a>
             </div>
        </div>
    `;

    const navElement = document.createElement('header');
    navElement.className = 'navbar';
    navElement.innerHTML = navbarHTML;
    document.body.prepend(navElement);

    // Simple responsive menu logic
    const desktopNav = document.getElementById('desktop-nav');
    const mobileBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');

    // Media query check for simple responsiveness
    const checkSize = () => {
        if (window.innerWidth >= 768) {
            desktopNav.style.display = 'flex';
            mobileBtn.style.display = 'none';
            mobileMenu.style.display = 'none';
        } else {
            desktopNav.style.display = 'none';
            mobileBtn.style.display = 'block';
        }
    };

    window.addEventListener('resize', checkSize);
    checkSize(); // Initial check

    mobileBtn.addEventListener('click', () => {
        mobileMenu.style.display = mobileMenu.style.display === 'none' ? 'block' : 'none';
    });
}

function renderFooter() {
    const footerHTML = `
        <div class="container py-xl text-center">
            <p class="text-gray">© 2025 Eco-Health AI. All rights reserved.</p>
        </div>
    `;
    const footerElement = document.createElement('footer');
    footerElement.className = 'bg-white border-t';
    footerElement.style.borderTop = '1px solid var(--border-color)';
    footerElement.innerHTML = footerHTML;
    document.body.appendChild(footerElement);
}
