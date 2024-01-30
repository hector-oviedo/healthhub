class HabitModal {
    constructor(title, contentHTML) {
        this.modalId = 'habitModal';
        this.title = title;
        this.contentHTML = contentHTML;
    }

    createModal() {
        // Remove existing modal
        const existingModal = document.getElementById(this.modalId);
        if (existingModal) existingModal.remove();

        // Create modal structure
        const modal = document.createElement('div');
        modal.id = this.modalId;
        modal.className = 'modal fade';
        modal.setAttribute('tabindex', '-1');
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${this.title}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div id="modal-body" class="modal-body">
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        document.getElementById("modal-body").appendChild(this.contentHTML)

        // Initialize the modal
        return new bootstrap.Modal(document.getElementById(this.modalId));
    }

    openModal() {
        const modalInstance = this.createModal();
        modalInstance.show();
    }

    closeModal() {
        const modalInstance = bootstrap.Modal.getInstance(document.getElementById(this.modalId));
        modalInstance.hide();
    }
}