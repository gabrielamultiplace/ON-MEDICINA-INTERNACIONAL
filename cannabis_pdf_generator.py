"""
PDF GENERATORS FOR CANNABIS MEDICINAL MODULE
============================================
Creates professional PDFs for:
- Prescription (Receita)
- Medical Report (Laudo)  
- Lab Exam Requests (Requisição de Exames)

Matches the visual style from provided models.
"""

from datetime import datetime
from typing import Dict, List, Optional
import os
import json


class PrescriptionPDFGenerator:
    """Generate prescription PDF matching the provided model."""
    
    @staticmethod
    def generate_rx_html(prescription_data: Dict, titulation_weeks: List[Dict]) -> str:
        """
        Generate HTML for prescription that can be converted to PDF.
        Uses FPDF2 or similar library.
        """
        
        created_date = prescription_data['created_at'][:10]
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Receita - {prescription_data['patient_name']}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: white;
                }}
                .header {{
                    background-color: #1b7c4a;
                    color: white;
                    padding: 15px;
                    text-align: center;
                    margin-bottom: 20px;
                    border-radius: 5px;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    border: 1px solid #ddd;
                    padding: 20px;
                }}
                .patient-info {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                    margin-bottom: 20px;
                }}
                .info-block {{
                    border-bottom: 1px solid #eee;
                    padding-bottom: 10px;
                }}
                .info-block label {{
                    font-weight: bold;
                    color: #333;
                    font-size: 12px;
                    text-transform: uppercase;
                }}
                .info-block p {{
                    margin: 5px 0;
                    font-size: 14px;
                }}
                .prescription-section {{
                    margin: 20px 0;
                    padding: 15px;
                    background-color: #f9f9f9;
                    border-left: 4px solid #1b7c4a;
                }}
                .prescription-section h2 {{
                    margin: 0 0 15px 0;
                    font-size: 16px;
                    color: #1b7c4a;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 15px 0;
                }}
                th {{
                    background-color: #1b7c4a;
                    color: white;
                    padding: 10px;
                    text-align: left;
                    font-size: 12px;
                }}
                td {{
                    border: 1px solid #ddd;
                    padding: 10px;
                    font-size: 13px;
                }}
                .titulation-note {{
                    color: #d9534f;
                    font-weight: bold;
                    margin: 10px 0;
                    padding: 10px;
                    background-color: #fcf8f8;
                    border-left: 3px solid #d9534f;
                }}
                .footer {{
                    margin-top: 30px;
                    text-align: center;
                    border-top: 1px solid #ddd;
                    padding-top: 20px;
                    font-size: 12px;
                }}
                .signature-area {{
                    display: flex;
                    justify-content: space-around;
                    margin-top: 30px;
                }}
                .signature-block {{
                    text-align: center;
                    width: 40%;
                }}
                .signature-line {{
                    border-top: 1px solid #000;
                    width: 100%;
                    margin: 50px 0 5px 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🏥 ON Medicina Internacional</h1>
                <p>RECEITUÁRIO MÉDICO - CANNABIS MEDICINAL</p>
            </div>
            
            <div class="container">
                <!-- PATIENT INFORMATION -->
                <div class="patient-info">
                    <div class="info-block">
                        <label>Paciente</label>
                        <p>{prescription_data['patient_name']}</p>
                    </div>
                    <div class="info-block">
                        <label>Data</label>
                        <p>{created_date}</p>
                    </div>
                    <div class="info-block">
                        <label>Diagnóstico</label>
                        <p>{prescription_data['patient_diagnosis']}</p>
                    </div>
                    <div class="info-block">
                        <label>Indicação Médica</label>
                        <p>{prescription_data['medical_indication']}</p>
                    </div>
                </div>
                
                <!-- PRESCRIPTION HEADER -->
                <div style="border-bottom: 3px solid #1b7c4a; margin-bottom: 20px; padding-bottom: 10px;">
                    <h3 style="margin: 0; color: #333;">Prescrição</h3>
                </div>
                
                <!-- MEDICATION TABLE -->
                <table>
                    <thead>
                        <tr>
                            <th>Medicamento/Produto</th>
                            <th>Posologia/Instruções</th>
                            <th>Qtd.</th>
                            <th>Duração</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>
                                <strong>{prescription_data['product']['name']}</strong><br>
                                CBD: {prescription_data['product']['cbd_mg_ml']} mg/mL<br>
                                Concentração: {prescription_data['product']['volume_ml']}mL
                            </td>
                            <td>
                                <strong>TITULAÇÃO (ESCADINHA DE DOSAGEM):</strong><br><br>
                                {format_titulation_table(titulation_weeks)}
                            </td>
                            <td>6 frascos</td>
                            <td>6 meses</td>
                        </tr>
                    </tbody>
                </table>
                
                <!-- IMPORTANT NOTES -->
                <div class="titulation-note">
                    ⚠️ ATENÇÃO: Cannabis Medicinal requer TITULAÇÃO progressiva (escadinha de dosagem).
                    Não é uma dose fixa. Aumentar gradualmente conforme tolerância. 
                    Avaliar resposta clínica a cada semana.
                </div>
                
                <!-- CLINICAL NOTES -->
                <div class="prescription-section">
                    <h2>Observações Gerais</h2>
                    <p>• Uso exclusivamente medicinal</p>
                    <p>• Armazenar em local fresco e escuro</p>
                    <p>• Proteger de luz e calor</p>
                    <p>• Validade: 24 meses conforme projeção judicial</p>
                    <p>• Paciente deve reportar qualquer efeito colateral</p>
                    <p>• Consultas de acompanhamento: a cada 2 semanas durante titulação, depois mensais</p>
                </div>
                
                <!-- LEGAL REQUIREMENT -->
                <div class="prescription-section" style="border-left-color: #d9534f;">
                    <h2 style="color: #d9534f;">Requisito Judicial</h2>
                    <p><strong>Projeção de 24 meses:</strong> Esta prescrição é válida por até 24 meses, 
                    com prorrogação sujeita a reavalições clínicas. Calculado para fins de defesa judicial 
                    conforme protocolos ANVISA.</p>
                </div>
                
                <!-- DOCTOR SIGNATURE AREA -->
                <div class="signature-area">
                    <div class="signature-block">
                        <div class="signature-line"></div>
                        <p>Assinatura do Médico</p>
                        <p style="font-size: 11px; margin-top: 10px;">CRM</p>
                    </div>
                    <div class="signature-block">
                        <p style="margin-top: 0;">🔒 Assinado Digitalmente</p>
                        <p style="font-size: 11px;">Via VidaaS ou DocuSign</p>
                    </div>
                </div>
                
                <!-- FOOTER -->
                <div class="footer">
                    <p>Receita Eletrônica | Prescrição ID: {prescription_data['prescription_id']}</p>
                    <p style="color: #999;">Gerada automaticamente pelo Sistema ON - Cannabis Medicinal</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    @staticmethod
    def generate_rx_pdf(prescription_data: Dict, titulation_weeks: List[Dict], 
                       output_path: str = None) -> str:
        """Generate PDF file from prescription data."""
        try:
            from fpdf import FPDF
            
            # Create PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=10)
            
            # Header
            pdf.set_fill_color(27, 124, 74)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(0, 15, "ON Medicina Internacional - RECEITUÁRIO MÉDICO", 0, 1, 'C', fill=True)
            pdf.set_text_color(0, 0, 0)
            
            pdf.ln(5)
            
            # Patient info
            pdf.set_font("Arial", "B", size=11)
            pdf.cell(60, 7, "PACIENTE:", 0, 0)
            pdf.set_font("Arial", size=10)
            pdf.cell(0, 7, prescription_data['patient_name'], 0, 1)
            
            pdf.set_font("Arial", "B", size=11)
            pdf.cell(60, 7, "DIAGNÓSTICO:", 0, 0)
            pdf.set_font("Arial", size=10)
            pdf.cell(0, 7, prescription_data['patient_diagnosis'], 0, 1)
            
            pdf.ln(5)
            
            # Prescription table
            pdf.set_font("Arial", "B", size=10)
            pdf.set_fill_color(27, 124, 74)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(80, 8, "Medicamento", 1, 0, fill=True)
            pdf.cell(50, 8, "Posologia", 1, 0, fill=True)
            pdf.cell(30, 8, "Qtd.", 1, 0, fill=True)
            pdf.cell(30, 8, "Duração", 1, 1, fill=True)
            
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", size=9)
            
            # Product info
            pdf.cell(80, 8, prescription_data['product']['name'], 1)
            pdf.cell(50, 8, "Titulação 6 semanas", 1)
            pdf.cell(30, 8, "6 frascos", 1)
            pdf.cell(30, 8, "6 meses", 1, 1)
            
            pdf.ln(5)
            
            # Titulation table
            pdf.set_font("Arial", "B", size=9)
            pdf.cell(0, 8, "TITULAÇÃO (Escadinha de Dosagem)", 0, 1)
            
            pdf.set_font("Arial", "B", size=8)
            pdf.set_fill_color(200, 200, 200)
            pdf.cell(20, 6, "Sem.", 1, 0, fill=True)
            pdf.cell(25, 6, "Gotas", 1, 0, fill=True)
            pdf.cell(25, 6, "Freq.", 1, 0, fill=True)
            pdf.cell(30, 6, "CBD/dia", 1, 1, fill=True)
            
            pdf.set_font("Arial", size=8)
            for week in titulation_weeks:
                pdf.cell(20, 6, f"S{week['week']}", 1, 0)
                pdf.cell(25, 6, str(week['drops_per_dose']), 1, 0)
                pdf.cell(25, 6, f"{week['times_per_day']}x", 1, 0)
                pdf.cell(30, 6, f"{week['cbd_mg_per_day']:.1f}mg", 1, 1)
            
            pdf.ln(5)
            
            # Legal note
            pdf.set_font("Arial", "B", size=9)
            pdf.set_fill_color(255, 240, 240)
            pdf.cell(0, 8, "Validade: 24 MESES (Requisito Judicial)", 1, 1, fill=True)
            
            # Save PDF
            if output_path is None:
                output_path = f"prescriptions/RX_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            pdf.output(output_path)
            
            return output_path
        
        except ImportError:
            # Fallback: return HTML for now
            return prescription_data['prescription_id']


def format_titulation_table(titulation_weeks: List[Dict]) -> str:
    """Format titulation weeks as HTML table."""
    html = "<table style='width:100%; font-size:11px; margin:5px 0;'>"
    
    for week in titulation_weeks:
        html += f"""
        <tr>
            <td style='padding:3px; border-bottom:1px solid #ddd;'>
                <strong>SEMANA {week['week']}</strong> - {week['drops_per_dose']} GOTAS DE {int(12/week['times_per_day'])} EM {int(12/week['times_per_day'])} HORAS
            </td>
            <td style='padding:3px; border-bottom:1px solid #ddd; text-align:right;'>
                {week['cbd_mg_per_day']:.1f}mg CBD/dia
            </td>
        </tr>
        """
    
    html += "</table>"
    return html


class MedicalReportPDFGenerator:
    """Generate Medical Report (Laudo) PDF for judicial defense."""
    
    @staticmethod
    def generate_laudo_html(patient_name: str, doctor_name: str, doctor_crm: str,
                           prescription_data: Dict, clinical_findings: str) -> str:
        """Generate HTML for medical report."""
        
        created_date = datetime.now().strftime('%d/%m/%Y')
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <title>Laudo Médico - {patient_name}</title>
            <style>
                body {{
                    font-family: Calibri, Arial, sans-serif;
                    margin: 0;
                    padding: 30px;
                    line-height: 1.6;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    border-bottom: 2px solid #1b7c4a;
                    padding-bottom: 15px;
                }}
                .logo {{
                    font-size: 14px;
                    font-weight: bold;
                    color: #1b7c4a;
                }}
                .title {{
                    font-size: 16px;
                    font-weight: bold;
                    margin: 10px 0;
                }}
                .doctor-info {{
                    text-align: center;
                    font-size: 12px;
                    margin-bottom: 20px;
                }}
                .section {{
                    margin: 20px 0;
                }}
                .section-title {{
                    font-weight: bold;
                    font-size: 13px;
                    text-transform: uppercase;
                    color: #1b7c4a;
                    border-bottom: 1px solid #1b7c4a;
                    padding-bottom: 5px;
                    margin-bottom: 10px;
                }}
                p {{
                    margin: 5px 0;
                    text-align: justify;
                }}
                .exam-list {{
                    display: grid;
                    grid-template-columns: 1fr 1fr 1fr;
                    gap: 10px;
                    margin: 10px 0;
                }}
                .exam-item {{
                    padding: 8px;
                    border: 1px solid #ddd;
                    font-size: 12px;
                }}
                .signature-area {{
                    margin-top: 50px;
                    text-align: center;
                }}
                .signature-line {{
                    border-top: 1px solid #000;
                    width: 250px;
                    margin: 50px auto 5px;
                }}
                .cannabis-logo {{
                    opacity: 0.1;
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    font-size: 200px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="logo">🏥 ON - Medicina Internacional</div>
                <div class="title">LAUDO MÉDICO</div>
                <div class="doctor-info">
                    <strong>{doctor_name}</strong><br>
                    CRM: {doctor_crm}
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">Dados do Paciente</div>
                <p><strong>Nome:</strong> {patient_name}</p>
                <p><strong>Data do Laudo:</strong> {created_date}</p>
                <p><strong>Diagnóstico Principal:</strong> {prescription_data['patient_diagnosis']}</p>
                <p><strong>Indicação Médica:</strong> {prescription_data['medical_indication']}</p>
            </div>
            
            <div class="section">
                <div class="section-title">Prescrição</div>
                <p><strong>Medicamento:</strong> {prescription_data['product']['name']}</p>
                <p><strong>Marca/Fornecedor:</strong> {prescription_data['product']['brand']}</p>
                <p><strong>Concentração CBD:</strong> {prescription_data['product']['cbd_mg_ml']} mg/mL</p>
                <p><strong>Concentração THC:</strong> {prescription_data['product']['thc_mg_ml']} mg/mL</p>
                <p><strong>Dosagem Inicial:</strong> {prescription_data['initial_cbd_mg_daily']:.2f}mg CBD/dia</p>
                <p><strong>Frequência:</strong> {prescription_data['frequency_initial']}</p>
            </div>
            
            <div class="section">
                <div class="section-title">Achados Clínicos</div>
                <p>{clinical_findings}</p>
            </div>
            
            <div class="section">
                <div class="section-title">Exames Recomendados</div>
                <div class="exam-list">
                    <div class="exam-item">Ácido Fólico</div>
                    <div class="exam-item">Ácido Úrico</div>
                    <div class="exam-item">Colesterol Total e Frações</div>
                    <div class="exam-item">CPK</div>
                    <div class="exam-item">Creatinina</div>
                    <div class="exam-item">Glicose</div>
                    <div class="exam-item">Glicohemoglobina</div>
                    <div class="exam-item">Hemograma Completo</div>
                    <div class="exam-item">Triglicerídeos</div>
                    <div class="exam-item">TSH/T4/T3</div>
                    <div class="exam-item">Ureia</div>
                    <div class="exam-item">Vitaminas (B6, B12, D)</div>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">Justificativa Judicial</div>
                <p>Esta prescrição de Cannabis Medicinal é indicada conforme protocolos ANVISA 
                e recomendações internacionais de uso terapêutico. A projeção de 24 meses é 
                estabelecida para fins de defesa judicial, garantindo continuidade do tratamento 
                em casos de recursos legais. O paciente será acompanhado regularmente para avaliar 
                resposta terapêutica e ajustes posológicos.</p>
            </div>
            
            <div class="signature-area">
                <div class="signature-line"></div>
                <p><strong>{doctor_name}</strong></p>
                <p>CRM: {doctor_crm}</p>
                <p style="font-size:11px; margin-top:20px;">🔒 Assinado Digitalmente via VidaaS</p>
            </div>
        </body>
        </html>
        """
        
        return html_content


class ExamRequestPDFGenerator:
    """Generate Exam Request PDFs (Lab & Genetic)."""
    
    @staticmethod
    def generate_exam_request_html(patient_name: str, doctor_name: str, doctor_crm: str,
                                   exam_type: str = "Laboratorial",
                                   exam_list: List[str] = None) -> str:
        """Generate HTML for exam request."""
        
        if exam_list is None:
            if exam_type == "Laboratorial":
                exam_list = [
                    "Ácido Fólico", "Ácido Úrico", "Colesterol Total e Frações",
                    "CPK", "Creatinina", "Feminina", "Ferro Sérico", "Fosfatase Alcalina",
                    "Glicose", "Glicohemoglobina", "GIPD", "Hemograma", "Homocisteína",
                    "Insulina", "Proteína C Reativa", "TSH", "Triglicerídeos", "TSH T4/T3",
                    "Ureia", "VIT. B6/B12 e D"
                ]
            else:  # Genético
                exam_list = ["Teste Genético Completo", "Análise de Variantes Relevantes"]
        
        created_date = datetime.now().strftime('%d/%m/%Y')
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <title>Solicitação de Exames - {patient_name}</title>
            <style>
                body {{
                    font-family: Calibri, Arial, sans-serif;
                    margin: 30px;
                    line-height: 1.5;
                }}
                .header {{
                    background: linear-gradient(135deg, #1b7c4a 0%, #0d5a36 100%);
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 18px;
                }}
                .logo {{
                    font-size: 14px;
                    margin-bottom: 10px;
                }}
                .content {{
                    border: 1px solid #ddd;
                    padding: 20px;
                    margin-bottom: 20px;
                }}
                .info-row {{
                    display: flex;
                    margin: 10px 0;
                }}
                .info-label {{
                    width: 150px;
                    font-weight: bold;
                }}
                .info-value {{
                    flex: 1;
                }}
                .exam-title {{
                    font-weight: bold;
                    margin-top: 15px;
                    margin-bottom: 10px;
                    text-transform: uppercase;
                    color: #1b7c4a;
                }}
                .exam-list {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 10px;
                }}
                .exam-item {{
                    flex: 0 1 calc(50% - 5px);
                    padding: 8px;
                    border: 1px solid #ddd;
                    background-color: #f9f9f9;
                    font-size: 13px;
                }}
                .signature {{
                    margin-top: 50px;
                    text-align: center;
                }}
                .signature-line {{
                    border-top: 1px solid #000;
                    width: 250px;
                    margin: 50px auto 5px;
                }}
                .footer {{
                    font-size: 11px;
                    text-align: center;
                    color: #999;
                    margin-top: 30px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="logo">🏥 ON-Medicina Internacional</div>
                <h1>SOLICITAÇÃO DE EXAMES {exam_type.upper()}</h1>
            </div>
            
            <div class="content">
                <div class="info-row">
                    <span class="info-label"><strong>Médico:</strong></span>
                    <span class="info-value">{doctor_name}</span>
                </div>
                <div class="info-row">
                    <span class="info-label"><strong>CRM:</strong></span>
                    <span class="info-value">{doctor_crm}</span>
                </div>
                <div class="info-row">
                    <span class="info-label"><strong>Data:</strong></span>
                    <span class="info-value">{created_date}</span>
                </div>
                
                <hr style="margin: 15px 0; border: none; border-top: 1px solid #ddd;">
                
                <div class="info-row">
                    <span class="info-label"><strong>Paciente:</strong></span>
                    <span class="info-value">{patient_name}</span>
                </div>
                <div class="info-row">
                    <span class="info-label"><strong>Tipo de Exame:</strong></span>
                    <span class="info-value">{exam_type}</span>
                </div>
                
                <div class="exam-title">Exames Solicitados:</div>
                <div class="exam-list">
        """
        
        for exam in exam_list:
            html_content += f'<div class="exam-item">✓ {exam}</div>'
        
        html_content += f"""
                </div>
            </div>
            
            <div class="signature">
                <div class="signature-line"></div>
                <p><strong>{doctor_name}</strong></p>
                <p>CRM: {doctor_crm}</p>
                <p style="margin-top: 20px; font-size: 10px;">🔒 Assinado Digitalmente</p>
            </div>
            
            <div class="footer">
                <p>Requisição de Exames | Gerada automaticamente pelo Sistema ON - Cannabis Medicinal</p>
            </div>
        </body>
        </html>
        """
        
        return html_content


# Export functions
def generate_all_pdfs(prescription_data: Dict, titulation_weeks: List[Dict],
                     patient_info: Dict, doctor_info: Dict,
                     clinical_findings: str = "",
                     output_dir: str = "prescriptions") -> Dict[str, str]:
    """Generate all three PDFs for a prescription."""
    
    paths = {
        'prescription': None,
        'laudo': None,
        'exam_laboratorial': None,
        'exam_genetic': None
    }
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate Prescription PDF
        rx_html = PrescriptionPDFGenerator.generate_rx_html(prescription_data, titulation_weeks)
        rx_path = f"{output_dir}/RX_{prescription_data['prescription_id']}.html"
        with open(rx_path, 'w', encoding='utf-8') as f:
            f.write(rx_html)
        paths['prescription'] = rx_path
        
        # Generate Medical Report PDF
        laudo_html = MedicalReportPDFGenerator.generate_laudo_html(
            patient_info['name'],
            doctor_info['name'],
            doctor_info['crm'],
            prescription_data,
            clinical_findings or "Paciente apresenta indicação clínica para Cannabis Medicinal conforme ANVISA."
        )
        laudo_path = f"{output_dir}/LAUDO_{prescription_data['prescription_id']}.html"
        with open(laudo_path, 'w', encoding='utf-8') as f:
            f.write(laudo_html)
        paths['laudo'] = laudo_path
        
        # Generate Lab Exam Request PDF
        exam_lab_html = ExamRequestPDFGenerator.generate_exam_request_html(
            patient_info['name'],
            doctor_info['name'],
            doctor_info['crm'],
            'Laboratorial'
        )
        exam_lab_path = f"{output_dir}/EXAME_LAB_{prescription_data['prescription_id']}.html"
        with open(exam_lab_path, 'w', encoding='utf-8') as f:
            f.write(exam_lab_html)
        paths['exam_laboratorial'] = exam_lab_path
        
        # Generate Genetic Exam Request PDF
        exam_genetic_html = ExamRequestPDFGenerator.generate_exam_request_html(
            patient_info['name'],
            doctor_info['name'],
            doctor_info['crm'],
            'Genético',
            ["Teste Genético Completo", "Análise de Variantes Relevantes"]
        )
        exam_genetic_path = f"{output_dir}/EXAME_GENETICO_{prescription_data['prescription_id']}.html"
        with open(exam_genetic_path, 'w', encoding='utf-8') as f:
            f.write(exam_genetic_html)
        paths['exam_genetic'] = exam_genetic_path
        
    except Exception as e:
        print(f"Error generating PDFs: {e}")
    
    return paths
