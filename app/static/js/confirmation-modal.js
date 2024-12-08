// modal.js
document.addEventListener("DOMContentLoaded", () => {
    const confirmationModal = document.getElementById("confirmation-modal");

    // Scope all elements inside the modal
    const closeModal = confirmationModal.querySelector("#close-modal");
    const modalConfTitle = confirmationModal.querySelector("#modal-confirmation-title");
    const modalMessage = confirmationModal.querySelector("#modal-message");
    const confirmActionButton = confirmationModal.querySelector("#confirm-action");
    const cancelActionButton = confirmationModal.querySelector("#cancel-action");

    // Close modal on 'x' button or cancel
    closeModal.addEventListener("click", () => {
        confirmationModal.classList.add("hidden");
    });

    cancelActionButton.addEventListener("click", () => {
        confirmationModal.classList.add("hidden");
    });

    // Function to show modal
    window.showConfirmationModal = function (action, targetName, payload, confirmCallback) {
        modalConfTitle.textContent = `Confirm ${action}`;
        modalMessage.textContent = `Are you sure you want to ${action} ${targetName}?`;

        confirmationModal.classList.remove("hidden");

        confirmActionButton.onclick = () => {
            confirmCallback(payload);
            confirmationModal.classList.add("hidden");
        };
    };
});
