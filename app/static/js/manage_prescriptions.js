

document.addEventListener('DOMContentLoaded', () => {
    const addMedicineButton = document.getElementById('add-medicine-button');
    const medicinesSection = document.getElementById('medicines-section');
    const prescriptionForm = document.getElementById('entity-form');
    const addButton = document.getElementById(`add-prescriptions-btn`);
    const entityModal = document.getElementById('entity-modal');
    const form = document.getElementById('entity-form');
    const modalTitle = document.getElementById('modal-title');
    let medicinesData = [];
    let medicineIndex = 1;

    // Fetch medicines from the API
    // Get the <html> tag
    const htmlTag = document.documentElement;

    
    // Get the lang attribute value
    const lang = htmlTag.lang || 'he'; // Default to 'en' if no lang is set

    // Import or include gettext.js
    // const gt = new Gettext({ domain: "messages" }); // 'messages' is your translation file's domain

    // // Load translation JSON file
    // fetch('/path/to/messages.json')
    //     .then(response => response.json())
    //     .then(translations => {
    //         gt.loadJSON(translations, "messages"); // Load translations for the "messages" domain
    //     })
    //     .catch(error => console.error("Failed to load translations:", error));
    const entityType='prescriptions'
    // Add button
    addButton.addEventListener('click', () => {
        form.reset(); // Clear previous inputs
        medicinesSection.innerHTML = ""; // Clear medicine section
        addMedicineField(medicineIndex);
        openModal('add', entityType)}
    );
    

    // Edit buttons
    // document.querySelectorAll(`.edit-button[data-entity-type="${entityType}"]`).forEach(button => {
    //     button.addEventListener('click', (event) => {
    //         const entityId = event.target.dataset.entityId;
    //         fetchEntityAndOpenModal(entityType, entityId);
    //     });
    // });

    // Delete buttons
    document.querySelectorAll(`.delete-button[data-entity-type="${entityType}"]`).forEach(button => {
        button.addEventListener('click', () => {
            const entityId = button.getAttribute('data-entity-id');
            const entityName = button.closest('li').querySelector('.item-name').textContent;
            deleteEntity(entityType, entityId, entityName);
        });
    });
    fetch(`/${lang}/management/prescriptions/medicines_list`)
        .then(response => response.json())
        .then(data => {
            medicinesData = data;
            addMedicineField(medicineIndex); // Populate first dropdown
        })
        .catch(error => console.error('Error fetching medicines:', error));

    addMedicineButton.addEventListener('click', () => {
        medicineIndex++;
        addMedicineField(medicineIndex);
    });

    prescriptionForm.addEventListener('submit', (event) => {
        event.preventDefault(); // Prevent default form submission

        const formData = new FormData(prescriptionForm);
        
        // Cast medicine_ids and quantities to integers
        const medicineIds = Array.from(formData.getAll('medicine_ids')).map(Number);
        const quantities = Array.from(formData.getAll('quantities')).map(Number);

        // Debug: Log converted data
        console.log('Medicine IDs:', medicineIds);
        console.log('Quantities:', quantities);

        // Rebuild FormData with converted data
        formData.delete('medicine_ids');
        formData.delete('quantities');
        medicineIds.forEach(id => formData.append('medicine_ids', id));
        quantities.forEach(qty => formData.append('quantities', qty));

        // Submit the form
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

    // function populateMedicineDropdown(index) {
    //     const medicineItem = document.createElement('div');
    //     medicineItem.classList.add('medicine-item');

    //     const medicineSelectGroup = document.createElement('div');
    //     medicineSelectGroup.classList.add('form-group');
    //     const medicineLabel = document.createElement('label');
    //     medicineLabel.setAttribute('for', `medicine_${index}`);
    //     medicineLabel.textContent = medicinesSection.getAttribute('medicine-name');
    //     const medicineSelect = document.createElement('select');
    //     medicineSelect.setAttribute('name', `medicine_ids`);
    //     medicineSelect.setAttribute('id', `medicine_${index}`);
    //     medicineSelect.setAttribute('required', true);

    //     medicinesData.forEach(medicine => {
    //         const option = document.createElement('option');
    //         option.value = medicine.id;
    //         option.textContent = medicine.name;
    //         medicineSelect.appendChild(option);
    //     });

    //     medicineSelectGroup.appendChild(medicineLabel);
    //     medicineSelectGroup.appendChild(medicineSelect);

    //     const quantityGroup = document.createElement('div');
    //     quantityGroup.classList.add('form-group');
    //     const quantityLabel = document.createElement('label');
    //     quantityLabel.setAttribute('for', `quantity_${index}`);
    //     quantityLabel.textContent = medicinesSection.getAttribute('quantity-name');
    //     const quantityInput = document.createElement('input');
    //     quantityInput.setAttribute('type', 'number');
    //     quantityInput.setAttribute('name', `quantities`);
    //     quantityInput.setAttribute('id', `quantity_${index}`);
    //     quantityInput.setAttribute('required', true);

    //     quantityGroup.appendChild(quantityLabel);
    //     quantityGroup.appendChild(quantityInput);

    //     medicineItem.appendChild(medicineSelectGroup);
    //     medicineItem.appendChild(quantityGroup);
    //     medicinesSection.appendChild(medicineItem);
    // }

    
    
    // Show modal for editing a prescription
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

                    // Populate medicines section
                    data.medicines.forEach((medicine, index) => {
                        addMedicineField(index + 1, medicine.id, medicine.quantity);
                    });
                })
                .catch(error => console.error('Error fetching prescription:', error));
        });
    });
    function addMedicineField(index, selectedMedicineId = "", quantity = "") {
        const medicineItem = document.createElement('div');
        medicineItem.classList.add('medicine-item');

        const medicineSelectGroup = document.createElement('div');
        medicineSelectGroup.classList.add('form-group');

        const medicineLabel = document.createElement('label');
        medicineLabel.setAttribute('for', `medicine_${index}`);
        medicineLabel.textContent = medicinesSection.getAttribute('medicine-name');;

        const medicineSelect = document.createElement('select');
        medicineSelect.setAttribute('name', `medicine_ids`);
        medicineSelect.setAttribute('id', `medicine_${index}`);
        medicineSelect.required = true;

        // Populate the dropdown with available medicines
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
        quantityLabel.setAttribute('for', `quantity_${index}`);
        quantityLabel.textContent = medicinesSection.getAttribute('quantity-name');;

        const quantityInput = document.createElement('input');
        quantityInput.setAttribute('type', 'number');
        quantityInput.setAttribute('name', `quantities`);
        quantityInput.setAttribute('id', `quantity_${index}`);
        quantityInput.setAttribute('value', quantity);
        quantityInput.required = true;

        quantityGroup.appendChild(quantityLabel);
        quantityGroup.appendChild(quantityInput);

        medicineItem.appendChild(medicineSelectGroup);
        medicineItem.appendChild(quantityGroup);

        medicinesSection.appendChild(medicineItem);
    }
});
