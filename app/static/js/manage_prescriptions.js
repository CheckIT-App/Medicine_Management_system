document.addEventListener('DOMContentLoaded', () => {
    const addMedicineButton = document.getElementById('add-medicine-button');
    const medicinesSection = document.getElementById('medicines-section');
    const prescriptionForm = document.getElementById('entity-form');
    const addButton = document.getElementById('add-prescriptions-btn');
    const entityModal = document.getElementById('entity-modal');
    const form = document.getElementById('entity-form');
    const modalTitle = document.getElementById('modal-title');
    let medicinesData = [];
    let uniqueIdCounter = 1;

    const htmlTag = document.documentElement;
    const lang = htmlTag.lang || 'he'; // Default to 'he' if no lang is set
    const entityType = 'prescriptions';

    // Open modal for adding a new prescription
    addButton.addEventListener('click', () => {
        form.reset(); // Clear previous inputs
        medicinesSection.innerHTML = ""; // Clear medicine section
        addMedicineField(); // Add the first medicine field
        openModal('add', entityType);
    });

    // Handle delete buttons
    document.querySelectorAll(`.delete-button[data-entity-type="${entityType}"]`).forEach(button => {
        button.addEventListener('click', () => {
            const entityId = button.getAttribute('data-entity-id');
            const entityName = button.closest('li').querySelector('.item-name').textContent;
            deleteEntity(entityType, entityId, entityName);
        });
    });

    // Fetch available medicines
    fetch(`/${lang}/management/prescriptions/medicines_list`)
        .then(response => response.json())
        .then(data => {
            medicinesData = data;
            addMedicineField(); // Populate the first dropdown
        })
        .catch(error => console.error('Error fetching medicines:', error));

    // Add medicine field dynamically
    addMedicineButton.addEventListener('click', () => {
        addMedicineField();
    });

    // Submit form handler
    prescriptionForm.addEventListener('submit', (event) => {
        event.preventDefault(); // Prevent default form submission

        const formData = new FormData(prescriptionForm);
        const medicineIds = Array.from(formData.getAll('medicine_ids')).map(Number);
        const quantities = Array.from(formData.getAll('quantities')).map(Number);

        // Remove the existing values and append properly formatted ones
        formData.delete('medicine_ids');
        formData.delete('quantities');
        medicineIds.forEach(id => formData.append('medicine_ids', id));
        quantities.forEach(qty => formData.append('quantities', qty));

        // Submit the form via fetch
        fetch(prescriptionForm.action, {
            method: 'POST',
            body: formData,
        })
        .then(response => {
            if (response.ok) {
                window.location.href = response.url; // Redirect if successful
            } else {
                return response.json().then(err => console.error('Error:', err));
            }
        })
        .catch(error => console.error('Submit Error:', error));
    });

    // Open modal for editing a prescription
    document.querySelectorAll('.edit-button').forEach(button => {
        button.addEventListener('click', (event) => {
            const prescriptionId = event.target.dataset.entityId;
            modalTitle.textContent = "Edit Prescription";
            form.reset(); // Clear previous inputs
            medicinesSection.innerHTML = ""; // Clear medicine section
            entityModal.classList.remove('hidden');

            fetch(`/${lang}/management/prescriptions/${prescriptionId}`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('entity_id').value = data.id;
                    document.getElementById('patient_id').value = data.patient_id;
                    document.getElementById('prescribed_by').value = data.prescribed_by;

                    // Populate medicines section with data
                    data.medicines.forEach(medicine => {
                        addMedicineField(medicine.id, medicine.quantity);
                    });
                })
                .catch(error => console.error('Error fetching prescription:', error));
        });
    });

    // Add a new medicine field dynamically
    function addMedicineField(selectedMedicineId = "", quantity = "") {
        const uniqueIndex = `medicine_${uniqueIdCounter++}`;
        const medicineItem = document.createElement('div');
        medicineItem.classList.add('medicine-item');
        medicineItem.dataset.index = uniqueIndex;

        const medicineSelectGroup = document.createElement('div');
        medicineSelectGroup.classList.add('form-group');

        const medicineLabel = document.createElement('label');
        medicineLabel.setAttribute('for', uniqueIndex);
        medicineLabel.textContent = medicinesSection.getAttribute('medicine-name');

        const medicineSelect = document.createElement('select');
        medicineSelect.setAttribute('name', 'medicine_ids');
        medicineSelect.setAttribute('id', uniqueIndex);
        medicineSelect.required = true;

        medicinesData.forEach(medicine => {
            const option = document.createElement('option');
            option.value = medicine.id;
            option.textContent = medicine.name;
            if (medicine.id === selectedMedicineId) {
                option.selected = true;
            }
            medicineSelect.appendChild(option);
        });

        medicineSelectGroup.appendChild(medicineLabel);
        medicineSelectGroup.appendChild(medicineSelect);

        const quantityGroup = document.createElement('div');
        quantityGroup.classList.add('form-group');

        const quantityLabel = document.createElement('label');
        quantityLabel.setAttribute('for', `quantity_${uniqueIndex}`);
        quantityLabel.textContent = medicinesSection.getAttribute('quantity-name');

        const quantityInput = document.createElement('input');
        quantityInput.setAttribute('type', 'number');
        quantityInput.setAttribute('name', 'quantities');
        quantityInput.setAttribute('id', `quantity_${uniqueIndex}`);
        quantityInput.setAttribute('value', quantity);
        quantityInput.required = true;

        quantityGroup.appendChild(quantityLabel);
        quantityGroup.appendChild(quantityInput);

        const removeButton = document.createElement('button');
        removeButton.type = 'button';
        removeButton.classList.add('remove-medicine-button');
        removeButton.innerHTML = '&times;'; // X symbol
        removeButton.setAttribute('aria-label', 'Remove');
        removeButton.addEventListener('click', () => {
            medicinesSection.removeChild(medicineItem);
        });

        medicineItem.appendChild(medicineSelectGroup);
        medicineItem.appendChild(quantityGroup);
        medicineItem.appendChild(removeButton);

        medicinesSection.appendChild(medicineItem);
    }
});
