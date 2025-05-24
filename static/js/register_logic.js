document.addEventListener('DOMContentLoaded', () => {
    // Existing dropdown for evakuert status
    const dropdownButton = document.getElementById("evak_status");
    const dropdownMenu = document.getElementById("dropdownMenu");

    if (dropdownButton && dropdownMenu) {
        const dropdownOptions = dropdownMenu.querySelectorAll("li");
        dropdownButton.addEventListener("click", () => {
            dropdownMenu.classList.toggle("hidden");
        });

        document.addEventListener("click", (event) => {
            if (!dropdownButton.contains(event.target) && !dropdownMenu.contains(event.target)) {
                dropdownMenu.classList.add("hidden");
            }
        });

        dropdownOptions.forEach((option) => {
            option.addEventListener("click", () => {
                const colorClass = option.getAttribute("data-color");
                const colorName = option.textContent.trim(); // trim to be safe

                dropdownButton.className = `h-12 w-48 px-4 py-2 text-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 transition ${colorClass}`;
                dropdownButton.textContent = colorName;

                const selectedStatusInput = document.getElementById("selected-status");
                if (selectedStatusInput) {
                    selectedStatusInput.value = colorName;
                }
                dropdownMenu.classList.add("hidden");
            });
        });
    }

    // Krise status dropdown code (for the removed incident status dropdown)
    const kriseDropdownButton = document.getElementById("krise-status"); // This element was removed
    const kriseDropdownMenu = document.getElementById("kriseDropdownMenu"); // This element was removed

    if (kriseDropdownButton && kriseDropdownMenu) { // Will likely not run as elements are removed
        const kriseDropdownOptions = kriseDropdownMenu.querySelectorAll("li");
        kriseDropdownButton.addEventListener("click", () => {
            kriseDropdownMenu.classList.toggle("hidden");
        });

        document.addEventListener("click", (event) => {
            if (!kriseDropdownButton.contains(event.target) && !kriseDropdownMenu.contains(event.target)) {
                kriseDropdownMenu.classList.add("hidden");
            }
        });

        kriseDropdownOptions.forEach((option) => {
            option.addEventListener("click", () => {
                const selectedValue = option.getAttribute("data-value");
                kriseDropdownButton.textContent = selectedValue;
                const selectedKriseStatusInput = document.getElementById("selected-krise-status"); // Element removed
                if (selectedKriseStatusInput) {
                    selectedKriseStatusInput.value = selectedValue;
                }
                kriseDropdownMenu.classList.add("hidden");
            });
        });
    }

    // New dropdown for Krise navn
    const kriseNavnDropdownButton = document.getElementById("krise-navn-dropdown");
    const kriseNavnMenu = document.getElementById("krise-navn-menu");

    if (kriseNavnDropdownButton && kriseNavnMenu) {
        const kriseNavnOptions = kriseNavnMenu.querySelectorAll("li");

        kriseNavnDropdownButton.addEventListener("click", () => {
            kriseNavnMenu.classList.toggle("hidden");
        });

        document.addEventListener("click", (event) => {
            if (!kriseNavnDropdownButton.contains(event.target) && !kriseNavnMenu.contains(event.target)) {
                kriseNavnMenu.classList.add("hidden");
            }
        });

        kriseNavnOptions.forEach((option) => {
            option.addEventListener("click", () => {
                const selectedId = option.getAttribute("data-id");
                const selectedName = option.getAttribute("data-name");

                kriseNavnDropdownButton.textContent = selectedName;
                const kriseIdInput = document.getElementById("krise_id");
                if (kriseIdInput) {
                    kriseIdInput.value = selectedId;
                }
                const kriseNavnInput = document.getElementById("krise-navn");
                if (kriseNavnInput) {
                    kriseNavnInput.value = selectedName;
                }
                kriseNavnMenu.classList.add("hidden");

                // The fetch call is okay to keep, but the part that updates removed DOM elements needs to be removed.
                fetch(`/admin-reg/get_krise_details/${selectedId}`)
                    .then((response) => response.json())
                    .then((data) => {
                        if (!data.error) {
                            // document.getElementById("krise-type").value = data.KriseSituasjonType; // Element removed
                            // document.getElementById("krise-lokasjon").value = data.Lokasjon; // Element removed
                            // const annenInfoInput = document.getElementById("annen-info"); // Element might exist, but was for Krise
                            // if(annenInfoInput) annenInfoInput.value = data.Tekstboks;

                            // Hidden fields for these were also tied to the removed incident component fields
                            // document.getElementById("hidden-krise-type").value = data.KriseSituasjonType; // Element removed
                            // document.getElementById("hidden-krise-lokasjon").value = data.Lokasjon; // Element removed
                            // document.getElementById("hidden-annen-info").value = data.Tekstboks; // Element removed

                            // Update old Krise status button/input - these are also removed
                            // if (kriseDropdownButton) kriseDropdownButton.textContent = data.Status; // kriseDropdownButton is the old incident status button
                            // const selectedKriseStatusInput = document.getElementById("selected-krise-status");
                            // if (selectedKriseStatusInput) selectedKriseStatusInput.value = data.Status;
                        } else {
                            console.error("Error from get_krise_details:", data.error);
                        }
                    })
                    .catch((err) => console.error("Error fetching crisis details:", err));
            });
        });
    }

    // Form submission logic for confirmation modal
    const form = document.querySelector('form');
    const modal = document.getElementById('confirmationModal');
    const confirmationContent = document.getElementById('confirmationContent');
    const cancelButton = document.getElementById('cancelButton');
    const confirmButton = document.getElementById('confirmButton');

    if (form && modal && confirmationContent && cancelButton && confirmButton) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const fieldLabels = {
                'evak-fnavn': 'Evakuert Fornavn',
                'evak-mnavn': 'Evakuert Mellomnavn',
                'evak-enavn': 'Evakuert Etternavn',
                'evak-tlf': 'Evakuert Telefonnummer',
                'evak-adresse': 'Evakuert Adresse',
                'status': 'Evakuert Status', // Added based on evacuee_component selected-status which is named status
                'evak-lokasjon': 'Evakuert Lokasjon',
                'krise-navn': 'Krise Navn', // Added, as this is selected
                'kon-fnavn': 'Pårørende Fornavn',
                'kon-mnavn': 'Pårørende Mellomnavn',
                'kon-enavn': 'Pårørende Etternavn',
                'kon-tlf': 'Pårørende Telefonnummer',
            };
            const formData = new FormData(form);
            let contentHTML = '';
            const ignoreKeys = new Set([
                'evakuert_id',
                'kontakt_person_id',
                'status_id',
                'krise_id', // This is shown via 'krise-navn'
                // Removed fields that are no longer in the incident component or should not be shown directly
                // 'krise-status', 'krise-type', 'krise-lokasjon', 'annen-info'
            ]);

            for (const [key, value] of formData.entries()) {
                if (!ignoreKeys.has(key) && value) { // Also check if value is not empty
                    const fieldName = fieldLabels[key] || key;
                    contentHTML += `<p><strong>${fieldName}:</strong> ${value}</p>`;
                }
            }
            confirmationContent.innerHTML = contentHTML;
            modal.classList.remove('hidden');
        });

        cancelButton.addEventListener('click', () => {
            modal.classList.add('hidden');
        });

        confirmButton.addEventListener('click', () => {
            // modal.classList.add('hidden'); // Keep modal open until submission is successful or explicitly closed
            form.submit(); // This will now submit the form directly
        });
    }

    // Removed the specific submit listener for "selected-krise-status" as the element is gone.
    // The evacuee "selected-status" (name="status") is handled by its own input field value updates.
    // The krise_id and krise-navn are also handled by their respective hidden input updates.
});
