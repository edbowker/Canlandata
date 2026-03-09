document.addEventListener('DOMContentLoaded', function() {
    const header = `
        <div class="header">
            <div style="display: flex; align-items: center; gap: 30px;">
                <h1><a href="/">Canlandata</a></h1>
                <nav>
                    <a href="/">Card Play Rates</a>
                    <a href="/colors">Color Representation</a>
                    <a href="/sets">Set Representation</a>
                </nav>
            </div>
            <a href="/about">About</a>
        </div>
    `;
    document.getElementById('header-placeholder').innerHTML = header;
});