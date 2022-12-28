function deleteArrival(id, url, post_data) {
    Swal.fire({
        title: `Czy na pewno chcesz usunąć przylot z ID: ${id}?`,
        text: "Usunięcie przylotu usunie również odpowiadające mu rezerwacje pasów!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Tak, usuń!',
        cancelButtonText: "Powrót"
    }).then((result) => {
        if (result.isConfirmed) {
            post(url, post_data)
        }
    })
}


function addArrival(url) {
    let html = `<form id="check-availability-form" action="" method="post" novalidate class="needs-validation">
                    <div class="p-2">
                        <input disabled type="text" id="date-picker-check" name="date" class="form-control"
                                       placeholder="Wybierz termin przylotu...">
                    </div>
                </form>`
    Swal.fire({
        title: "Wybierz termin przylotu",
        html: html,
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Dalej...',
        cancelButtonText: 'Powrót',
        willOpen: () => {
            flatpickr("#date-picker-check", {
                enableTime: true,
                dateFormat: "Y-m-d H:i",
                time_24hr: true,
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