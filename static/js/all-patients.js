document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("search-input");
    const sortBySelect = document.getElementById("sort-by");
    const sortOrderSelect = document.getElementById("sort-order");
    const patientsTableBody = document.getElementById("patientsTableBody");
    const paginationInfo = document.getElementById("pagination-info");
    const prevBtn = document.getElementById("prev-page");
    const nextBtn = document.getElementById("next-page");


    let currentPage = 1;
    const limit = 10; 

    async function fetchPatients() {
        const searchQuery = searchInput.value.trim();
        const sortBy = sortBySelect.value;
        const sortOrder = sortOrderSelect.value;

        // The API URL is loaded from the relative path
        const url = `/api/all_patients/?page=${currentPage}&limit=${limit}&sort_by=${sortBy}&sort_order=${sortOrder}&search=${encodeURIComponent(searchQuery)}`; 

        try {
            patientsTableBody.innerHTML = `<tr><td colspan="8" class="text-center">Loading...</td></tr>`;
            prevBtn.disabled = true;
            nextBtn.disabled = true;
            paginationInfo.textContent = 'Loading...'; 

            const response = await fetch(url);

             if (response.status === 404) {
                 renderError("API not found (404). Check the API URL in JavaScript and urls.py.");
                 updatePagination(1, 1); 
                 return;
             }

            const data = await response.json();

            if (response.ok) { 
                renderPatients(data.patients); 
                updatePagination(data.page, data.total_pages);
            } else { 
                console.error("API Error:", data); 
                renderError(data.error || `Error ${response.status} fetching patients.`);
                updatePagination(1, 1); 
            }
        } catch (error) {
            console.error("Fetch request error:", error);
            renderError("Network error or error processing response.");
            updatePagination(1, 1); 
        }
    }

    function renderPatients(patients) {
        patientsTableBody.innerHTML = ''; 

        if (!patients || patients.length === 0) {
             patientsTableBody.innerHTML = `<tr><td colspan="8" class="text-center">No patients found matching the criteria.</td></tr>`;
             return;
        }

        patients.forEach(patient => {
            const idUtente = patient.episode_id || patient.patient_id || patient.id || '-'; 
            const nomeUtente = patient.patient_name || "Name missing";
            const sala = patient.sala || 'N/A';
            const cama = patient.cama || 'N/A';
            const dataEntrada = patient.data_entrada || 'N/A';
            const ultimoDiario = patient.ultimo_diario || 'No records'; 

            const pdfUrl = `/generate_pdf/${idUtente}/`; 
            
            // UPDATED: Corrected navigation URL to /info-patient/
            const patientUrl = `/info-patient/?id=${idUtente}`;

            const row = `
                <tr>
                    <td><a href="${patientUrl}" style="text-decoration:none; color:inherit;">${idUtente}</a></td>
                    <td><a href="${patientUrl}" style="text-decoration:none; color:inherit;">${nomeUtente}</a></td>
                    <td>${sala}</td>
                    <td>${cama}</td>
                    <td>${dataEntrada}</td>
                    <td class="diario"><div class='diario-content'>${ultimoDiario}</div></td>
                    <td>
                        <button class="btn btn-sm btn-pdf"
                             onclick="window.open('${pdfUrl}', '_blank')">
                            <i class="bi bi-file-earmark-pdf me-1"></i> Generate PDF
                        </button>
                    </td>
                </tr>
            `;
            patientsTableBody.insertAdjacentHTML('beforeend', row); 
        });
    }

    function renderError(message) {
        patientsTableBody.innerHTML = `<tr><td colspan="8" class="text-center text-danger">${message}</td></tr>`;
    }

    function updatePagination(page, totalPages) {
         const currentPageNum = Number(page) || 1; 
         const maxPages = Math.max(1, Number(totalPages) || 1); 
        paginationInfo.textContent = `Page ${currentPageNum} of ${maxPages}`;
        prevBtn.disabled = currentPageNum <= 1;
        nextBtn.disabled = currentPageNum >= maxPages;
    }

    prevBtn.addEventListener("click", () => {
        if (currentPage > 1) {
            currentPage--;
            fetchPatients();
        }
    });

    nextBtn.addEventListener("click", () => {
        currentPage++;
        fetchPatients();
    });

    // Debounce search input
    let searchTimeout;
    searchInput.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            currentPage = 1; 
            fetchPatients();
        }, 300); // 300ms delay
    });

    sortBySelect.addEventListener('change', () => {
        currentPage = 1;
        fetchPatients();
    });

    sortOrderSelect.addEventListener('change', () => {
        currentPage = 1;
        fetchPatients();
    });

    fetchPatients(); 
});