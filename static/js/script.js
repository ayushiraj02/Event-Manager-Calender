document.addEventListener('DOMContentLoaded', () => {
    const selectedDates = new Set();  
    const dayElements = document.querySelectorAll('.day');

    dayElements.forEach(day => {
        day.addEventListener('click', (e) => {
            if (e.target.tagName === 'A') {
                e.preventDefault();  
            }

            const date = day.getAttribute('data-date');
            if (!date) return;

            if (selectedDates.has(date)) {
                selectedDates.delete(date);
                day.classList.remove('selected');
            } else {
                selectedDates.add(date);
                day.classList.add('selected');
            }

            document.getElementById('selectedDates').value = Array.from(selectedDates).join(',');
        });
    });

    // --- Modal related ---

    const editButtons = document.querySelectorAll('.edit-btn');
    const deleteButtons = document.querySelectorAll('.delete-btn');
    const modal = $('#editEventModal');
    const modalTitleInput = document.getElementById('modalTitle');
    const modalCategorySelect = document.getElementById('modalCategory');
    const modalDatesDiv = document.getElementById('modalDates');
    // const modalEventIndexInput = document.getElementById('modalEventIndex');
    const modalEventIndexInput = document.getElementById('modalEventId');


    // Pass events data from Flask via a JS variable
    

    editButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            
            const idx = btn.getAttribute('data-event-index');
            console.log('Edit button clicked for index:', idx);


            const event = events[idx];
            console.log('Event data:', event);


            modalEventIndexInput.value = idx;
            modalTitleInput.value = event.title;
            modalCategorySelect.value = event.category;
            modalDatesDiv.innerHTML = event.dates.map(d => (new Date(d)).toLocaleDateString()).join(', ');

            modal.modal('show');
        });
    });

    deleteButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const idx = btn.getAttribute('data-event-index');
            if (confirm('Are you sure you want to delete this event?')) {
                fetch(`/delete_event/${idx}`, { method: 'POST' })
                .then(() => window.location.reload());
            }
        });
    });

    // Cancel buttons close modal
    document.getElementById('modalCancelBtn').addEventListener('click', () => modal.modal('hide'));
    document.getElementById('modalCancelBtn2').addEventListener('click', () => modal.modal('hide'));

});

