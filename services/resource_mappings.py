"""
Hospital mappings for resource recommendation system
Maps hospital IDs, names, and types (Municipal vs Private)
"""

HOSPITAL_NAME_MAPPING = {
    "KEM_H1": "King Edward Memorial Hospital",
    "LOK_H2": "Lokmanya Tilak Hospital",
    "NAI_H3": "BYL Nair Hospital",
    "JJ_H4": "JJ Hospital",
    "HIN_H5": "Hinduja Hospital",
    "LIL_H6": "Lilavati Hospital",
    "NAN_H7": "NANAVATI Hospital",
    "BOM_H8": "Bombay Hospital",
    "JAS_H9": "Jaslok Hospital",
    "BRE_H10": "Breach Candy Hospital",
    "SAI_H11": "Saifee Hospital",
    "JUP_H13": "Jupiter Hospital",
    "COO_H14": "Dr. R N Cooper Hospital",
    "HBT_H15": "HBT Trauma Care"
}

# Hospital types for safety buffer calculation
HOSPITAL_TYPES = {
    "KEM_H1": "Municipal",
    "LOK_H2": "Municipal",
    "NAI_H3": "Municipal",
    "JJ_H4": "Municipal",
    "HIN_H5": "Private",
    "LIL_H6": "Private",
    "NAN_H7": "Private",
    "BOM_H8": "Private",
    "JAS_H9": "Private",
    "BRE_H10": "Private",
    "SAI_H11": "Private",
    "JUP_H13": "Private",
    "COO_H14": "Municipal",
    "HBT_H15": "Municipal"
}

# Per-patient supply requirements by admission category
# Category mapping: respiratory -> Airborne, waterborne -> Waterborne, 
# heat_related -> Heat-related, trauma -> Trauma, other -> Other
SUPPLY_REQUIREMENTS = {
    "Oxygen Cylinders": {
        "respiratory": 0.3,
        "waterborne": 0.05,
        "heat_related": 0.2,
        "trauma": 0.3,
        "other": 0.25
    },
    "Ventilators": {
        "respiratory": 0.1,
        "waterborne": 0.02,
        "heat_related": 0.05,
        "trauma": 0.15,
        "other": 0.08
    },
    "Oxygen Masks": {
        "respiratory": 2.0,
        "waterborne": 0.5,
        "heat_related": 1.5,
        "trauma": 2.0,
        "other": 1.5
    },
    "Humidifiers": {
        "respiratory": 0.3,
        "waterborne": 0.05,
        "heat_related": 0.1,
        "trauma": 0.2,
        "other": 0.15
    },
    "Trauma Stretchers": {
        "respiratory": 0.1,
        "waterborne": 0.05,
        "heat_related": 0.2,
        "trauma": 1.0,
        "other": 0.15
    },
    "IV Stand Kits": {
        "respiratory": 0.6,
        "waterborne": 0.8,
        "heat_related": 0.9,
        "trauma": 0.95,
        "other": 0.7
    },
    "Defibrillators": {
        "respiratory": 0.02,
        "waterborne": 0.01,
        "heat_related": 0.05,
        "trauma": 0.08,
        "other": 0.15
    },
    "Gloves/PPE": {
        "respiratory": 25,
        "waterborne": 20,
        "heat_related": 12,
        "trauma": 30,
        "other": 15
    },
    "Cooling Pads": {
        "respiratory": 2,
        "waterborne": 1,
        "heat_related": 15,
        "trauma": 3,
        "other": 2
    },
    "Thermometers": {
        "respiratory": 0.5,
        "waterborne": 0.3,
        "heat_related": 0.6,
        "trauma": 0.4,
        "other": 0.4
    }
}

# Safety buffer percentages
SAFETY_BUFFERS = {
    "Municipal": 0.30,  # 30% buffer
    "Private": 0.20     # 20% buffer
}
