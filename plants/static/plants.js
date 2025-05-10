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

    function setModalVisibility(triggerId, modalId, displayValue) {
        const trigger = document.getElementById(triggerId);
        const modal = document.getElementById(modalId);
        if (trigger && modal) {
            trigger.addEventListener('click', () => {
                modal.style.display = displayValue;
            });
        }
    }
    setModalVisibility('openModal', 'eventModal', 'flex');
    setModalVisibility('closeModal', 'eventModal', 'none');
    setModalVisibility('openWateringModal', 'wateringModal', 'flex');
    setModalVisibility('wateringCloseModal', 'wateringModal', 'none');


    const sendForm = (url, data, callback) => {
        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json'
            },
            body: data
        })
        .then(res => res.json())
        .then(callback)
        .catch(err => alert("Network error"));
    };

    const handleButtonClick = (selector, dataObject, url) => {
        document.querySelectorAll(selector).forEach(button => {
            button.addEventListener("click", function () {
                const event_data = dataObject(this);
                console.log(event_data)
                if (!getCSRFToken()) return;
                sendForm(url, JSON.stringify(event_data), data => {
                    if (data.success) location.reload();
                    else alert("Error: " + data.error);
                });
                console.log('after')
            });
        });
    };

    // Obsługa wysyłki formularza - Dodawanie eventu
    const eventForm = document.getElementById('eventForm');
    if (eventForm) {
        eventForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const form = e.target;
            const formData = new FormData(form);
            const url = this.dataset.url;

            sendForm(url,formData,data => {
                if (data.success) {
                    alert('Event added!');
                    location.reload();
                } else {
                    alert('Błąd: ' + data.errors.join(', '));
                }
            });
        });
    }

    // finish-event on calendar
    const finishEvent = document.querySelectorAll('.finish-event')
    if(finishEvent) {
        handleButtonClick('.finish-event', btn => ({event_id: btn.dataset.eventId}), "/finish-event/");
    }
    const cancelEvent = document.querySelectorAll('.cancel-event')
    if(cancelEvent) {
        handleButtonClick('.cancel-event', btn => ({event_id: btn.dataset.eventId}), "/cancel-event/");
    }
    const wishlistRemove = document.querySelectorAll('.wishlist-remove')
    if(wishlistRemove) {
        handleButtonClick('.wishlist-remove', btn => ({ plant_id: btn.dataset.plantId, owner_id: btn.dataset.ownerId }), "/wishlist-remove/");
    }

    const wishlistBought = document.querySelectorAll('.wishlist-bought')
    if(wishlistBought) {
        handleButtonClick('.wishlist-bought', btn => ({ plant_id: btn.dataset.plantId }), "/wishlist-bought/");
    }

    // watering form
    const wateringForm = document.getElementById('wateringForm');
    if (wateringForm) {
        wateringForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const form = e.target;
            const formData = new FormData(form);
            sendForm("{% url 'add-watering' %}",formData,data => {
                if (data.success) location.reload();
                else alert("Error: " + data.errors.join(', '));
            });
        });
    }
    const addDay = document.querySelectorAll('.add-day')
    if(addDay) {
        handleButtonClick('.add-day', btn => ({watering_id: btn.dataset.wateringId, days: btn.dataset.days }), "/move-watering/");
    }

    const wateringDone = document.querySelectorAll('.watering-done')
    if(wateringDone) {
        handleButtonClick('.watering-done', btn => ({watering_id: btn.dataset.wateringId, fertilizer: btn.dataset.fertilizer }), "/finish-watering/");
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
            sendForm(url,formData,data => {
                if (data.diagnosis) alert("Diagnosis:\n" + data.diagnosis);
                else if (data.error) alert("Error:\n" + data.error);
                else alert("Failed to get answer.");
                const modal = document.getElementById('diagnoseModal');
                if (modal) modal.style.display = 'none';
                diagnoseForm.reset();
                location.reload();
            });
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

            sendForm(url,JSON.stringify({ plant_id: plantId, user_id: userId, note: note }),data => {
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

            sendForm('change-watering-frequency',JSON.stringify({ plant_id: plantId, owner_id: ownerId, frequency: frequency }),data => {
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

                sendForm(addUrl,JSON.stringify({ owner_id: ownerId, plant_id: plantId }),data => {
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

                sendForm(removeUrl,JSON.stringify({ plant_id: plantId, owner_id: ownerId }),data => {
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
