// Shared hover-preview for card names. Loaded on every page by header.js.
// Any element carrying a data-img attribute (a Scryfall image URL) shows that
// image near the cursor while hovered. Uses delegated listeners on document so
// it keeps working when DataTables paginates or filters rows in place.

function init() {
    if (window.__cardHoverReady) return;   // header.js loads this once; guard anyway
    window.__cardHoverReady = true;

    const style = document.createElement('style');
    style.textContent = `
        .card-hover-popup {
            position: fixed;
            z-index: 10000;
            display: none;
            width: 244px;
            pointer-events: none;
            border: 1px solid var(--border-color);
            border-radius: 5px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35);
            background: var(--background);
            overflow: hidden;
        }
        .card-hover-popup img {
            display: block;
            width: 100%;
        }
    `;
    document.head.appendChild(style);

    const popup = document.createElement('div');
    popup.className = 'card-hover-popup';
    const img = document.createElement('img');
    popup.appendChild(img);
    document.body.appendChild(popup);

    const CURSOR_GAP = 16;   // space between cursor and popup
    const EDGE_MARGIN = 8;   // min space kept from the viewport edge
    let currentUrl = null;   // URL the <img> is currently loaded (or loading) with
    let hovering = false;    // pointer is over a data-img element right now
    let mouseX = 0, mouseY = 0;

    function position(x, y) {
        const w = popup.offsetWidth;
        const h = popup.offsetHeight;

        let left = x + CURSOR_GAP;
        if (left + w > window.innerWidth - EDGE_MARGIN) {
            left = x - CURSOR_GAP - w;   // flip to the left of the cursor
        }
        left = Math.max(EDGE_MARGIN, left);

        let top = y + CURSOR_GAP;
        if (top + h > window.innerHeight - EDGE_MARGIN) {
            top = window.innerHeight - EDGE_MARGIN - h;   // pull up from the bottom
        }
        top = Math.max(EDGE_MARGIN, top);

        popup.style.left = left + 'px';
        popup.style.top = top + 'px';
    }

    function reveal() {
        popup.style.display = 'block';
        position(mouseX, mouseY);
    }

    function show(target) {
        const url = target.getAttribute('data-img');
        if (!url) return;
        hovering = true;
        if (url === currentUrl) {
            // Same card, image already decoded — show it straight away.
            if (img.complete) reveal();
            return;
        }
        // New card: keep the popup hidden until the new image has loaded, so we
        // never flash the previous card's image at the new position.
        currentUrl = url;
        popup.style.display = 'none';
        img.src = url;
    }

    function hide() {
        hovering = false;
        popup.style.display = 'none';
    }

    img.addEventListener('load', function() {
        // Ignore a stale load if the pointer has already moved on to another card.
        if (hovering && img.getAttribute('src') === currentUrl) reveal();
    });
    img.addEventListener('error', function() {
        currentUrl = null;
        popup.style.display = 'none';
    });

    document.addEventListener('mouseover', function(e) {
        mouseX = e.clientX;
        mouseY = e.clientY;
        const target = e.target.closest('[data-img]');
        if (target) show(target);
    });

    document.addEventListener('mousemove', function(e) {
        mouseX = e.clientX;
        mouseY = e.clientY;
        if (popup.style.display === 'block') position(mouseX, mouseY);
    });

    document.addEventListener('mouseout', function(e) {
        const target = e.target.closest('[data-img]');
        if (target && !target.contains(e.relatedTarget)) hide();
    });

    // A stale popup left hanging after the page scrolls looks broken.
    window.addEventListener('scroll', hide, true);
}

// header.js appends this script after DOMContentLoaded has already fired, so run
// straight away when that's the case.
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
