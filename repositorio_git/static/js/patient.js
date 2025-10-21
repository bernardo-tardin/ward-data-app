document.addEventListener("DOMContentLoaded", () => {

  function formatHour(hour) {
      const hourStr = String(hour);
      if (hourStr.length === 3) {
          return `${hourStr[0]}:${hourStr.slice(1)}`;
      } else if (hourStr.length === 4) {
          return `${hourStr.slice(0, 2)}:${hourStr.slice(2)}`;
      }
      return "00:00";
  }

  function generateDiagnostics(fenomenos) {
      return fenomenos.map(f => 
          `<div>${f.DATA_INICIO || ''} ${formatHour(f.HORA_INICIO || '0000')} - ${f.FENOMENO_PT || ''} - ${f.DEFINICAO_PT || ''}</div>`
      ).join('');
  }

  function generatePrescriptions(medicacoes) {
      return medicacoes.map(m => 
          `<div>${m.FARMACO || ''} - ${m.VIA || ''} - ${m.DOSE || ''}</div>`
      ).join('');
  }

  function generateTherapeutics(atitudes) {
      return atitudes.map(a => 
          `<div>${a.ATITUDE_TERAPEUTICA || ''} - ${a.HORARIO || ''}</div>`
      ).join('');
  }

  function generateAnalysis(analises) {
      return analises.map(a => 
          `<div>${a.ANALISE || 'OTHER ANALYSIS'} - Start: ${a.DTA_INICIO || ''} ${formatHour(a.HORA_INICIO || '0000')}</div>`
      ).join('');
  }

  function generateExams(exames) {
      return exames.map(e => 
          `<div>${e.EXAME || ''} - Scheduled Date: ${e.DTA_INICIO || ''} </div>`
      ).join('');
  }

  function generateDiaries(diarios) {
      return diarios.map(d => 
          `<div>${d.DATA || ''} ${formatHour(d.HORA || '0000')} - ${d.DIARIO || ''}</div>`
      ).join('');
  }

  function renderPatient(patient) {
      const patientInfo = document.getElementById("patientInfo");
      patientInfo.innerHTML = '';

      const name = patient.patient_name || "Name missing";
      const sala = patient.COD_SALA || 'N/A';
      const cama = patient.NUM_CAMA || 'N/A';
      const dataEntrada = patient.DTA_ENTRADA || 'N/A';
      const antecedentes = patient.antecedentes || 'N/A';
      const diagnostico = patient.diagnostico || 'N/A';

      const fenomenos = generateDiagnostics(patient.fenomenos);
      const medicacao = generatePrescriptions(patient.medicacao);
      const atitudes = generateTherapeutics(patient.atitudes_terapeuticas);
      const analises = generateAnalysis(patient.analises);
      const exames = generateExams(patient.exames);
      const diarios = generateDiaries(patient.diarios);

      const formattedDataEntrada = `${dataEntrada} ${formatHour(patient.HORA_ENTRADA || 'N/A')}`;

      const row = `
      <div class="patient-info m-4 d-flex flex-column">
          <div class="patient-info-header d-flex justify-content-between">
              <div class="personal-info d-flex flex-column">
                  <div class="d-flex align-items-center">
                      <div><strong>ID:</strong></div> 
                      <div class="ms-2"><span>${patient.id}</span></div>
                  </div>
                  <div class="d-flex align-items-center">
                      <div><strong>Name:</strong></div>
                      <div class="ms-2"><span>${name}</span></div>
                  </div>
                  <div class="d-flex align-items-center">
                      <div><strong>Diagnosis:</strong></div>
                      <div class="ms-2"><span>${diagnostico}</span></div>
                  </div>
                  <div class="d-flex align-items-center">
                      <div><strong>History:</strong></div>
                      <div class="ms-2"><span>${antecedentes}</span></div>
                  </div>
                  <div class="d-flex align-items-center">
                      <div><strong>Admission Date:</strong></div>
                      <div class="ms-2"><span>${formattedDataEntrada}</span></div>
                  </div>
              </div>
              <div class="local-info d-flex flex-column me-5">
                  <div class="d-flex align-items-center">
                      <div><strong>Room:</strong></div>
                      <div class="ms-2"><span>${sala}</span></div>
                  </div>
                  <div class="d-flex align-items-center">
                      <div><strong>Bed:</strong></div>
                      <div class="ms-2"><span>${cama}</span></div>
                  </div>
                   <button class="btn btn-sm btn-outline-primary mt-2" onclick="window.open('/pdfs/${patient._id}.pdf', '_blank')">
                          Generate PDF
                      </button>
               </div>
          </div>
          <div class="additional-info mt-5">
              <div class="d-flex flex-column mb-3">
                  <strong>Nursing Diagnoses:</strong>
                  <div>${fenomenos}</div>
              </div>
              <div class="d-flex flex-column mb-3">
                  <strong>Prescription:</strong>
                  <div>${medicacao}</div>
              </div>
              <div class="d-flex flex-column mb-3">
                  <strong>Therapeutic Interventions:</strong>
                  <div>${atitudes}</div>
              </div>
              <div class="d-flex flex-column mb-3">
                  <strong>Analysis:</strong>
                  <div>${analises}</div>
              </div>
              <div class="d-flex flex-column mb-3">
                  <strong>Exams:</strong>
                  <div>${exames}</div>
              </div>
              <div class="d-flex flex-column mb-3">
                  <strong>Diary:</strong>
                  <div>${diarios}</div>
              </div>
          </div>
      </div>
      `;
    
      patientInfo.innerHTML += row;
  }
});