document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("search-input");
    const searchBtn = document.getElementById("search-btn");

    // Check if an ID was passed in the URL (e.g., from the all-patients page)
    const urlParams = new URLSearchParams(window.location.search);
    const patientIdFromUrl = urlParams.get('id');

    if (patientIdFromUrl) {
        if (searchInput) {
            searchInput.value = patientIdFromUrl; 
        }
        fetchPatient(patientIdFromUrl);
    }

    searchBtn.addEventListener("click", async function() {
        const searchQuery = searchInput.value.trim();
        if (searchQuery) {
            await fetchPatient(searchQuery);
        } else {
            renderError("Please enter a search term.");
        }
    });

     searchInput.addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            event.preventDefault(); 
            searchBtn.click(); 
        }
    });

    async function fetchPatient(searchQuery) {
        renderLoading();
        const url = `/api/patient_info/?search=${encodeURIComponent(searchQuery)}`;

        try {
            const response = await fetch(url);
            const data = await response.json();

            if (response.ok) {
                renderPatient(data); 

            } else {
                console.error("API Error:", data);
                renderError(data.error || `Error ${response.status} fetching patient.`);
            }
        } catch (error) {
            console.error("Fetch request error:", error);
            renderError("Network error or error processing response while fetching patient.");
        }
    }

    // --- HTML Generation Functions ---

    function generatePrescriptions(medicacoes = []) {
        if (!medicacoes || medicacoes.length === 0) {
            return `<div class="card p-3 mb-3">
                        <p>No medication registered.</p>
                    </div>`;
        }

        let rows = medicacoes.map(m => `
            <tr>
                <td><div id='farmaco-content'>${m.farmaco || 'N/A'}</div></td>
                <td>${m.via || 'N/A'}</td>
                <td>${m.dose || 'N/A'}</td>
                <td>${m.horario || 'N/A'}</td>
            </tr>
        `).join('');

        return `
        <div class="card p-3 mb-3">
            <table class="table table-striped table-sm custom-table-color">
                <thead>
                    <tr>
                        <th>Drug</th>
                        <th>Route</th>
                        <th>Dose</th>
                        <th>Schedule</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows}
                </tbody>
            </table>
        </div>`;
    }

    function generateTherapeutics(atitudes = []) {
        if (!atitudes || atitudes.length === 0) {
            return `<div class="card p-3 mb-3">
                        <p>No therapeutic interventions registered.</p>
                    </div>`;
        }

        let rows = atitudes.map(a => `
            <tr>
                <td>${a.atitude || 'OTHER INTERVENTION'}</td>
                <td>${a.hora_at || 'N/A'}</td>
            </tr>
        `).join('');

        return `
        <div class="card p-3 mb-3">
            <table class="table table-striped table-sm custom-table-color">
                <thead>
                    <tr>
                        <th>Intervention</th>
                        <th>Schedule</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows}
                </tbody>
            </table>
        </div>`;
    }

    function generateAnalysis(analises = []) {
        if (!analises || analises.length === 0) {
            return `<div class="card p-3 mb-3">
                        <p>No lab analysis registered.</p>
                    </div>`;
        }

        let rows = analises.map(a => `
            <tr>
                <td>${a.analise || 'OTHER ANALYSIS'}</td>
                <td>${a.dta_anl || 'N/A'}</td>
                <td>${a.hora_anl || 'N/A'}</td>
            </tr>
        `).join('');

        return `
        <div class="card p-3 mb-3">
            <table class="table table-striped table-sm custom-table-color">
                <thead>
                    <tr>
                        <th>Analysis</th>
                        <th>Start Date</th>
                        <th>Time</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows}
                </tbody>
            </table>
        </div>`;
    }

    function generateExams(exames = []) {
        if (!exames || exames.length === 0) {
            return `<div class="card p-3 mb-3">
                        <p>No exams registered.</p>
                    </div>`;
        }

        let rows = exames.map(e => `
            <tr>
                <td>${e.exame || 'OTHER EXAM'}</td>
                <td>${e.dta_exm || 'N/A'}</td>
            </tr>
        `).join('');

        return `
        <div class="card p-3 mb-3">
            <table class="table table-striped table-sm custom-table-color">
                <thead>
                    <tr>
                        <th>Exam</th>
                        <th>Scheduled Date</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows}
                </tbody>
            </table>
        </div>`;
    }

    function generateDiaries(diarios = []) {
        if (!diarios || diarios.length === 0) {
            return `<div class="card p-3 mb-3">
                        <p>No diary entries registered.</p>
                    </div>`;
        }

        let rows = diarios.map(d => `
            <tr>
                <td>${d.dta_dir || 'N/A'}</td>
                <td>${d.hora_dir || 'N/A'}</td>
                <td>${d.diario || 'Empty entry'}</td>
            </tr>
        `).join('');

        return `
        <div class="card p-3 mb-3">
            <table class="diario table table-striped table-sm custom-table-color">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Time</th>
                        <th>Entry</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows}
                </tbody>
            </table>
        </div>`;
    }
    
    function renderPatient(patient) {
        const patientInfoDiv = document.getElementById("patientInfo");
        patientInfoDiv.innerHTML = '';

        // Extract and clean data
        const patientId = patient.episode_id || 'Unknown ID';
        const name = patient.patient_name || "Name missing.";
        const sala = patient.sala || 'N/A';
        const cama = patient.cama || 'N/A';
        const dataEntrada = patient.data_entrada || '---';
        const horaEntrada = patient.hora_entrada || '';
        const telemovel = patient.telefone?.[0]?.telemovel || 'N/A';
        const telefone_morada = patient.telefone?.[0]?.telefone_morada || 'N/A';

        const antecedentes = Array.isArray(patient.antecedentes) && patient.antecedentes.length > 0
            ? patient.antecedentes.join(', ')
            : 'No history registered.';
        const diagnostico = Array.isArray(patient.diagnostico) && patient.diagnostico.length > 0
            ? patient.diagnostico.join(', ')
            : 'No medical diagnosis registered.';
        const observacoes = (patient.observacoes?.map(o => o.observacoes?.trim()).filter(o => o) || []).join(", ") ||
        "No observations registered.";
        const pessoa_signif = (patient.pessoa_signif?.map(p => p.pessoa_signif?.trim()).filter(p => p) || []).join(", ") ||
        "";

        // Helper for formatting contact numbers
        function formatarContactos(telefone_morada, telemovel) {
            if (telefone_morada && telemovel) {
                if (telefone_morada !== telemovel) {
                return `${telefone_morada} / ${telemovel}`;
                } else {
                return telefone_morada;
                }
            }
            return telefone_morada || telemovel || "No phone registered.";
        }
        
        // Helper for formatting nursing diagnoses
        function generateDiagnosticsCard(fenomenos) {
            if (!fenomenos || fenomenos.length === 0) {
                return `<p>No nursing diagnoses registered.</p>`;
            }

            function criarDataManual(dataStr, horaStr) {
                if (!dataStr || !horaStr) return null;
                const [dia, mes, ano] = dataStr.split('-').map(Number);
                const [hora, minuto] = horaStr.split(':').map(Number);
                return new Date(ano, mes - 1, dia, hora, minuto);
            }

            function compararDiagnosticos(a, b) {
                const dataHoraA = criarDataManual(a.dta_fenom, a.hora_fenom);
                const dataHoraB = criarDataManual(b.dta_fenom, b.hora_fenom);
                if (!dataHoraA) return 1;
                if (!dataHoraB) return -1;
                return dataHoraB - dataHoraA; // Sort descending
            }

            const fenomenosOrdenados = [...fenomenos].sort(compararDiagnosticos);

            let html = '';
            fenomenosOrdenados.forEach(fenomeno => {
                const nomeFenomeno = fenomeno.fenomeno || 'Unknown diagnosis';
                const definicao = fenomeno.def_fenom || '-';
                const data = fenomeno.dta_fenom || '-';
                const hora = fenomeno.hora_fenom || '-';

                html += `
                <strong class="diagnostico mt-3 mb-2">${nomeFenomeno}</strong>
                <table class="table table-striped table-sm custom-table-color">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Time</th>
                            <th>Diagnosis</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>${data}</td>
                            <td>${hora}</td>
                            <td>${definicao}</td>
                        </tr>
                    </tbody>
                </table>`;
            });
            return html;
        } 

        // Generate HTML for all sections
        const telefone = formatarContactos(telefone_morada, telemovel);
        const fenomenosHtml = generateDiagnosticsCard(patient.fenomenos);
        const medicacaoHtml = generatePrescriptions(patient.medicacao);
        const atitudesHtml = generateTherapeutics(patient.atitudes_terapeuticas);
        const analisesHtml = generateAnalysis(patient.analises);
        const examesHtml = generateExams(patient.exames);
        const diariosHtml = generateDiaries(patient.diarios);

        const formattedDataEntrada = `${dataEntrada} ${horaEntrada}`.trim();

        // Final patient HTML structure
        const patientHtml = `
        <div class="patient-info m-4 d-flex flex-column">
            <div class="patient-info-header d-flex justify-content-between align-items-start">
                <div class="personal-info d-flex flex-column me-2">
                    <div class="d-flex align-items-center mb-1">
                        <div><strong>Episode ID:</strong></div>
                        <div class="ms-2"><span>${patientId}</span></div>
                    </div>
                    <div class="d-flex align-items-center mb-1">
                        <div><strong>Name:</strong></div>
                        <div class="ms-2"><span>${name}</span></div>
                    </div>
                    <div class="d-flex align-items-center mb-1">
                        <div><strong>Phone:</strong></div>
                        <div class="ms-2"><span>${telefone}</span></div>
                    </div>
                    <div class="d-flex align-items-center mb-1">
                        <div><strong>Observations:</strong></div>
                        <div class="ms-2"><span>${observacoes}</span></div>
                    </div>
                    <div class="d-flex align-items-baseline mb-1">
                        <div><strong>Medical&nbsp;Diagnosis:</strong></div>
                        <div class="ms-2"><span>${diagnostico}</span></div>
                    </div>
                    <div class="d-flex align-items-baseline mb-1">
                        <div><strong>History:</strong></div>
                        <div class="ms-2"><span>${antecedentes}</span></div>
                    </div>
                    <div class="d-flex align-items-baseline mb-1">
                        <div><strong>Contact Person:</strong></div>
                        <div class="ms-2"><span>${pessoa_signif}</span></div>
                    </div>
                    <div class="d-flex align-items-center mb-1">
                        <div><strong>Admission Date:</strong></div>
                        <div class="ms-2"><span>${formattedDataEntrada}</span></div>
                    </div>
                </div>
                <div class="local-info d-flex flex-column align-items-start me-5">
                    <div class="d-flex align-items-center w-100">
                        <div><strong>Room:</strong></div>
                        <div class="ms-2"><span>${sala}</span></div>
                    </div>
                    <div class="d-flex align-items-center w-100">
                        <div><strong>Bed:</strong></div>
                        <div class="ms-2"><span>${cama}</span></div>
                    </div>
                    <button class="btn btn-sm btn-search mt-2" id='gerar-pdf-button' onclick="window.open('/generate_pdf/${patientId}', '_blank')">
                        <i class="bi bi-file-earmark-pdf me-1"></i> Generate PDF
                    </button>
                </div>
            </div>
            <hr>
            <div class="additional-info d-flex gap-4">
                <div class="card-section" style="flex: 0 0 50%; max-width: 50%; max-height: none; overflow-y: visible;">
                    <strong>Nursing Diagnoses</strong>
                    <div class="card p-3 mb-3">
                        ${fenomenosHtml}
                    </div>
                </div>
                <div class="card-section d-flex flex-column gap-3" style="flex: 0 0 48%; max-width: 48%; max-height: none; overflow-y: visible;">
                    <div>
                        <strong>Medical Prescription</strong>
                        <div class="data-section" style="max-height: none; overflow-y: visible;">${medicacaoHtml}</div>
                    </div>
                    <div>
                        <strong>Lab Results</strong>
                        <div class="data-section" style="max-height: none; overflow-y: visible;">${analisesHtml}</div>
                    </div>
                    <div>
                        <strong>Exams</strong>
                        <div class="data-section" style="max-height: none; overflow-y: visible;">${examesHtml}</div>
                    </div>
                    <div>
                        <strong>Therapeutic Interventions</strong>
                        <div class="data-section" style="max-height: none; overflow-y: visible;">${atitudesHtml}</div>
                    </div>
                    <div>
                        <strong>Clinical Diary</strong>
                        <div class="data-section" style="max-height: none; overflow-y: visible;">${diariosHtml}</div>
                    </div>
                </div>
            </div>
        </div>
        `;

        patientInfoDiv.innerHTML = patientHtml;
    }

    function renderLoading() {
        const patientInfoDiv = document.getElementById("patientInfo");
        patientInfoDiv.innerHTML = `<div class="d-flex justify-content-center align-items-center p-5">
                                        <div class="spinner-border custom-spinner" role="status">
                                            <span class="visually-hidden">Loading...</span>
                                        </div>
                                        <span class="ms-2">Loading patient data...</span>
                                     </div>`;
    }

    function renderError(message) {
        const patientInfoDiv = document.getElementById("patientInfo");
        patientInfoDiv.innerHTML = `<div class="alert alert-danger text-center m-4" role="alert">
                                        ${message}
                                     </div>`;
    }
});