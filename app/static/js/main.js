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
});