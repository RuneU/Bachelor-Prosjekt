// Existing dropdown for evakuert status
const dropdownButton = document.getElementById("evak_status");
const dropdownMenu = document.getElementById("dropdownMenu");
const dropdownOptions = dropdownMenu.querySelectorAll("li");

document.querySelector("form").addEventListener("submit", function () {
  document.getElementById("selected-status").value =
    dropdownButton.textContent.trim();
  document.getElementById("selected-krise-status").value =
    kriseDropdownButton.textContent.trim();
});

dropdownButton.addEventListener("click", () => {
  dropdownMenu.classList.toggle("hidden");
});

document.addEventListener("click", (event) => {
  if (
    !dropdownButton.contains(event.target) &&
    !dropdownMenu.contains(event.target)
  ) {
    dropdownMenu.classList.add("hidden");
  }
});

dropdownOptions.forEach((option) => {
	option.addEventListener("click", () => {
	  const colorClass = option.getAttribute("data-color");
	  const colorName = option.textContent;
  
	  // Update the button background color and text
	  dropdownButton.className = `h-12 w-48 px-4 py-2 text-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 transition ${colorClass}`;
	  dropdownButton.textContent = colorName;
  
	  // Update the hidden input's value with the selected status text
	  document.getElementById("selected-status").value = colorName;
  
	  dropdownMenu.classList.add("hidden");
	});
  });

// Krise status dropdown code (unchanged)
const kriseDropdownButton = document.getElementById("krise-status");
const kriseDropdownMenu = document.getElementById("kriseDropdownMenu");
const kriseDropdownOptions = kriseDropdownMenu.querySelectorAll("li");
kriseDropdownButton.addEventListener("click", () => {
  kriseDropdownMenu.classList.toggle("hidden");
});
document.addEventListener("click", (event) => {
  if (
    !kriseDropdownButton.contains(event.target) &&
    !kriseDropdownMenu.contains(event.target)
  ) {
    kriseDropdownMenu.classList.add("hidden");
  }
});
kriseDropdownOptions.forEach((option) => {
  option.addEventListener("click", () => {
    const selectedValue = option.getAttribute("data-value");
    kriseDropdownButton.textContent = selectedValue;
    document.getElementById("selected-krise-status").value = selectedValue;
    kriseDropdownMenu.classList.add("hidden");
  });
});

// New dropdown for Krise navn
const kriseNavnDropdownButton = document.getElementById("krise-navn-dropdown");
const kriseNavnMenu = document.getElementById("krise-navn-menu");
const kriseNavnOptions = kriseNavnMenu.querySelectorAll("li");

kriseNavnDropdownButton.addEventListener("click", () => {
  kriseNavnMenu.classList.toggle("hidden");
});

document.addEventListener("click", (event) => {
  if (
    !kriseNavnDropdownButton.contains(event.target) &&
    !kriseNavnMenu.contains(event.target)
  ) {
    kriseNavnMenu.classList.add("hidden");
  }
});

kriseNavnOptions.forEach((option) => {
  option.addEventListener("click", () => {
    const selectedId = option.getAttribute("data-id");
    const selectedName = option.getAttribute("data-name");

    // Update the dropdown button text and hidden fields for Krise ID and Name
    kriseNavnDropdownButton.textContent = selectedName;
    document.getElementById("krise_id").value = selectedId;
    document.getElementById("krise-navn").value = selectedName;

    // Hide the dropdown menu
    kriseNavnMenu.classList.add("hidden");

    // Fetch the crisis details from the backend using AJAX
    fetch(`/admin-reg/get_krise_details/${selectedId}`)
      .then((response) => response.json())
      .then((data) => {
        if (!data.error) {
          // Update the displayed fields
          document.getElementById("krise-type").value = data.KriseSituasjonType;
          document.getElementById("krise-lokasjon").value = data.Lokasjon;
          document.getElementById("annen-info").value = data.Tekstboks;

          // Update the hidden fields so they are submitted with the form
          document.getElementById("hidden-krise-type").value =
            data.KriseSituasjonType;
          document.getElementById("hidden-krise-lokasjon").value =
            data.Lokasjon;
          document.getElementById("hidden-annen-info").value = data.Tekstboks;

          // Optionally update Krise status if needed
          kriseDropdownButton.textContent = data.Status;
          document.getElementById("selected-krise-status").value = data.Status;
        }
      })
      .catch((err) => console.error("Error fetching crisis details:", err));
  });
});

// On form submission, ensure hidden fields are set
document.querySelector("form").addEventListener("submit", function () {
  document.getElementById("selected-krise-status").value =
    kriseDropdownButton.textContent.trim();
});

document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form');
    const modal = document.getElementById('confirmationModal');
    const confirmationContent = document.getElementById('confirmationContent');
    const cancelButton = document.getElementById('cancelButton');
    const confirmButton = document.getElementById('confirmButton');

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        // Mapping of form field keys to human-readable names
        const fieldLabels = {
            'evak-fnavn': 'evakuert fornavn',
            'evak-mnavn': 'evakuert mellomnavn',
            'evak-enavn': 'evakuert etternavn',
            'evak-tlf': 'evakuert telefonnummer',
            'evak-adresse': 'evakuert adresse',
            'evak-lokasjon': 'evakuert lokasjon',
            'kon-fnavn': 'Pårørende fornavn',
            'kon-mnavn': 'Pårørende mellomnavn',
            'kon-enavn': 'Pårørende etternavn',
            'kon-tlf': 'Pårørende elefonnummer',
            // add additional mappings as needed:
            // 'some-key': 'Human Readable Name'
        };

        // Gather form data
        const formData = new FormData(form);
        let contentHTML = '';

        // Set of keys to ignore
        const ignoreKeys = new Set([
            'evakuert_id',
            'kontakt_person_id',
            'status_id',
            'krise-status',
            'krise-type',
            'krise_id',
            'krise-lokasjon',
            'annen-info'
        ]);

        // Loop through the form data and add fields not in the ignore list
        for (const [key, value] of formData.entries()) {
            if (!ignoreKeys.has(key)) {
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
        modal.classList.add('hidden');
        form.submit();
    });
});
