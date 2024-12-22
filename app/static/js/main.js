document.addEventListener("DOMContentLoaded", function () {
    const loadingOverlay = document.getElementById("loading-overlay");
    const loaderMessage = document.getElementById("loader-message");
    const htmlTag = document.documentElement;
    const lang = htmlTag.lang || 'he'; // Default to 'he' if no lang is set
    // Show loading overlay and update message on form submission
    document.querySelectorAll("form").forEach(form => {
        form.addEventListener("submit", function () {
            // Show the loading overlay with the current step message
            loadingOverlay.classList.add("visible");
            loaderMessage.textContent = loaderMessage.textContent; // Set based on server-provided step message
        });
    });

    // Hide loading overlay once the page loads (after hardware response)
    window.addEventListener("pageshow", function () {
        loadingOverlay.classList.remove("visible");
    });

    //search
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        const userList = document.getElementById(searchInput.getAttribute("list-name"));
        const userItems = userList.querySelectorAll('li');

        // Filter the user list based on the search query
        searchInput.addEventListener('input', () => {
            const query = searchInput.value.toLowerCase();

            userItems.forEach(item => {
                const name = item.dataset.name.toLowerCase();
                const id = item.dataset.id.toLowerCase();


                if (name.includes(query) || id.includes(query)) {
                    item.style.display = ''; // Show item
                } else {
                    item.style.display = 'none'; // Hide item
                }
            });
        });
    }

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

    // help
    const helpButton = document.getElementById('help-button');
    const helpText = document.getElementById('help-text');

    helpButton.addEventListener('click', () => {
        if (helpText.classList.contains('hidden')) {
            helpText.classList.remove('hidden'); // Show help text
        } else {
            helpText.classList.add('hidden'); // Hide help text
        }
    });
    const userCircle=document.querySelector('.user-circle');
    userCircle.addEventListener('click', () => {
    
        const popup = document.getElementById('user-popup');
        popup.classList.toggle('hidden');
    });
    const closeModal = document.getElementById('close-details-modal');
    const detailsModal = document.getElementById('personal-details-modal');
    const openModalButton=document.getElementById('open-details-modal');
    closeModal.addEventListener("click", () => {
        detailsModal.classList.add("hidden");
    });
    openModalButton.addEventListener("click", () => {
        detailsModal.classList.remove("hidden");
    });


//update user details
    document.getElementById("personal-details-form").addEventListener("submit", async function (event) {
        event.preventDefault(); // Prevent default form submission
    
        const form = event.target;
        const formData = new FormData(form);
    
        try {
            const response = await fetch(form.action, {
                method: "POST",
                body: formData,
            });
    
            const result = await response.json();
    
            if (response.ok) {
                // Success: Close the modal and show a success message
                document.getElementById("personal-details-modal").classList.add("hidden");
                alert(result.message);
                // Redirect to the logout endpoint
                window.location.href = `/${lang}/logout`; // Replace `lang` with your current language
            } else {
                // Errors: Display them in the modal
                const errorContainer = detailsModal.querySelector("#modal-details-errors");
                errorContainer.innerHTML = ""; // Clear existing errors
    
                result.errors.forEach(error => {
                    const errorElement = document.createElement("p");
                    errorElement.classList.add("error");
                    errorElement.textContent = error;
                    errorContainer.appendChild(errorElement);
                });
            }
        } catch (error) {
            console.error("An unexpected error occurred:", error);
        }
        loadingOverlay.classList.remove("visible");
    });


    const closePasswordModal = document.getElementById('close-password-modal');
    const PasswordModal = document.getElementById('change-password-modal');
    const openPasswordModalButton=document.getElementById('open-password-modal');
    closePasswordModal.addEventListener("click", () => {
        PasswordModal.classList.add("hidden");
    });
    openPasswordModalButton.addEventListener("click", () => {
        PasswordModal.classList.remove("hidden");
    });
    document.getElementById("change-password-form").addEventListener("submit", async function (event) {
        event.preventDefault(); // Prevent default form submission
    
        const form = event.target;
        const formData = new FormData(form);
    
        try {
            const response = await fetch(form.action, {
                method: "POST",
                body: formData,
            });
    
            const result = await response.json();
    
            if (response.ok) {
                // Success: Close the modal and show a success message
                document.getElementById("change-password-modal").classList.add("hidden");
                alert(result.message);
                // Redirect to the logout endpoint
                window.location.href = `/${lang}/logout`; // Replace `lang` with your current language
            } else {
                // Errors: Display them in the modal
                const errorContainer = PasswordModal.querySelector("#modal-password-errors");
                errorContainer.innerHTML = ""; // Clear existing errors
    
                result.errors.forEach(error => {
                    const errorElement = document.createElement("p");
                    errorElement.classList.add("error");
                    errorElement.textContent = error;
                    errorContainer.appendChild(errorElement);
                });
            }
        } catch (error) {
            console.error("An unexpected error occurred:", error);
        }
        loadingOverlay.classList.remove("visible");
    });
    
});
