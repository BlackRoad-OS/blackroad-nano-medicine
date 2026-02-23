#!/usr/bin/env python3
"""
Nanomedicine drug delivery and treatment simulation system.
Simulates nanoparticle design, delivery, pharmacokinetics, and treatment planning.
"""

import os
import json
import sqlite3
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum
import uuid
import argparse
import math

# Database setup
DB_PATH = os.path.expanduser("~/.blackroad/nanomed.db")

class NanoparticleType(Enum):
    LIPOSOME = "liposome"
    POLYMERIC = "polymeric"
    METALLIC = "metallic"
    DENDRIMER = "dendrimer"
    QUANTUM_DOT = "quantum_dot"
    CARBON_NANOTUBE = "carbon_nanotube"

class DeliveryRoute(Enum):
    IV = "iv"
    ORAL = "oral"
    INHALATION = "inhalation"
    TOPICAL = "topical"
    INTRATUMORAL = "intratumoral"

class TreatmentStatus(Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    DISCONTINUED = "discontinued"

class Material(Enum):
    PLA = "pla"
    PLGA = "plga"
    CHITOSAN = "chitosan"
    GOLD = "gold"
    IRON_OXIDE = "iron_oxide"
    SILICA = "silica"
    LIPID = "lipid"

@dataclass
class Nanoparticle:
    id: str
    name: str
    type: str
    diameter_nm: float
    surface_charge_mv: float
    drug_payload: str
    encapsulation_pct: float
    targeting_ligand: str
    material: str
    created_at: str

@dataclass
class TreatmentPlan:
    id: str
    patient_id: str
    nanoparticle_id: str
    dose_mg_kg: float
    route: str
    frequency: str
    duration_days: int
    status: str
    efficacy_pct: float
    side_effects: List[str] = field(default_factory=list)

class NanoMedicineSystem:
    def __init__(self):
        self.db_path = DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database with required tables."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS nanoparticles (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            diameter_nm REAL NOT NULL,
            surface_charge_mv REAL NOT NULL,
            drug_payload TEXT NOT NULL,
            encapsulation_pct REAL NOT NULL,
            targeting_ligand TEXT,
            material TEXT NOT NULL,
            created_at TEXT NOT NULL
        )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS treatments (
            id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            nanoparticle_id TEXT NOT NULL,
            dose_mg_kg REAL NOT NULL,
            route TEXT NOT NULL,
            frequency TEXT NOT NULL,
            duration_days INTEGER NOT NULL,
            status TEXT NOT NULL,
            efficacy_pct REAL DEFAULT 0,
            side_effects TEXT DEFAULT '[]',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(nanoparticle_id) REFERENCES nanoparticles(id)
        )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS biodistribution (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nanoparticle_id TEXT NOT NULL,
            tissue TEXT NOT NULL,
            concentration_ug_ml REAL NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY(nanoparticle_id) REFERENCES nanoparticles(id)
        )''')
        
        conn.commit()
        conn.close()
    
    def design_nanoparticle(self, name: str, type_str: str, diameter_nm: float, 
                           drug_payload: str, material: str, targeting_ligand: str = "",
                           encapsulation_pct: float = 85) -> Nanoparticle:
        """Design a new nanoparticle formulation."""
        if type_str not in [t.value for t in NanoparticleType]:
            raise ValueError(f"Invalid type. Must be one of {[t.value for t in NanoparticleType]}")
        if material not in [m.value for m in Material]:
            raise ValueError(f"Invalid material. Must be one of {[m.value for m in Material]}")
        
        # Surface charge based on material
        charge_map = {
            "lipid": -10,
            "plga": -15,
            "pla": -12,
            "chitosan": 25,
            "gold": -8,
            "iron_oxide": -20,
            "silica": -25
        }
        
        surface_charge = charge_map.get(material, -10)
        np_id = f"NP_{uuid.uuid4().hex[:8].upper()}"
        
        np = Nanoparticle(
            id=np_id,
            name=name,
            type=type_str,
            diameter_nm=diameter_nm,
            surface_charge_mv=surface_charge,
            drug_payload=drug_payload,
            encapsulation_pct=encapsulation_pct,
            targeting_ligand=targeting_ligand,
            material=material,
            created_at=datetime.now().isoformat()
        )
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT INTO nanoparticles VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 tuple(asdict(np).values()))
        conn.commit()
        conn.close()
        
        return np
    
    def simulate_delivery(self, nanoparticle_id: str, target_tissue: str, dose_mg: float) -> Dict:
        """Simulate nanoparticle biodistribution."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM nanoparticles WHERE id = ?', (nanoparticle_id,))
        np_row = c.fetchone()
        conn.close()
        
        if not np_row:
            raise ValueError(f"Nanoparticle {nanoparticle_id} not found")
        
        # Simulate tissue distribution based on targeting
        tissue_distribution = {
            "liver": 35,
            "spleen": 25,
            "kidney": 15,
            "bone_marrow": 10,
            "tumor": 5,
            "other": 10
        }
        
        # If targeting ligand present, increase target tissue
        if np_row[7]:  # targeting_ligand
            tissue_distribution[target_tissue] = min(70, tissue_distribution.get(target_tissue, 10) + 40)
        
        # Normalize to 100%
        total = sum(tissue_distribution.values())
        biodist = {k: (v / total) * dose_mg * 1000 for k, v in tissue_distribution.items()}
        
        # Store in db
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        for tissue, conc in biodist.items():
            c.execute('''INSERT INTO biodistribution (nanoparticle_id, tissue, concentration_ug_ml, timestamp)
                        VALUES (?, ?, ?, ?)''',
                     (nanoparticle_id, tissue, conc, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        
        return biodist
    
    def create_treatment(self, patient_id: str, nanoparticle_id: str, dose_mg_kg: float,
                        route: str, duration_days: int, frequency: str = "daily") -> TreatmentPlan:
        """Create a treatment plan."""
        if route not in [r.value for r in DeliveryRoute]:
            raise ValueError(f"Invalid route. Must be one of {[r.value for r in DeliveryRoute]}")
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM nanoparticles WHERE id = ?', (nanoparticle_id,))
        if not c.fetchone():
            conn.close()
            raise ValueError(f"Nanoparticle {nanoparticle_id} not found")
        
        treatment_id = f"TX_{uuid.uuid4().hex[:8].upper()}"
        now = datetime.now().isoformat()
        
        treatment = TreatmentPlan(
            id=treatment_id,
            patient_id=patient_id,
            nanoparticle_id=nanoparticle_id,
            dose_mg_kg=dose_mg_kg,
            route=route,
            frequency=frequency,
            duration_days=duration_days,
            status=TreatmentStatus.PLANNED.value,
            efficacy_pct=0
        )
        
        c.execute('''INSERT INTO treatments 
                    (id, patient_id, nanoparticle_id, dose_mg_kg, route, frequency, duration_days, status, efficacy_pct, side_effects, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (treatment.id, treatment.patient_id, treatment.nanoparticle_id, treatment.dose_mg_kg,
                  treatment.route, treatment.frequency, treatment.duration_days, treatment.status,
                  treatment.efficacy_pct, json.dumps(treatment.side_effects), now, now))
        conn.commit()
        conn.close()
        
        return treatment
    
    def update_efficacy(self, treatment_id: str, efficacy_pct: float, side_effects: List[str] = None):
        """Update treatment efficacy and side effects."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        side_effects = side_effects or []
        c.execute('''UPDATE treatments SET efficacy_pct = ?, side_effects = ?, status = ?, updated_at = ?
                    WHERE id = ?''',
                 (efficacy_pct, json.dumps(side_effects), TreatmentStatus.ACTIVE.value, 
                  datetime.now().isoformat(), treatment_id))
        conn.commit()
        conn.close()
    
    def get_treatments(self, patient_id: Optional[str] = None, status: Optional[str] = None) -> List[TreatmentPlan]:
        """Retrieve treatment plans."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        query = 'SELECT * FROM treatments WHERE 1=1'
        params = []
        
        if patient_id:
            query += ' AND patient_id = ?'
            params.append(patient_id)
        if status:
            query += ' AND status = ?'
            params.append(status)
        
        c.execute(query, params)
        rows = c.fetchall()
        conn.close()
        
        treatments = []
        for row in rows:
            treatments.append(TreatmentPlan(
                id=row[0], patient_id=row[1], nanoparticle_id=row[2],
                dose_mg_kg=row[3], route=row[4], frequency=row[5],
                duration_days=row[6], status=row[7], efficacy_pct=row[8],
                side_effects=json.loads(row[9])
            ))
        return treatments
    
    def pharmacokinetics(self, nanoparticle_id: str, dose_mg: float) -> Dict:
        """Calculate pharmacokinetic parameters."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM nanoparticles WHERE id = ?', (nanoparticle_id,))
        np_row = c.fetchone()
        conn.close()
        
        if not np_row:
            raise ValueError(f"Nanoparticle {nanoparticle_id} not found")
        
        # Simplified PK modeling based on size and material
        diameter = np_row[3]
        material = np_row[8]
        
        # Size-dependent clearance
        if diameter < 50:
            t_half = 0.5  # hours, fast clearance
        elif diameter < 100:
            t_half = 2.0
        elif diameter < 200:
            t_half = 6.0
        else:
            t_half = 12.0
        
        # Material-dependent absorption
        material_abs = {
            "lipid": 0.95,
            "plga": 0.85,
            "pla": 0.80,
            "chitosan": 0.70,
            "gold": 0.50,
            "iron_oxide": 0.60,
            "silica": 0.40
        }
        
        absorption = material_abs.get(material, 0.75)
        
        # PK calculations
        cmax = dose_mg * absorption / (diameter / 100)  # μg/mL
        tmax = t_half * 0.3  # hours, simplified
        ke = 0.693 / t_half
        auc = cmax / ke
        
        return {
            "cmax_ug_ml": round(cmax, 2),
            "tmax_h": round(tmax, 2),
            "auc_ug_h_ml": round(auc, 2),
            "half_life_h": round(t_half, 2),
            "clearance_route": material
        }
    
    def toxicity_assessment(self, nanoparticle_id: str) -> Dict:
        """Assess nanoparticle toxicity risk."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM nanoparticles WHERE id = ?', (nanoparticle_id,))
        np_row = c.fetchone()
        conn.close()
        
        if not np_row:
            raise ValueError(f"Nanoparticle {nanoparticle_id} not found")
        
        diameter = np_row[3]
        charge = abs(np_row[4])
        material = np_row[8]
        
        # Safety scoring (0-100, higher is safer)
        score = 100
        
        # Size considerations (optimal 50-150nm)
        if diameter < 10 or diameter > 500:
            score -= 30
        elif diameter < 30 or diameter > 300:
            score -= 15
        
        # Charge considerations (±20 is safer, neutral is risky for targeting)
        if abs(charge) < 5:
            score -= 10
        elif abs(charge) > 50:
            score -= 15
        
        # Material toxicity
        material_toxicity = {
            "lipid": 90,
            "plga": 85,
            "pla": 85,
            "chitosan": 80,
            "gold": 75,
            "iron_oxide": 70,
            "silica": 65
        }
        
        score = min(score, material_toxicity.get(material, 60))
        
        return {
            "safety_score": score,
            "risk_level": "low" if score > 75 else "moderate" if score > 50 else "high",
            "diameter_optimal": 50 <= diameter <= 200,
            "charge_optimal": 10 <= abs(charge) <= 40,
            "material": material
        }
    
    def optimize_formulation(self, drug_payload: str, target_tissue: str) -> Dict:
        """Suggest optimal nanoparticle parameters for target."""
        suggestions = {}
        
        # Organ-specific recommendations
        if target_tissue == "lung":
            suggestions = {
                "diameter_nm": 50,
                "type": "polymeric",
                "material": "plga",
                "targeting_ligand": "folate",
                "charge_mv": -15,
                "route": "inhalation"
            }
        elif target_tissue == "tumor":
            suggestions = {
                "diameter_nm": 100,
                "type": "liposome",
                "material": "lipid",
                "targeting_ligand": "rgd_peptide",
                "charge_mv": -20,
                "route": "iv"
            }
        elif target_tissue == "brain":
            suggestions = {
                "diameter_nm": 80,
                "type": "polymeric",
                "material": "pla",
                "targeting_ligand": "transferrin",
                "charge_mv": 15,
                "route": "iv"
            }
        elif target_tissue == "liver":
            suggestions = {
                "diameter_nm": 150,
                "type": "dendrimer",
                "material": "chitosan",
                "targeting_ligand": "galactose",
                "charge_mv": 25,
                "route": "iv"
            }
        else:
            # Default systemic delivery
            suggestions = {
                "diameter_nm": 100,
                "type": "liposome",
                "material": "lipid",
                "targeting_ligand": "peg",
                "charge_mv": -10,
                "route": "iv"
            }
        
        suggestions["drug_payload"] = drug_payload
        suggestions["target_tissue"] = target_tissue
        
        return suggestions


