function selectReservationDates(url) {
    let html = `<form id="check-availability-form" action="" method="post" novalidate class="needs-validation">
                    <div class="p-2">
                        <input disabled type="text" id="date-picker-check" name="date" class="form-control"
                                       placeholder="Wybierz termin rezerwacji...">
                    </div>
                </form>`
    Swal.fire({
        title: "Wybierz termin rezerwacji",
        html: html,
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Dalej...',
        cancelButtonText: 'Powrót',
        willOpen: () => {
            flatpickr("#date-picker-check", {
                mode: "range",
                enableTime: true,
                time_24hr: true,
                dateFormat: "Y-m-d H:i",
            })
        },
        didOpen: () => {
            document.getElementById('date-picker-check').removeAttribute('disabled')
        }
    }).then((result) => {
        if (result.isConfirmed) {
            let dt = document.getElementById('date-picker-check').value
            if (dt !== "") {
                post(url, {timestamp: dt})
            }
        }
    })
}

function updateReservationDates(url) {
    let html = `<form id="check-availability-form" action="" method="post" novalidate class="needs-validation">
                    <div class="p-2">
                        <input disabled type="text" id="date-picker-check" name="date" class="form-control"
                                       placeholder="Wybierz nowy termin rezerwacji...">
                    </div>
                </form>`
    Swal.fire({
        title: "Wybierz nowy termin rezerwacji",
        html: html,
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Dalej...',
        cancelButtonText: 'Powrót',
        willOpen: () => {
            flatpickr("#date-picker-check", {
                mode: "range",
                enableTime: true,
                time_24hr: true,
                dateFormat: "Y-m-d H:i",
            })
        },
        didOpen: () => {
            document.getElementById('date-picker-check').removeAttribute('disabled')
        }
    }).then((result) => {
        if (result.isConfirmed) {
            let dt = document.getElementById('date-picker-check').value
            if (dt !== "") {
                post(url, {dates: dt})
            }
        }
    })
}