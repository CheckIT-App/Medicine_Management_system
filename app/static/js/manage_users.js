document.addEventListener('DOMContentLoaded', () => {
    const htmlTag = document.documentElement;
    const userModal = document.getElementById('user-modal');
    const addUserBtn = document.getElementById('add-user-btn');
    const form = document.getElementById('user-form');
    const modalTitle = document.getElementById('modal-title');
    const userIdInput = document.getElementById('user_id');
    const closeModal = document.getElementById("close-edit-modal");
    const lang = htmlTag.lang || 'he';

    // Close modal on 'x' button or cancel
    closeModal.addEventListener("click", () => {
        userModal.classList.add("hidden");
    });
    // Show modal for adding a user
    addUserBtn.addEventListener('click', () => {
        modalTitle.textContent = "Add User";
        form.reset(); // Clear previous inputs
        userIdInput.value = 0; // Ensure no user_id is set
        userModal.classList.remove('hidden');
    });

    // Show modal for editing a user
    document.querySelectorAll('.edit-button').forEach(button => {
        button.addEventListener('click', (event) => {
            const userId = event.target.dataset.userId;
            modalTitle.textContent = "Edit User";
            userModal.classList.remove('hidden');

            fetch(`/${lang}/management/users/${userId}`)
                .then(response => response.json())
                .then(data => {
                    userIdInput.value = data.id;
                    document.getElementById('username').value = data.username;
                    document.getElementById('first_name').value = data.first_name;
                    document.getElementById('last_name').value = data.last_name;
                    document.getElementById('identity_number').value = data.identity_number;
                    document.getElementById('email').value = data.email;
                    document.getElementById('role_id').value = data.role_id;
                })
                .catch(error => console.error('Error fetching user:', error));
        });
    });

    // Delete user with confirmation modal handled by `modal_handler.js`
    document.querySelectorAll('.delete-button').forEach(button => {
        button.addEventListener('click', () => {
            const userId = button.getAttribute('data-user-id');
            const username = button.closest('li').querySelector('.item-name').textContent;

            // Assuming `showConfirmationModal` is now defined in `modal_handler.js`
            showConfirmationModal('delete', username, { userId }, payload => {
                deleteUser(payload.userId);
            });
        });
    });

    function deleteUser(userId) {
        fetch(`/${lang}/management/users/${userId}`, { method: 'DELETE' })
            .then(response => {
                if (response.ok) {
                    const userItem = document.querySelector(`.delete-button[data-user-id="${userId}"]`).closest('li');
                    userItem.remove();
                } else {
                    alert('Failed to delete user.');
                }
            })
            .catch(error => {
                console.error('Error deleting user:', error);
                alert('Failed to delete user.');
            });
    }

    });
