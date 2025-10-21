document.addEventListener("DOMContentLoaded", () => {
    fetch('/api/recent_patients_api/')
        .then(response => response.json())
        .then(data => {
            const tableBody = document.getElementById("recentPatientsTableBody");
            tableBody.innerHTML = ""; 
            data.forEach(paciente => {
                // UPDATED: Corrected navigation URL to /info-patient/
                const patientUrl = `/info-patient/?id=${paciente.episode_id}`;
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td><a href="${patientUrl}" style="text-decoration:none; color:inherit;">${paciente.episode_id}</a></td>
                    <td><a href="${patientUrl}" style="text-decoration:none; color:inherit;">${paciente.patient_name || 'Name missing'}</a></td>
                    <td>${paciente.sala || '-'}</td>
                    <td>${paciente.cama || '-'}</td>
                    <td>
                        <button class="btn btn-sm btn-pdf" onclick="window.open('/generate_pdf/${paciente.episode_id}', '_blank')">Generate PDF</button>
                    </td>
                `;
                tableBody.appendChild(row);
            });
        })
        .catch(error => {
            console.error("Error fetching recent patients:", error);
        });      
});