def main():
    parser = argparse.ArgumentParser(description="Nanomedicine drug delivery simulator")
    subparsers = parser.add_subparsers(dest="command")
    
    # Design command
    design_parser = subparsers.add_parser("design", help="Design a new nanoparticle")
    design_parser.add_argument("name")
    design_parser.add_argument("type")
    design_parser.add_argument("diameter", type=float)
    design_parser.add_argument("drug")
    design_parser.add_argument("material")
    design_parser.add_argument("--ligand", default="")
    design_parser.add_argument("--encapsulation", type=float, default=85)
    
    # Simulate command
    sim_parser = subparsers.add_parser("simulate", help="Simulate delivery")
    sim_parser.add_argument("np_id")
    sim_parser.add_argument("tissue")
    sim_parser.add_argument("dose", type=float)
    
    # Optimize command
    opt_parser = subparsers.add_parser("optimize", help="Optimize formulation")
    opt_parser.add_argument("drug")
    opt_parser.add_argument("tissue")
    
    args = parser.parse_args()
    system = NanoMedicineSystem()
    
    if args.command == "design":
        np = system.design_nanoparticle(args.name, args.type, args.diameter, args.drug, 
                                       args.material, args.ligand, args.encapsulation)
        print(f"✓ Designed: {np.id} - {np.name}")
        print(json.dumps(asdict(np), indent=2, default=str))
    
    elif args.command == "simulate":
        biodist = system.simulate_delivery(args.np_id, args.tissue, args.dose)
        print(f"✓ Biodistribution for {args.np_id}:")
        print(json.dumps({k: f"{v:.2f} μg/mL" for k, v in biodist.items()}, indent=2))
    
    elif args.command == "optimize":
        suggestion = system.optimize_formulation(args.drug, args.tissue)
        print(f"✓ Optimized formulation for {args.drug} targeting {args.tissue}:")
        print(json.dumps(suggestion, indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
