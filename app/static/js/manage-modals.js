document.addEventListener('DOMContentLoaded', () => {
    const htmlTag = document.documentElement;
    const lang = htmlTag.lang || 'en';

    const modal = document.getElementById('entity-modal');
    const form = modal.querySelector('#entity-form');
    const modalTitle = modal.querySelector('#modal-title');
    const entityIdInput = modal.querySelector('#entity_id');
    const closeModal = modal.querySelector('#close-entity-modal');
    
    //for errors
    if (modal.classList.contains('open')) {
        modal.classList.remove('hidden');
    }
    // Close modal handler
    closeModal.addEventListener("click", () => {
        modal.classList.add("hidden");
    });

    /**
     * Function to open modal for adding or editing an entity.
     * @param {string} action - Either 'add' or 'edit'.
     * @param {string} entityType - Entity type (e.g., 'users', 'medicines').
     * @param {object} entityData - Data of the entity for editing (optional).
     */
    window.openModal =function(action, entityType, entityData = null) {
        modalTitle.textContent = action === 'add' ? modalTitle.getAttribute("add-text") : modalTitle.getAttribute("edit-text");
        form.reset();
        // Explicitly clear all input values to avoid pre-filled fields
        const inputs = modal.querySelectorAll('input, select');
        inputs.forEach(input => {
            if (input.type !== 'hidden') {
                input.value = ''; // Clear input fields
            }
    });
        entityIdInput.value = action === 'add' ? 0 : entityData.id; // Set ID for edit

        const errors = modal.querySelectorAll('.error');
        errors.forEach(error => error.remove());

        // Populate form fields for edit
        if (action === 'edit' && entityData) {
            for (const key in entityData) {
                const input = document.getElementById(key);
                if (input) {
                    input.value = entityData[key];
                }
            }
        }

        modal.classList.remove('hidden');
    }

    /**
     * Fetch entity data and open modal for editing.
     * @param {string} entityType - Entity type (e.g., 'users', 'medicines').
     * @param {number} entityId - ID of the entity to edit.
     */
    window.fetchEntityAndOpenModal = function (entityType, entityId) {
        fetch(`/${lang}/management/${entityType}/${entityId}`)
            .then(response => response.json())
            .then(data => {
                openModal('edit', entityType, data);
            })
            .catch(error => console.error(`Error fetching ${entityType}:`, error));
    }

    /**
     * Delete an entity with confirmation.
     * @param {string} entityType - Entity type (e.g., 'users', 'medicines').
     * @param {number} entityId - ID of the entity to delete.
     * @param {string} entityName - Name of the entity to display in confirmation modal.
     */
     window.deleteEntity = function(entityType, entityId, entityName) {
        showConfirmationModal('delete', entityName, { entityId }, payload => {
            fetch(`/${lang}/management/${entityType}/${payload.entityId}`, { method: 'DELETE' })
                .then(response => {
                    if (response.ok) {
                        const entityItem = document.querySelector(`.delete-button[data-entity-id="${payload.entityId}"]`).closest('li');
                        entityItem.remove();
                    } else {
                        alert(`Failed to delete ${entityType}.`);
                    }
                })
                .catch(error => {
                    console.error(`Error deleting ${entityType}:`, error);
                    alert(`Failed to delete ${entityType}.`);
                });
        });
    }

    /**
     * Initialize event listeners for a specific entity type.
     * @param {string} entityType - Entity type (e.g., 'users', 'medicines').
     */
    function initializeEntityActions(entityType) {
        // Add button
        const addButton = document.getElementById(`add-${entityType}-btn`);
        if (addButton) {
            addButton.addEventListener('click', () => openModal('add', entityType));
        }

        // Edit buttons
        modal.querySelectorAll(`.edit-button[data-entity-type="${entityType}"]`).forEach(button => {
            button.addEventListener('click', (event) => {
                const entityId = event.target.dataset.entityId;
                fetchEntityAndOpenModal(entityType, entityId);
            });
        });

        // Delete buttons
        modal.querySelectorAll(`.delete-button[data-entity-type="${entityType}"]`).forEach(button => {
            button.addEventListener('click', () => {
                const entityId = button.getAttribute('data-entity-id');
                const entityName = button.closest('li').querySelector('.item-name').textContent;
                deleteEntity(entityType, entityId, entityName);
            });
        });
    }

    // Initialize actions for users and medicines
    initializeEntityActions('users');
    initializeEntityActions('medicines');
    initializeEntityActions('patients');
    // initializeEntityActions('prescriptions');
});
