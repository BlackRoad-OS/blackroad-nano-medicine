# BlackRoad Nanomedicine

Advanced nanomedicine drug delivery and treatment simulation system for designing, analyzing, and optimizing nanoparticle-based therapeutics.

## Features

### 🧬 Nanoparticle Design
- **6 Types**: Liposome, Polymeric, Metallic, Dendrimer, Quantum Dot, Carbon Nanotube
- **7 Materials**: PLA, PLGA, Chitosan, Gold, Iron Oxide, Silica, Lipid
- **Tunable Parameters**:
  - Diameter (1-500 nm)
  - Surface charge (-50 to +50 mV)
  - Drug payload specification
  - Encapsulation efficiency (0-100%)
  - Targeting ligands

### 📊 Biodistribution Simulation
- Tissue-specific accumulation modeling
- Targeting ligand enhancement effects
- Multi-organ distribution tracking
- Time-dependent concentration profiles

### 💊 Pharmacokinetics
- Peak concentration (Cmax) calculation
- Time to peak (Tmax) estimation
- Area under curve (AUC) analysis
- Half-life prediction
- Size and material-dependent clearance
- Absorption rate modeling

### 🏥 Treatment Planning
- 5 Delivery Routes: IV, Oral, Inhalation, Topical, Intratumoral
- Treatment status tracking (Planned, Active, Completed, Discontinued)
- Efficacy monitoring
- Side effect documentation
- Patient-specific dosing (mg/kg)

### ⚠️ Safety Assessment
- Toxicity scoring (0-100, higher is safer)
- Diameter optimization analysis
- Surface charge evaluation
- Material safety considerations
- Risk level classification

### 🔬 Formulation Optimization
- Organ-specific parameter recommendations
- Target tissue optimization (lung, tumor, brain, liver)
- Automated suggestion engine
- PEGylation support

## Installation

```bash
git clone https://github.com/BlackRoad-OS/blackroad-nano-medicine.git
cd blackroad-nano-medicine
pip install -e .
```

## Usage

### Design a Nanoparticle
```bash
python src/nano_medicine.py design "DoxNP" liposome 100 doxorubicin lipid --ligand "rgd_peptide" --encapsulation 90
```

Output:
```json
{
  "id": "NP_ABC12345",
  "name": "DoxNP",
  "type": "liposome",
  "diameter_nm": 100,
  "surface_charge_mv": -10,
  "drug_payload": "doxorubicin",
  "encapsulation_pct": 90,
  "targeting_ligand": "rgd_peptide",
  "material": "lipid"
}
```

### Simulate Delivery
```bash
python src/nano_medicine.py simulate NP_ABC12345 tumor 5.0
```

### Optimize Formulation
```bash
python src/nano_medicine.py optimize paclitaxel lung
```

## Database

SQLite database stored at `~/.blackroad/nanomed.db`

### Schema
- **nanoparticles**: Nanoparticle formulations
- **treatments**: Patient treatment plans
- **biodistribution**: Tissue concentration profiles

## Examples

### Design and Test a Doxorubicin Liposome
```python
from src.nano_medicine import NanoMedicineSystem

system = NanoMedicineSystem()

# Design nanoparticle
np = system.design_nanoparticle(
    name="DoxNP",
    type_str="liposome",
    diameter_nm=100,
    drug_payload="doxorubicin",
    material="lipid",
    targeting_ligand="rgd_peptide",
    encapsulation_pct=92
)

# Check pharmacokinetics
pk = system.pharmacokinetics(np.id, dose_mg=10)
print(f"Cmax: {pk['cmax_ug_ml']} μg/mL")
print(f"Half-life: {pk['half_life_h']} hours")

# Assess safety
safety = system.toxicity_assessment(np.id)
print(f"Safety Score: {safety['safety_score']}/100")

# Create treatment plan
treatment = system.create_treatment(
    patient_id="PATIENT_001",
    nanoparticle_id=np.id,
    dose_mg_kg=5.0,
    route="iv",
    duration_days=28
)

# Update with efficacy
system.update_efficacy(treatment.id, efficacy_pct=78, side_effects=["mild_nausea"])
```

## CLI Commands

```bash
# Design new nanoparticle
python src/nano_medicine.py design <name> <type> <diameter> <drug> <material> [--ligand LIGAND] [--encapsulation PCT]

# Simulate biodistribution
python src/nano_medicine.py simulate <np_id> <tissue> <dose_mg>

# Optimize formulation for target
python src/nano_medicine.py optimize <drug> <tissue>
```

## Science Background

This system models simplified versions of real nanomedicine processes:
- Nanoparticle size influences lymphatic vs. blood clearance
- Surface charge affects protein corona formation
- Targeting ligands enable receptor-mediated uptake
- Material composition determines biodegradability

## Limitations

This is a simplified educational simulation. Real-world nanomedicine involves:
- Complex protein corona effects
- Non-linear pharmacokinetics
- Individual patient variability
- Manufacturing variability
- Immune system interactions

## License

MIT
