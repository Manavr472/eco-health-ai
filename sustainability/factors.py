from models.carbon_models import EmissionFactor

# Source: CO2 Baseline Database for the Indian Power Sector (CEA), Version 18 (2022)
# Average Grid Emission Factor for India
GRID_INDIA_CEA = EmissionFactor(
    source="CEA (India) CO2 Baseline Database V18",
    region="India",
    value=0.82, # kgCO2/kWh (approx weighted average)
    unit="kgCO2/kWh",
    valid_from="2022"
)

# Source: IPCC Guidelines for National Greenhouse Gas Inventories (2006)
# Diesel (Stationary Combustion)
DIESEL_IPCC = EmissionFactor(
    source="IPCC Guidelines 2006",
    region="Global",
    value=2.68, # kgCO2/Liter. Note: We need to convert kWh to Liters if using generator efficiency.
    # For simplicity in this agent, we might assume a direct kWh -> kgCO2 factor for diesel generators 
    # or convert kWh -> Liters -> kgCO2.
    # A typical diesel gen produces ~3.5 kWh per Liter. 
    # So 1 kWh = 1/3.5 Liters = ~0.28 Liters.
    # 0.28 Liters * 2.68 kgCO2/L = ~0.75 kgCO2/kWh.
    # Let's use a direct factor for simplicity but document it.
    unit="kgCO2/Liter", 
    valid_from="2006"
)

# Derived Diesel Factor per kWh (assuming 3.5 kWh/L efficiency)
DIESEL_GEN_FACTOR = EmissionFactor(
    source="IPCC 2006 (Derived)",
    region="Global",
    value=0.76, # 2.68 / 3.5
    unit="kgCO2/kWh",
    valid_from="2006"
)

SOLAR_FACTOR = EmissionFactor(
    source="Internal",
    region="Global",
    value=0.0,
    unit="kgCO2/kWh",
    valid_from="2023"
)

FACTOR_DB = {
    "Scope 2": GRID_INDIA_CEA,
    "Scope 1": DIESEL_GEN_FACTOR,
    "Solar": SOLAR_FACTOR
}
