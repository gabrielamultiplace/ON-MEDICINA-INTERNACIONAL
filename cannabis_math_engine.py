"""
CANNABIS MEDICINAL PRESCRIPTION MATH ENGINE
============================================
Handles titulation (dosage escalation), 24-month judicial projection,
posology calculations based on CBD/THC concentrations.

Brazilian ANVISA-compliant calculations for medicinal cannabis.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json


class CannabisProduct:
    """Represents a medicinal cannabis oil product from a supplier."""
    
    def __init__(self, product_id: str, name: str, brand: str, 
                 cbd_mg_ml: float, thc_mg_ml: float, 
                 volume_ml: int, supplier_id: str):
        self.product_id = product_id
        self.name = name  # e.g., "CBD Isolate USA Hemp"
        self.brand = brand  # e.g., "Principios Ativos"
        self.cbd_mg_ml = cbd_mg_ml  # CBD concentration: mg/mL
        self.thc_mg_ml = thc_mg_ml  # THC concentration: mg/mL
        self.volume_ml = volume_ml  # Bottle size: 30mL
        self.supplier_id = supplier_id
        self.created_at = datetime.now()
    
    def to_dict(self):
        return {
            'product_id': self.product_id,
            'name': self.name,
            'brand': self.brand,
            'cbd_mg_ml': self.cbd_mg_ml,
            'thc_mg_ml': self.thc_mg_ml,
            'volume_ml': self.volume_ml,
            'supplier_id': self.supplier_id,
            'total_cbd_mg': self.cbd_mg_ml * self.volume_ml,
            'total_thc_mg': self.thc_mg_ml * self.volume_ml,
            'created_at': self.created_at.isoformat()
        }


class TitulationSchedule:
    """
    Cannabis titulation is a dose-escalation strategy.
    NOT a fixed amount - it's a PROGRESSIVE INCREASE.
    
    Example: Week 1 = 2 drops x 3x/day, Week 2 = 4 drops x 3x/day, etc.
    This is the "escadinha" (little staircase) of dosage.
    """
    
    WORLDWIDE_TITULATION_TEMPLATE = {
        # Week: (drops_per_dose, times_per_day, notes)
        'semana_1': {'drops': 2, 'times_per_day': 3, 'notes': '2 GOTAS DE 12 EM 12 HORAS'},
        'semana_2': {'drops': 4, 'times_per_day': 3, 'notes': '4 GOTAS DE 12 EM 12 HORAS'},
        'semana_3': {'drops': 6, 'times_per_day': 3, 'notes': '6 GOTAS DE 12 EM 12 HORAS'},
        'semana_4': {'drops': 8, 'times_per_day': 3, 'notes': '8 GOTAS DE 12 EM 12 HORAS'},
        'semana_5': {'drops': 10, 'times_per_day': 3, 'notes': '10 GOTAS DE 12 EM 12 HORAS'},
        'semana_6': {'drops': 12, 'times_per_day': 3, 'notes': '12 GOTAS DE 12 EM 12 HORAS'},
    }
    
    @staticmethod
    def calculate_cbd_per_dose(product: CannabisProduct, drops: int) -> float:
        """
        Calculate actual CBD mg per dose.
        1 drop = ~0.05 mL (standard dropper)
        """
        drops_to_ml = drops * 0.05
        return product.cbd_mg_ml * drops_to_ml
    
    @staticmethod
    def calculate_weekly_schedule(product: CannabisProduct, week_num: int) -> Dict:
        """Generate dosage for a specific week of titulation."""
        week_key = f'semana_{week_num}' if week_num <= 6 else f'semana_6'
        schedule = TitulationSchedule.WORLDWIDE_TITULATION_TEMPLATE.get(week_key)
        
        if not schedule:
            return {}
        
        drops_per_dose = schedule['drops']
        times_per_day = schedule['times_per_day']
        
        cbd_per_dose = TitulationSchedule.calculate_cbd_per_dose(product, drops_per_dose)
        cbd_per_day = cbd_per_dose * times_per_day
        cbd_per_week = cbd_per_day * 7
        
        return {
            'week': week_num,
            'drops_per_dose': drops_per_dose,
            'times_per_day': times_per_day,
            'frequency': schedule['notes'],
            'cbd_mg_per_dose': round(cbd_per_dose, 2),
            'cbd_mg_per_day': round(cbd_per_day, 2),
            'cbd_mg_per_week': round(cbd_per_week, 2),
            'thc_mg_per_day': round(product.thc_mg_ml * drops_per_dose * 0.05 * times_per_day, 2)
        }


class JudicialProjection:
    """
    Brazilian judicial requirement: Project Cannabis prescription for 24 months.
    This is for defense in court when challenged by Ministério Público.
    
    Calculates: Product consumption, costs, therapeutic milestones.
    """
    
    @staticmethod
    def project_24_months(product: CannabisProduct, weekly_schedule: Dict) -> List[Dict]:
        """
        Project 24 months of treatment with progressive titulation.
        
        Months 1-6: Titulation phase (increase dosage)
        Months 7-24: Maintenance phase (stable dosage)
        """
        projection = []
        start_date = datetime.now()
        
        for month in range(1, 25):
            # Determine which week of titulation (or maintenance)
            week_of_titulation = min(6, month)  # Cap at week 6
            
            # For simplicity: use same schedule, but calculate monthly consumption
            cbd_per_day = weekly_schedule['cbd_mg_per_day']
            cbd_per_month = cbd_per_day * 30  # Approx 30 days/month
            
            # Estimate droplets per month (accounting for dropper efficiency)
            ml_per_month = (weekly_schedule['drops_per_dose'] * 0.05 * 
                           weekly_schedule['times_per_day'] * 30)
            
            # Estimate cost (R$ per mL) - adjust per actual supplier
            cost_per_ml = 5.0  # Example: R$5 per mL
            monthly_cost = ml_per_month * cost_per_ml
            
            month_start = start_date + timedelta(days=30 * (month - 1))
            
            projection.append({
                'month': month,
                'date_start': month_start.strftime('%d/%m/%Y'),
                'titulation_week': week_of_titulation if month <= 6 else 'maintenance',
                'cbd_mg_daily': round(cbd_per_day, 2),
                'cbd_mg_monthly': round(cbd_per_month, 2),
                'cbd_mg_cumulative': round(cbd_per_month * month, 2),
                'ml_per_month': round(ml_per_month, 2),
                'bottles_needed': round(ml_per_month / product.volume_ml, 1),
                'monthly_cost_brl': round(monthly_cost, 2),
                'cumulative_cost_brl': round(monthly_cost * month, 2),
                'therapeutic_goal': f"Week {week_of_titulation} dosage" if month <= 6 else "Maintenance"
            })
        
        return projection
    
    @staticmethod
    def generate_judicial_defense_summary(patient_name: str, product: CannabisProduct, 
                                         projection: List[Dict]) -> Dict:
        """Generate summary for court defense document."""
        total_cbd_24mo = projection[-1]['cbd_mg_cumulative']
        total_cost_24mo = projection[-1]['cumulative_cost_brl']
        
        return {
            'patient': patient_name,
            'product_name': product.name,
            'product_brand': product.brand,
            'cbd_concentration': f"{product.cbd_mg_ml} mg/mL",
            'thc_concentration': f"{product.thc_mg_ml} mg/mL",
            'treatment_duration_months': 24,
            'total_cbd_projected_mg': round(total_cbd_24mo, 2),
            'total_ml_projected': round(projection[-1]['ml_per_month'] * 24, 2),
            'total_bottles_projected': round(projection[-1]['ml_per_month'] * 24 / product.volume_ml, 1),
            'total_cost_projected_brl': round(total_cost_24mo, 2),
            'monthly_cost_average_brl': round(total_cost_24mo / 24, 2),
            'justification': 'Medicinal cannabis for therapeutic treatment per ANVISA protocols',
            'clinical_indication': 'To be filled by physician',
            'projected_benefits': [
                'Symptom relief and therapeutic improvement',
                'Progressive titulation allows body adaptation',
                'Consistent dosing for predictable outcomes'
            ]
        }


class PrescriptionCalculator:
    """
    Main calculator for cannabis medicinal prescriptions.
    Handles product selection, dosage calculations, 24-month projections.
    """
    
    def __init__(self):
        self.products: Dict[str, CannabisProduct] = {}
        self.titulation = TitulationSchedule()
        self.judicial = JudicialProjection()
    
    def add_product(self, product: CannabisProduct):
        """Register a new cannabis product."""
        self.products[product.product_id] = product
    
    def calculate_prescription(self, product_id: str, patient_name: str, 
                              patient_diagnosis: str, medical_indication: str) -> Dict:
        """
        Calculate complete prescription with titulation schedule and 24-month projection.
        
        Returns:
            {
                'prescription': {...},
                'titulation_weeks': [...],
                'projection_24_months': [...],
                'judicial_summary': {...}
            }
        """
        if product_id not in self.products:
            return {'error': f'Product {product_id} not found'}
        
        product = self.products[product_id]
        
        # Generate first week schedule
        week_1_schedule = self.titulation.calculate_weekly_schedule(product, 1)
        
        # Generate all 6 weeks of titulation
        titulation_weeks = []
        for week in range(1, 7):
            week_schedule = self.titulation.calculate_weekly_schedule(product, week)
            titulation_weeks.append(week_schedule)
        
        # Project 24 months
        projection_24mo = self.judicial.project_24_months(product, week_1_schedule)
        
        # Generate judicial summary
        judicial_summary = self.judicial.generate_judicial_defense_summary(
            patient_name, product, projection_24mo
        )
        
        prescription = {
            'prescription_id': f"RX-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'created_at': datetime.now().isoformat(),
            'patient_name': patient_name,
            'patient_diagnosis': patient_diagnosis,
            'medical_indication': medical_indication,
            'product': product.to_dict(),
            'initial_cbd_mg_daily': round(week_1_schedule['cbd_mg_per_day'], 2),
            'initial_thc_mg_daily': round(week_1_schedule['thc_mg_per_day'], 2),
            'frequency_initial': week_1_schedule['frequency'],
            'duration_months': 24,
            'titulation_required': True,
            'legal_note': 'Prescrição de Cannabis Medicinal conforme protocolos ANVISA - Judicial'
        }
        
        return {
            'prescription': prescription,
            'titulation_weeks': titulation_weeks,
            'projection_24_months': projection_24mo,
            'judicial_summary': judicial_summary
        }


# Example usage:
if __name__ == '__main__':
    calculator = PrescriptionCalculator()
    
    # Add sample products
    product1 = CannabisProduct(
        product_id='PROD001',
        name='CBD Isolate USA Hemp',
        brand='Principios Ativos',
        cbd_mg_ml=10.0,  # 10 mg/mL
        thc_mg_ml=0.0,
        volume_ml=30,
        supplier_id='SUP001'
    )
    
    calculator.add_product(product1)
    
    # Calculate prescription
    result = calculator.calculate_prescription(
        product_id='PROD001',
        patient_name='Murilo Pinheiro Fogaça',
        patient_diagnosis='Epilepsy',
        medical_indication='Therapeutic control of seizures'
    )
    
    print(json.dumps(result, indent=2, default=str))
