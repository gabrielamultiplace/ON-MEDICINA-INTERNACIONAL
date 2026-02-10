"""
CANNABIS MEDICINAL - FRONTEND UI MODULE
=====================================
JavaScript & HTML for prescription editor integrated with video consultation.
Displays AI-generated prescription side-by-side with editable version.
"""

CANNABIS_FRONTEND_HTML = """
<!-- CANNABIS MEDICINAL PRESCRIPTION EDITOR PANEL -->
<div id="cannabis-panel" style="display: none;">
    <div style="padding: 20px; background: white; border-radius: 8px;">
        
        <!-- HEADER -->
        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px solid #1b7c4a;">
            <span style="font-size: 24px;">💊</span>
            <div>
                <h2 style="margin: 0; color: #333;">Prescrição de Cannabis Medicinal</h2>
                <p style="margin: 5px 0; color: #999; font-size: 13px;">Gerada por IA | Editável pelo Médico</p>
            </div>
        </div>
        
        <!-- TABS: AI Prescription vs Editable Version -->
        <div style="display: flex; gap: 10px; margin-bottom: 20px; border-bottom: 2px solid #eee;">
            <button onclick="switchCannabisTabs('ai')" class="cannabis-tab-btn active" id="tab-ai-btn" 
                    style="padding: 10px 20px; background: none; border: none; cursor: pointer; font-weight: bold; color: #1b7c4a; border-bottom: 3px solid #1b7c4a; margin-bottom: -2px;">
                🤖 Prescrição IA (Automática)
            </button>
            <button onclick="switchCannabisTabs('edit')" class="cannabis-tab-btn" id="tab-edit-btn"
                    style="padding: 10px 20px; background: none; border: none; cursor: pointer; font-weight: bold; color: #999; border-bottom: 3px solid transparent; margin-bottom: -2px;">
                ✏️ Editar / Finalizar
            </button>
        </div>
        
        <!-- TAB 1: AI-GENERATED PRESCRIPTION -->
        <div id="tab-cannabis-ai" style="display: block;">
            <div style="background: #f9f9f9; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                <p style="margin: 0 0 10px 0; color: #666; font-size: 13px;">
                    <strong>Prescrição gerada automaticamente pela IA</strong> baseada na anamnese, exames e protocolos ANVISA.
                </p>
                <div id="ai-prescription-display" style="background: white; padding: 15px; border-radius: 5px; border: 1px solid #ddd;">
                    <p style="color: #999; text-align: center; padding: 20px;">Carregando prescrição automática...</p>
                </div>
            </div>
            
            <!-- TITULATION SCHEDULE VISUALIZATION -->
            <div style="margin-bottom: 20px;">
                <h3 style="margin: 0 0 10px 0; color: #333; font-size: 14px;">📊 Cronograma de Titulação (6 Semanas)</h3>
                <div id="titulation-chart" style="background: white; padding: 15px; border-radius: 5px; border: 1px solid #ddd; overflow-x: auto;">
                    <table style="width: 100%; font-size: 12px; border-collapse: collapse;">
                        <thead>
                            <tr style="background: #1b7c4a; color: white;">
                                <th style="padding: 8px; text-align: left;">Semana</th>
                                <th style="padding: 8px; text-align: center;">Gotas</th>
                                <th style="padding: 8px; text-align: center;">Frequência</th>
                                <th style="padding: 8px; text-align: center;">CBD/dia</th>
                                <th style="padding: 8px; text-align: center;">THC/dia</th>
                            </tr>
                        </thead>
                        <tbody id="titulation-schedule-table">
                            <tr style="border-bottom: 1px solid #eee;"><td colspan="5" style="padding: 10px; text-align: center; color: #999;">Carregando...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- 24-MONTH JUDICIAL PROJECTION -->
            <div style="margin-bottom: 20px;">
                <h3 style="margin: 0 0 10px 0; color: #333; font-size: 14px;">⚖️ Projeção Judicial (24 Meses)</h3>
                <div id="judicial-projection" style="background: white; padding: 15px; border-radius: 5px; border: 1px solid #ddd;">
                    <div id="judicial-summary" style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                        <!-- Will be populated by JS -->
                    </div>
                    <details>
                        <summary style="cursor: pointer; font-weight: bold; color: #1b7c4a; margin-top: 10px;">
                            📋 Ver Projeção Detalhada (24 meses)
                        </summary>
                        <div id="judicial-detail-table" style="margin-top: 10px; overflow-x: auto;">
                            <table style="width: 100%; font-size: 11px; border-collapse: collapse;">
                                <thead>
                                    <tr style="background: #f0f0f0;">
                                        <th style="padding: 6px; border: 1px solid #ddd;">Mês</th>
                                        <th style="padding: 6px; border: 1px solid #ddd;">CBD (mg)</th>
                                        <th style="padding: 6px; border: 1px solid #ddd;">Volume (mL)</th>
                                        <th style="padding: 6px; border: 1px solid #ddd;">Custo (R$)</th>
                                    </tr>
                                </thead>
                                <tbody id="judicial-months">
                                    <tr><td colspan="4" style="padding: 10px; text-align: center; color: #999;">Carregando...</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </details>
                </div>
            </div>
        </div>
        
        <!-- TAB 2: EDITABLE VERSION -->
        <div id="tab-cannabis-edit" style="display: none;">
            <!-- PRODUCT SELECTION -->
            <div style="margin-bottom: 20px;">
                <label style="display: block; font-weight: bold; margin-bottom: 8px; color: #333;">
                    🧴 Selecionar Óleo de Cannabis
                </label>
                <select id="cannabis-product-select" onchange="updateCannabisProduct()" 
                        style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 13px;">
                    <option value="">-- Carregando produtos disponíveis --</option>
                </select>
                <div id="product-info" style="background: #f0f0f0; padding: 10px; border-radius: 5px; margin-top: 10px; font-size: 12px; display: none;">
                    <!-- Product details will appear here -->
                </div>
            </div>
            
            <!-- DOSAGE CUSTOMIZATION -->
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
                <div>
                    <label style="display: block; font-weight: bold; margin-bottom: 5px; color: #333;">
                        💧 Gotas por Dose
                    </label>
                    <input type="number" id="cannabis-drops" min="2" max="30" value="2" 
                           style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 5px;" />
                </div>
                <div>
                    <label style="display: block; font-weight: bold; margin-bottom: 5px; color: #333;">
                        🕐 Vezes por Dia
                    </label>
                    <input type="number" id="cannabis-frequency" min="1" max="4" value="3"
                           style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 5px;" />
                </div>
            </div>
            
            <!-- CLINICAL NOTES -->
            <div style="margin-bottom: 20px;">
                <label style="display: block; font-weight: bold; margin-bottom: 8px; color: #333;">
                    📝 Observações Clínicas
                </label>
                <textarea id="cannabis-notes" placeholder="Observações adicionais..." 
                          style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; min-height: 100px; font-size: 13px; font-family: Arial;"></textarea>
            </div>
            
            <!-- EXAM REQUESTS -->
            <div style="margin-bottom: 20px; padding: 15px; background: #f9f9f9; border-radius: 5px; border-left: 4px solid #1b7c4a;">
                <h3 style="margin: 0 0 15px 0; color: #333; font-size: 14px;">🔬 Solicitar Exames</h3>
                
                <div style="display: flex; gap: 10px; margin-bottom: 15px;">
                    <button onclick="toggleExamType('laboratorial')" id="exam-lab-btn" class="exam-type-btn" 
                            style="flex: 1; padding: 10px; border: 2px solid #1b7c4a; background: #1b7c4a; color: white; border-radius: 5px; cursor: pointer; font-weight: bold;">
                        🧪 Exames Laboratoriais
                    </button>
                    <button onclick="toggleExamType('genetic')" id="exam-genetic-btn" class="exam-type-btn"
                            style="flex: 1; padding: 10px; border: 2px solid #ddd; background: white; color: #333; border-radius: 5px; cursor: pointer; font-weight: bold;">
                        🧬 Exame Genético
                    </button>
                </div>
                
                <div id="exam-list" style="display: flex; flex-direction: column; gap: 8px;">
                    <!-- Exam items will be populated here -->
                </div>
            </div>
            
            <!-- SIGNATURE & FINALIZE -->
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <button onclick="signCannabisRx()" 
                        style="padding: 12px; background: linear-gradient(135deg, #1b7c4a 0%, #0d5a36 100%); color: white; border: none; border-radius: 5px; font-weight: bold; cursor: pointer; font-size: 14px;">
                    🔒 Assinar com VidaaS
                </button>
                <button onclick="saveDraft()" 
                        style="padding: 12px; background: #f0f0f0; color: #333; border: 1px solid #ddd; border-radius: 5px; font-weight: bold; cursor: pointer; font-size: 14px;">
                    💾 Salvar Rascunho
                </button>
            </div>
        </div>
    </div>
</div>

<script>
// ============ CANNABIS MODULE JAVASCRIPT ============

let cannabisData = {
    prescription: null,
    titulation_weeks: [],
    projection_24_months: [],
    judicial_summary: null,
    selected_product: null,
    exams: {
        laboratorial: [],
        genetic: []
    }
};

// Default exam lists
const DEFAULT_LAB_EXAMS = [
    "Ácido Fólico", "Ácido Úrico", "Colesterol Total e Frações", "CPK", "Creatinina",
    "Feminina", "Ferro Sérico", "Fosfatase Alcalina", "Glicose", "Glicohemoglobina",
    "GIPD", "Hemograma", "Homocisteína", "Insulina", "Proteína C Reativa",
    "TSH", "Triglicerídeos", "TSH T4/T3", "Ureia", "VIT. B6/B12 e D"
];

const DEFAULT_GENETIC_EXAMS = [
    "Teste Genético Completo", "Análise de Variantes Relevantes"
];

// Switch between AI and Editable tabs
function switchCannabisTabs(tab) {
    document.getElementById('tab-cannabis-ai').style.display = tab === 'ai' ? 'block' : 'none';
    document.getElementById('tab-cannabis-edit').style.display = tab === 'edit' ? 'block' : 'none';
    
    document.getElementById('tab-ai-btn').style.borderBottom = tab === 'ai' ? '3px solid #1b7c4a' : '3px solid transparent';
    document.getElementById('tab-ai-btn').style.color = tab === 'ai' ? '#1b7c4a' : '#999';
    
    document.getElementById('tab-edit-btn').style.borderBottom = tab === 'edit' ? '3px solid #1b7c4a' : '3px solid transparent';
    document.getElementById('tab-edit-btn').style.color = tab === 'edit' ? '#1b7c4a' : '#999';
}

// Load cannabis products
async function loadCannabisProducts() {
    try {
        const response = await fetch('/api/cannabis/products');
        const data = await response.json();
        
        if (data.success) {
            const select = document.getElementById('cannabis-product-select');
            select.innerHTML = '<option value="">-- Selecione um óleo --</option>';
            
            data.products.forEach(product => {
                const option = document.createElement('option');
                option.value = product.product_id;
                option.text = `${product.brand} - ${product.name} (CBD: ${product.cbd_mg_ml}mg/mL)`;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Erro ao carregar produtos:', error);
    }
}

// Calculate prescription
async function calculateCannabisRx(patientData) {
    try {
        const payload = {
            product_id: document.getElementById('cannabis-product-select').value,
            patient_name: patientData.name || 'Paciente',
            patient_diagnosis: patientData.diagnosis || '',
            medical_indication: patientData.indication || ''
        };
        
        const response = await fetch('/api/cannabis/prescriptions/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        
        if (data.success) {
            cannabisData = {
                ...cannabisData,
                prescription: data.prescription,
                titulation_weeks: data.titulation_weeks,
                projection_24_months: data.projection_24_months,
                judicial_summary: data.judicial_summary
            };
            
            displayPrescription();
        }
    } catch (error) {
        console.error('Erro ao calcular prescrição:', error);
    }
}

// Display AI prescription
function displayPrescription() {
    if (!cannabisData.prescription) return;
    
    const rx = cannabisData.prescription;
    const html = `
        <div style="padding: 15px;">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                <div>
                    <p style="margin: 0 0 5px 0; color: #999; font-size: 11px; text-transform: uppercase;">Paciente</p>
                    <p style="margin: 0; font-weight: bold; color: #333;">${rx.patient_name}</p>
                </div>
                <div>
                    <p style="margin: 0 0 5px 0; color: #999; font-size: 11px; text-transform: uppercase;">Diagnóstico</p>
                    <p style="margin: 0; color: #333;">${rx.patient_diagnosis}</p>
                </div>
                <div>
                    <p style="margin: 0 0 5px 0; color: #999; font-size: 11px; text-transform: uppercase;">Medicamento</p>
                    <p style="margin: 0; font-weight: bold; color: #333;">${rx.product.name}</p>
                </div>
                <div>
                    <p style="margin: 0 0 5px 0; color: #999; font-size: 11px; text-transform: uppercase;">CBD/Dia Inicial</p>
                    <p style="margin: 0; font-weight: bold; color: #333;">${rx.initial_cbd_mg_daily.toFixed(2)} mg</p>
                </div>
            </div>
            
            <div style="padding: 10px; background: #fff9e6; border-left: 3px solid #ff9800; border-radius: 3px;">
                <strong style="color: #333;">⚠️ IMPORTANTE:</strong>
                <p style="margin: 5px 0; color: #666; font-size: 12px;">
                    Cannabis Medicinal requer TITULAÇÃO progressiva. Não é dose fixa. 
                    Aumentar gradualmente conforme tolerância do paciente.
                </p>
            </div>
        </div>
    `;
    
    document.getElementById('ai-prescription-display').innerHTML = html;
    
    // Display titulation schedule
    displayTitulation();
    displayJudicialProjection();
}

// Display titulation schedule
function displayTitulation() {
    const tbody = document.getElementById('titulation-schedule-table');
    tbody.innerHTML = '';
    
    cannabisData.titulation_weeks.forEach(week => {
        const row = `
            <tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 8px; color: #333;"><strong>Semana ${week.week}</strong></td>
                <td style="padding: 8px; text-align: center; color: #666;">${week.drops_per_dose}</td>
                <td style="padding: 8px; text-align: center; color: #666;">${week.times_per_day}x ao dia</td>
                <td style="padding: 8px; text-align: center; color: #1b7c4a; font-weight: bold;">${week.cbd_mg_per_day.toFixed(1)}</td>
                <td style="padding: 8px; text-align: center; color: #999;">${week.thc_mg_per_day.toFixed(2)}</td>
            </tr>
        `;
        tbody.innerHTML += row;
    });
}

// Display judicial projection
function displayJudicialProjection() {
    const summary = cannabisData.judicial_summary;
    if (!summary) return;
    
    const summaryDiv = document.getElementById('judicial-summary');
    summaryDiv.innerHTML = `
        <div style="background: #f0f0f0; padding: 10px; border-radius: 5px; text-align: center;">
            <p style="margin: 0 0 5px 0; color: #999; font-size: 11px;">Total CBD Projetado</p>
            <p style="margin: 0; font-weight: bold; font-size: 16px; color: #1b7c4a;">${summary.total_cbd_projected_mg.toFixed(0)} mg</p>
        </div>
        <div style="background: #f0f0f0; padding: 10px; border-radius: 5px; text-align: center;">
            <p style="margin: 0 0 5px 0; color: #999; font-size: 11px;">Garrafas Previstas</p>
            <p style="margin: 0; font-weight: bold; font-size: 16px; color: #1b7c4a;">${summary.total_bottles_projected.toFixed(0)}</p>
        </div>
        <div style="background: #f0f0f0; padding: 10px; border-radius: 5px; text-align: center;">
            <p style="margin: 0 0 5px 0; color: #999; font-size: 11px;">Custo Total 24 Meses</p>
            <p style="margin: 0; font-weight: bold; font-size: 16px; color: #1b7c4a;">R$ ${summary.total_cost_projected_brl.toFixed(2)}</p>
        </div>
    `;
    
    // Display monthly projections
    const monthsTable = document.getElementById('judicial-months');
    monthsTable.innerHTML = '';
    
    // Show every 3 months for readability
    cannabisData.projection_24_months.forEach((month, idx) => {
        if (month.month % 3 === 0 || month.month === 1) {
            const row = `
                <tr style="border: 1px solid #ddd;">
                    <td style="padding: 6px;">Mês ${month.month}</td>
                    <td style="padding: 6px; text-align: right;">${month.cbd_mg_daily.toFixed(1)} mg</td>
                    <td style="padding: 6px; text-align: right;">${month.ml_per_month.toFixed(1)} mL</td>
                    <td style="padding: 6px; text-align: right;">R$ ${month.monthly_cost_brl.toFixed(2)}</td>
                </tr>
            `;
            monthsTable.innerHTML += row;
        }
    });
}

// Toggle exam type
function toggleExamType(type) {
    const btn1 = document.getElementById('exam-lab-btn');
    const btn2 = document.getElementById('exam-genetic-btn');
    
    if (type === 'laboratorial') {
        btn1.style.background = '#1b7c4a';
        btn1.style.color = 'white';
        btn2.style.background = 'white';
        btn2.style.color = '#333';
        cannabisData.exams.laboratorial = DEFAULT_LAB_EXAMS;
        displayExamList(DEFAULT_LAB_EXAMS);
    } else {
        btn2.style.background = '#1b7c4a';
        btn2.style.color = 'white';
        btn1.style.background = 'white';
        btn1.style.color = '#333';
        cannabisData.exams.genetic = DEFAULT_GENETIC_EXAMS;
        displayExamList(DEFAULT_GENETIC_EXAMS);
    }
}

// Display exam list
function displayExamList(exams) {
    const listDiv = document.getElementById('exam-list');
    listDiv.innerHTML = '';
    
    exams.forEach(exam => {
        const checkbox = `
            <label style="display: flex; align-items: center; gap: 8px; padding: 8px; background: white; border-radius: 5px; cursor: pointer; border: 1px solid #eee;">
                <input type="checkbox" checked style="width: 16px; height: 16px; cursor: pointer;" />
                <span style="color: #333; font-size: 13px;">${exam}</span>
            </label>
        `;
        listDiv.innerHTML += checkbox;
    });
}

// Sign prescription with VidaaS
async function signCannabisRx() {
    alert('🔒 Integração com VidaaS será realizada aqui. Por enquanto, prescription será salva como rascunho.');
    saveDraft();
}

// Save draft
async function saveDraft() {
    if (!cannabisData.prescription) {
        alert('⚠️ Nenhuma prescrição gerada. Selecione um produto primeiro.');
        return;
    }
    
    try {
        const response = await fetch('/api/cannabis/prescriptions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                product_id: cannabisData.selected_product,
                patient_id: getCurrentPatientId(),
                doctor_id: getCurrentDoctorId(),
                patient_name: cannabisData.prescription.patient_name,
                patient_diagnosis: cannabisData.prescription.patient_diagnosis,
                medical_indication: cannabisData.prescription.medical_indication,
                clinical_findings: document.getElementById('cannabis-notes').value
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`✅ Prescrição salva! ID: ${data.prescription_id}`);
            console.log('PDFs gerados:', data.pdf_paths);
        }
    } catch (error) {
        console.error('Erro ao salvar:', error);
        alert('❌ Erro ao salvar prescrição.');
    }
}

// Update product selection
function updateCannabisProduct() {
    const select = document.getElementById('cannabis-product-select');
    cannabisData.selected_product = select.value;
}

// Initialize on load
function initCannabisModule() {
    loadCannabisProducts();
    toggleExamType('laboratorial');  // Default to lab exams
}

// Helper functions (to be integrated with your app)
function getCurrentPatientId() {
    // Return current patient ID from your session/context
    return 'patient_' + new Date().getTime();
}

function getCurrentDoctorId() {
    // Return current doctor ID from your session/context
    return 'doctor_' + new Date().getTime();
}

// Call init when module is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCannabisModule);
} else {
    initCannabisModule();
}
</script>
"""


