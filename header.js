document.addEventListener('DOMContentLoaded', function() {
    const header = `
        <style>
            .nav-dropdown {
                position: relative;
            }
            .nav-dropdown-menu {
                display: none;
                position: absolute;
                top: 100%;
                left: 0;
                background-color: white;
                border: 1px solid var(--border-color);
                min-width: 140px;
                z-index: 100;
            }
            .nav-dropdown:hover .nav-dropdown-menu {
                display: block;
            }
            .nav-dropdown-menu a {
                display: block;
                padding: 8px 14px;
            }
            .nav-dropdown-menu a:hover {
                background-color: rgba(255, 255, 255, 0.05);
            }
        </style>
        <div class="header">
            <div style="display: flex; align-items: center; gap: 30px;">
                <h1><a href="/">Canlandata</a></h1>
                <nav>
                    <div class="nav-dropdown">
                        <a href="/cards_table">Cards</a>
                        <div class="nav-dropdown-menu">
                            <a href="/cards_lines">Trend Lines</a>
                            <a href="/cards_table">Data Table</a>
                        </div>
                    </div>
                    <a href="/colors">Colors</a>
                    <a href="/sets">Sets</a>
                </nav>
            </div>
            <a href="/about">About</a>
        </div>
    `;
    document.getElementById('header-placeholder').innerHTML = header;
});
