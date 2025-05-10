document.addEventListener("DOMContentLoaded", function() {
    function getCSRFToken() {
        const name = 'csrftoken';
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                return decodeURIComponent(cookie.substring(name.length + 1));
            }
        }
        return null;
    }

    // Formularz dodawania eventu
    const openModalBtn = document.getElementById('openModal');
    if (openModalBtn) {
        openModalBtn.addEventListener('click', function () {
            const modal = document.getElementById('eventModal');
            if (modal) {
                modal.style.display = 'flex';
            }
        });
    }
    // Zamykanie formularza dodawania eventu
    const closeModalBtn = document.getElementById('closeModal');
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', function () {
            const modal = document.getElementById('eventModal');
            if (modal) {
                modal.style.display = 'none';
            }
        });
    }


    // Obsługa wysyłki formularza
    // Dodawanie eventu
    const eventForm = document.getElementById('eventForm');
    if (eventForm) {
        eventForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const form = e.target;
            const formData = new FormData(form);
            const url = this.dataset.url;

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken()
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Event added!');
                    location.reload();
                } else {
                    alert('Błąd: ' + data.errors.join(', '));
                }
            })
            .catch(error => {
                console.error(error);
                alert('Wystąpił błąd.');
            });
        });
    }
    const sendForm = (url, data, callback) => {
        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(callback)
        .catch(err => alert("Network error"));
    };
    // finish-event on calendar
    const finishEvent = document.querySelectorAll('.finish-event')

    if(finishEvent){
        finishEvent.forEach(button => {
            button.addEventListener('click', function () {
                const eventId = this.dataset.eventId;
                const csrfToken = getCSRFToken();
                if (!csrfToken) return;

                sendForm('/finish-event/',{event_id: eventId},data => {
                    if (data.success) location.reload();
                    else alert("Error: " + data.error);
                });
            });
        });
    }

    // cancel-event on dashboard
    const cancelEvent = document.querySelectorAll('.cancel-event')
    if(cancelEvent){

        cancelEvent.forEach(button => {
            button.addEventListener('click', function () {
                const eventId = this.dataset.eventId;
                const csrfToken = getCSRFToken();
                if (!csrfToken) return;

                sendForm('/cancel-event/',{event_id: eventId},data => {
                    if (data.success) location.reload();
                    else alert("Error: " + data.error);
                });
            });
        });
    }

    // wishlist remove on dashboard
    const wishlistRemove = document.querySelectorAll('.wishlist-remove')
    if(wishlistRemove){
        wishlistRemove.forEach(button => {
            button.addEventListener('click', function () {
                const { plantId, ownerId } = this.dataset;
                const csrfToken = getCSRFToken();
                if (!csrfToken) return;

                sendForm('/wishlist-remove/',{ plant_id: plantId, owner_id: ownerId },data => {
                    if (data.success) location.reload();
                    else alert("Error: " + data.error);
                });
            });
        });
    }

    // wishlist bought on dashboard
    const wishlistBought = document.querySelectorAll('.wishlist-bought')
    if(wishlistBought){
        wishlistBought.forEach(button => {
            button.addEventListener('click', function () {
                const plantId = this.dataset.plantId;
                const csrfToken = getCSRFToken();
                if (!csrfToken) return;

                sendForm('/wishlist-bought/',{ plant_id: plantId },data => {
                    if (data.success) location.reload();
                    else alert("Error: " + data.error);
                });
            });
        });
    }

    // modal watering
    const openWatering = document.getElementById('openWateringModal');
    const closeWatering = document.getElementById('wateringCloseModal');
    const wateringModal = document.getElementById('wateringModal');

    if (openWatering && wateringModal) {
        openWatering.addEventListener('click', () => wateringModal.style.display = 'flex');
    }
    if (closeWatering && wateringModal) {
        closeWatering.addEventListener('click', () => wateringModal.style.display = 'none');
    }

    // watering form
    const wateringForm = document.getElementById('wateringForm');
    if (wateringForm) {
        wateringForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const form = e.target;
            const formData = new FormData(form);
            fetch("{% url 'add-watering' %}", {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken()
                },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) location.reload();
                else alert("Error: " + data.errors.join(', '));
            })
            .catch(err => alert("Error occured."));
        });
    }

    // change watering date
    const addDay = document.querySelectorAll('.add-day')
    if(addDay){
        addDay.forEach(button => {
            button.addEventListener('click', function () {
                const { wateringId, days } = this.dataset;
                const csrfToken = getCSRFToken();
                if (!csrfToken) return;

                sendForm('/move-watering/',{ watering_id: wateringId, days: days },data => {
                    if (data.success) location.reload();
                    else alert("Error: " + data.error);
                });
            });
        });
    }

    // watering done
    const wateringDone = document.querySelectorAll('.watering-done')
    if(wateringDone){
        wateringDone.forEach(button => {
            button.addEventListener('click', function () {
                const { wateringId, fertilizer } = this.dataset;
                const csrfToken = getCSRFToken();
                if (!csrfToken) return;
                sendForm('/finish-watering/',{ watering_id: wateringId, fertilizer: fertilizer },data => {
                    if (data.success) location.reload();
                    else alert("Error: " + data.error);
                });
            });
        });
    }

    // diagnose modal visibility
    const diagnoseBtn = document.querySelectorAll('.diagnose-btn')
    if(diagnoseBtn){
        diagnoseBtn.forEach(button => {
            button.addEventListener('click', function () {
                const plantId = this.dataset.plantId;
                const plantInput = document.getElementById('plantIdInput');
                const modal = document.getElementById('diagnoseModal');
                if (plantInput && modal) {
                    plantInput.value = plantId;
                    modal.style.display = 'block';
                }
            });
        });
    }

    // diagnose form
    const diagnoseForm = document.getElementById('diagnoseForm');
    if (diagnoseForm) {
        diagnoseForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const formData = new FormData(this);
            const csrfToken = getCSRFToken();
            const url = this.dataset.url;
            if (!csrfToken) return;
            fetch(url, {
                method: "POST",
                headers: { "X-CSRFToken": csrfToken },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.diagnosis) alert("Diagnosis:\n" + data.diagnosis);
                else if (data.error) alert("Error:\n" + data.error);
                else alert("Failed to get answer.");
                const modal = document.getElementById('diagnoseModal');
                if (modal) modal.style.display = 'none';
                diagnoseForm.reset();
                location.reload();
            })
            .catch(err => alert("Network error"));
        });
    }
    // note form post
    const noteForm = document.getElementById("note-form");
    if (noteForm) {
        noteForm.addEventListener("submit", function (e) {
            e.preventDefault();
            const note = this.querySelector("textarea[name=note]").value;
            const plantId = this.querySelector("input[name=plant_id]").value;
            const userId = this.querySelector("input[name=user_id]").value;
            const csrfToken = getCSRFToken();
            const url = this.dataset.url;
            console.log(url)
            if (!csrfToken) return;

            sendForm(url,{ plant_id: plantId, user_id: userId, note: note },data => {
                if (data.success) location.reload();
                else alert("Error: " + data.error);
            });
        });
    }
    // watering frequency form post
    const freqForm = document.getElementById("watering-frequency-form");
    if (freqForm) {
        freqForm.addEventListener("submit", function (e) {
            e.preventDefault();
            const plantId = this.querySelector("input[name=plant_id]").value;
            const ownerId = this.querySelector("input[name=owner_id]").value;
            const frequency = this.querySelector("input[name=frequency]").value;
            const csrfToken = getCSRFToken()
            if (!csrfToken) return;

            sendForm('change-watering-frequency',{ plant_id: plantId, owner_id: ownerId, frequency: frequency },data => {
                if (data.success) location.reload();
                else alert("Error: " + data.error);
            });
        });
    }
    //dodawanie do wishlisty przez katalog
    const toWishlistIcons = document.querySelectorAll('.to-wishlist');
    if (toWishlistIcons.length) {
        toWishlistIcons.forEach(icon => {
            icon.addEventListener('click', function(e) {
                e.preventDefault();

                const plantId = this.dataset.plantId;
                const ownerId = this.dataset.userId;
                const addUrl = this.dataset.addUrl

                sendForm(addUrl,{ owner_id: ownerId, plant_id: plantId },data => {
                    if (data.success) {
                        this.classList.add('hidden');
                        this.nextElementSibling.classList.remove('hidden');
                        location.reload();
                    } else if (data.error) {
                        alert("Error:\n" + data.error);
                    }
                });
            });
        });
    }
    //usuwanie z wishlisty przez katalog
    const wishlistedIcons = document.querySelectorAll('.wishlisted');
    if (wishlistedIcons) {
        wishlistedIcons.forEach(icon => {
            icon.addEventListener('click', function(e) {
                e.preventDefault();

                const plantId = this.dataset.plantId;
                const ownerId = this.dataset.userId;
                const removeUrl = this.dataset.removeUrl

                sendForm(removeUrl,{ plant_id: plantId, owner_id: ownerId },data => {
                    if (data.success) {
                        this.classList.add('hidden');
                        this.previousElementSibling.classList.remove('hidden');
                        location.reload();
                    } else if (data.error) {
                        alert("Error:\n" + data.error);
                    }
                });
            });
        });
    }
    //dodawanie komentarza w plant-detail
    const commentForm = document.getElementById("comment-form");
    if (commentForm) {
        commentForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const plantId = this.querySelector("input[name=plant_id]").value;
            const userId = this.querySelector("input[name=user_id]").value;
            const comment = this.querySelector("textarea[name=comment]").value;
            const csrfToken = getCSRFToken();
            console.log(csrfToken)

            const formUrl = commentForm.dataset.url;

            fetch(formUrl, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    plant_id: plantId,
                    user_id: userId,
                    comment: comment
                })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    } else {
                        alert("Error: " + data.error);
                    }
                })
                .catch(async(error) => {
                    console.error(error);
                    const text = await error.text?.();
                    console.error('Network error:', error);
                    console.log('Response text:', text);
                    alert("Network error:\n" + text);
                    alert("Network error");
                });
        });
    }
    const buttonAiForm=document.getElementById("fileInput")
    if (buttonAiForm){
        buttonAiForm.addEventListener("change", function () {
            const fileName = this.files[0]?.name || "No file selected";
            document.getElementById("fileName").textContent = fileName;
        });
    }
});
