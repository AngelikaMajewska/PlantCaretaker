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


    const sendRequest= (url, data, callback) => {
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
                sendRequest(url, JSON.stringify(event_data), data => {
                    if (data.success) location.reload();
                    else alert("Error: " + data.error);
                });
                console.log('after')
            });
        });
    };

    // finish-event on calendar
    const finishEvent = document.querySelectorAll('.finish-event')
    if(finishEvent) {
        handleButtonClick('.finish-event', btn => ({event_id: btn.dataset.eventId}), "/finish-event/");
    }
    // cancel-event on calendar
    const cancelEvent = document.querySelectorAll('.cancel-event')
    if(cancelEvent) {
        handleButtonClick('.cancel-event', btn => ({event_id: btn.dataset.eventId}), "/cancel-event/");
    }
    //removing from wishlist through dashboard
    const wishlistRemove = document.querySelectorAll('.wishlist-remove')
    if(wishlistRemove) {
        handleButtonClick('.wishlist-remove', btn => ({ plant_id: btn.dataset.plantId, owner_id: btn.dataset.ownerId }), "/wishlist-remove/");
    }
    //marking as acquired through dashboard
    const wishlistBought = document.querySelectorAll('.wishlist-bought')
    if(wishlistBought) {
        handleButtonClick('.wishlist-bought', btn => ({ plant_id: btn.dataset.plantId }), "/wishlist-bought/");
    }
    //adding to wishlist through catalh
    const toWishlistIcons = document.querySelectorAll('.to-wishlist');
    if(toWishlistIcons) {
        handleButtonClick('.to-wishlist', btn => ({owner_id: btn.dataset.userId, plant_id: btn.dataset.plantId }), "/add-to-wishlist/");
    }
    //removing from wishlist through catalog
    const wishlistedIcons = document.querySelectorAll('.wishlisted');
    if(wishlistedIcons) {
        handleButtonClick('.wishlisted', btn => ({owner_id: btn.dataset.userId, plant_id: btn.dataset.plantId }), "/remove-from-wishlist/");
    }
    // changing next watering date by +-1 day
    const addDay = document.querySelectorAll('.add-day')
    if(addDay) {
        handleButtonClick('.add-day', btn => ({watering_id: btn.dataset.wateringId, days: btn.dataset.days, plant_id: btn.dataset.plantId }), "/move-watering/");
    }
    // marking watering as done(with and without fertilizer)
    const wateringDone = document.querySelectorAll('.watering-done')
    if(wateringDone) {
        handleButtonClick('.watering-done', btn => ({watering_id: btn.dataset.wateringId, fertilizer: btn.dataset.fertilizer }), "/finish-watering/");
    }

    const sendForm = (url, data, callback) => {
        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
            },
            body: data
        })
        .then(res => res.json())
        .then(callback)
        .catch(err => alert("Network error"));
    };

    const handleFormSubmit = (formId, getData) => {
        const form = document.getElementById(formId);
        if (form) {
            form.addEventListener("submit", function (e) {
                e.preventDefault();
                const url = this.dataset.url || form.action;
                const form_data = getData(this);
                sendForm(url, form_data, data => {
                    if (data.success) {
                        location.reload();
                    } else {
                        alert("Error: " + (data.error || data.errors?.join(", ")));
                    }
                });
            });
        }
    };

    // adding event in the calendar
    const eventForm = document.getElementById('eventForm');
    if (eventForm) {
        handleFormSubmit('eventForm',form => new FormData(form))
    }

    // watering form
    const wateringForm = document.getElementById('wateringForm');
    if (wateringForm) {
        handleFormSubmit('wateringForm',form => new FormData(form))
    }
    // owned plant note form post
    const noteForm = document.getElementById("note-form");
    if (noteForm) {
        handleFormSubmit('note-form',form => new FormData(form))
    }

    // watering frequency caenge form post
    const freqForm = document.getElementById("watering-frequency-form");
    if (freqForm) {
        handleFormSubmit('watering-frequency-form',form => new FormData(form))
    }
    // AI diagnose modal visibility
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

    // AI diagnose form
    const diagnoseForm = document.getElementById('diagnoseForm');
    if (diagnoseForm) {
        diagnoseForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const formData = new FormData(this);
            const csrfToken = getCSRFToken();
            const url = this.dataset.url;
            if (!csrfToken) return;
            sendForm(url,formData,data => {
                if (data.diagnosis) alert("Rating:"+ data.diagnosis.rating +"\nDiagnosis:\n" + data.diagnosis.note);
                else if (data.error) alert("Error:\n" + data.error);
                else alert("Failed to get answer.");
                const modal = document.getElementById('diagnoseModal');
                if (modal) modal.style.display = 'none';
                diagnoseForm.reset();
                location.reload();
            });
        });
    }


    //adding comment in plant-detail
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
    //showing chosen file name in owned plant diagnosis form box
    const buttonAiForm=document.getElementById("fileInput")
    if (buttonAiForm){
        buttonAiForm.addEventListener("change", function () {
            const fileName = this.files[0]?.name || "No file selected";
            document.getElementById("fileName").textContent = fileName;
        });
    }
    const fileInput = document.getElementById('id_image');
    const fileNameSpan = document.getElementById('file-name');
    if(fileInput && fileNameSpan)
    {
       fileInput.addEventListener('change', function () {
          fileNameSpan.textContent = this.files.length > 0 ? this.files[0].name : 'No file chosen';
       });
    }
});
