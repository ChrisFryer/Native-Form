/* Native-Form client-side utilities */

/**
 * CSRF-aware POST via Fetch API.
 */
function apiPost(url, data) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    return fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify(data),
    });
}

/**
 * Simple client-side table sorting.
 * Add data-sortable to <table> and it enables click-to-sort on <th> elements.
 */
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('table[data-sortable]').forEach(function (table) {
        const headers = table.querySelectorAll('th');
        headers.forEach(function (th, colIndex) {
            th.style.cursor = 'pointer';
            th.addEventListener('click', function () {
                sortTable(table, colIndex);
            });
        });
    });
});

function sortTable(table, colIndex) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const currentDir = table.dataset.sortDir === 'asc' ? 'desc' : 'asc';
    table.dataset.sortDir = currentDir;
    table.dataset.sortCol = colIndex;

    rows.sort(function (a, b) {
        const aText = a.cells[colIndex].textContent.trim().toLowerCase();
        const bText = b.cells[colIndex].textContent.trim().toLowerCase();
        if (aText < bText) return currentDir === 'asc' ? -1 : 1;
        if (aText > bText) return currentDir === 'asc' ? 1 : -1;
        return 0;
    });

    rows.forEach(function (row) {
        tbody.appendChild(row);
    });
}
