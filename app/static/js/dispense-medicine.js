document.addEventListener("DOMContentLoaded", () => {
    // Toggle quantity input when a checkbox is clicked
    const checkboxes = document.querySelectorAll('input[type="checkbox"][data-medicine-key]');
    checkboxes.forEach((checkbox) => {
        checkbox.addEventListener("change", () => {
            const uniqueKey = checkbox.getAttribute("data-medicine-key");
            const quantityInput = document.getElementById(`${uniqueKey}-quantity`);
            if (checkbox.checked) {
                quantityInput.disabled = false; // Enable input
            } else {
                quantityInput.disabled = true; // Disable input
                quantityInput.value = quantityInput.max; // Reset to max value
            }
        });
    });

    // Select all medicines
    const selectAllButton = document.getElementById("select-all-button");
    selectAllButton.addEventListener("click", () => {
        checkboxes.forEach((checkbox) => {
            const uniqueKey = checkbox.getAttribute("data-medicine-key");
            checkbox.checked = true;
            const quantityInput = document.getElementById(`${uniqueKey}-quantity`);
            quantityInput.disabled = false; // Enable input
        });
    });

    // Clear all selections
    const clearAllButton = document.getElementById("clear-all-button");
    clearAllButton.addEventListener("click", () => {
        checkboxes.forEach((checkbox) => {
            const uniqueKey = checkbox.getAttribute("data-medicine-key");
            checkbox.checked = false;
            const quantityInput = document.getElementById(`${uniqueKey}-quantity`);
            quantityInput.disabled = true; // Disable input
            quantityInput.value = quantityInput.max; // Reset to max value
        });
    });
});
