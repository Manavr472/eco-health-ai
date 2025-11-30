"""
Hospital name to ID mapping for NESCO Resourcing Agent
Maps hospital IDs from surge data to full hospital names in Hsupply.json
"""

HOSPITAL_NAME_MAPPING = {
    "KEM_H1": "King Edward Memorial Hospital, Parel",
    "LOK_H2": "Lokmanya Tilak Hospital, Sion",
    "NAI_H3": "BBL Nair Hospital, Mumbai Central",
    "JJ_H4": "JJ Hospital, Mumbai Central",
    "HIN_H5": "Hinduja Hospital, Mahim",
    "LIL_H6": "Lilavati Hospital, Bandra West",
    "NAN_H7": "NANAVATI, Vile Parle",
    "BOM_H8": "Bombay Hospital, Marine Lines",
    "JAS_H9": "Juslok Hospital & Research Centre, Tardeo",
    "BRE_H10": "Breach Candy Hospital Trust, Breach Candy",
    "SAI_H11": "Saifee Hospital, Charni Road",
    "JUP_H13": "Jupitar Hospital, Thane West",
    "COO_H14": "Dr. R N Cooper Hospital, Juhu",
    "HBT_H15": "HBT (THACKERAY) Trauma Care, Joghshwari East"
}

# Reverse mapping for lookup
HOSPITAL_ID_MAPPING = {v: k for k, v in HOSPITAL_NAME_MAPPING.items()}

# Hospital types (Municipal vs Private)
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
