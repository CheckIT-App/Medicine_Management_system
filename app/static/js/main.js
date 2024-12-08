document.addEventListener("DOMContentLoaded", function() {
    const loadingOverlay = document.getElementById("loading-overlay");
    const loaderMessage = document.getElementById("loader-message");

    // Show loading overlay and update message on form submission
    document.querySelectorAll("form").forEach(form => {
        form.addEventListener("submit", function() {
            // Show the loading overlay with the current step message
            loadingOverlay.classList.add("visible");
            loaderMessage.textContent = loaderMessage.textContent; // Set based on server-provided step message
        });
    });

    // Hide loading overlay once the page loads (after hardware response)
    window.addEventListener("pageshow", function() {
        loadingOverlay.classList.remove("visible");
    });

    //search
    const searchInput = document.getElementById('search-input');
    const userList = document.getElementById(searchInput.getAttribute("list-name"));
    const userItems = userList.querySelectorAll('li');

    // Filter the user list based on the search query
    searchInput.addEventListener('input', () => {
        const query = searchInput.value.toLowerCase();

        userItems.forEach(item => {
            const name = item.dataset.name.toLowerCase();
            const id = item.dataset.id.toLowerCase();
            

            if (name.includes(query) || id.includes(query) ) {
                item.style.display = ''; // Show item
            } else {
                item.style.display = 'none'; // Hide item
            }
        });
    });


    // tooggle button
    const toggleButtons = document.querySelectorAll('.toggle-details');

    toggleButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            const parentItem = button.closest('.action-list-item');
            const details = parentItem.querySelector('.item-details');

            // Toggle visibility
            if (details.classList.contains('hidden')) {
                details.classList.remove('hidden');
                button.textContent = '-'; // Change to collapse symbol
            } else {
                details.classList.add('hidden');
                button.textContent = '+'; // Change to expand symbol
            }
        });
    });

});