# JavaScript for integrating with video consultation
VIDEO_CONSULTATION_INTEGRATION = """
// When opening consultation with a patient
async function openConsultationWithCannabis(patientData, consultationId) {
    // Show cannabis panel
    document.getElementById('cannabis-panel').style.display = 'block';
    
    // Pre-fill patient data
    if (patientData.diagnosis) {
        document.getElementById('cannabis-patient-diagnosis').value = patientData.diagnosis;
    }
    
    // Load patient's previous exams
    await loadPatientExams(patientData.id);
    
    // Load any active prescriptions
    await loadActivePrescrriptions(patientData.id);
}

// Load patient exams into container
async function loadPatientExams(patientId) {
    try {
        const response = await fetch(`/api/cannabis/patient-exams/${patientId}`);
        const data = await response.json();
        
        if (data.success) {
            console.log('Patient exams:', data.exams);
            // Display in exam container panel
        }
    } catch (error) {
        console.error('Error loading exams:', error);
    }
}

// Load active prescriptions for patient
async function loadActivePrescrriptions(patientId) {
    try {
        const response = await fetch(`/api/cannabis/prescriptions?patient_id=${patientId}`);
        const data = await response.json();
        
        if (data.success && data.prescriptions.length > 0) {
            console.log('Active prescriptions:', data.prescriptions);
            // Display in sidebar
        }
    } catch (error) {
        console.error('Error loading prescriptions:', error);
    }
}

// Export prescription to PDF for printing
async function exportCannabisRxPDF(prescriptionId) {
    try {
        const response = await fetch(`/api/cannabis/prescriptions/${prescriptionId}`);
        const data = await response.json();
        
        if (data.success) {
            // Generate PDF download
            const link = document.createElement('a');
            link.href = `/prescriptions/RX_${prescriptionId}.pdf`;
            link.download = `Receita_${prescriptionId}.pdf`;
            link.click();
        }
    } catch (error) {
        console.error('Error exporting PDF:', error);
    }
}
"""
