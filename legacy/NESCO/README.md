# NESCO Resourcing Agent

Medical supply prediction system for Mumbai hospitals using Google Gemini AI with historical data (2019-2024).

## Quick Start

### Basic Usage (Uses config.py defaults)
```bash
python resourcing_agent.py
```

### Custom Parameters
```bash
python resourcing_agent.py --surge_data data/custom_surge.csv --inventory data/custom_inventory.json --output custom_report.json
```

### Single Hospital Analysis
```bash
python resourcing_agent.py --hospital_id KEM_H1
```

## Configuration

All API keys and default settings are in **`config.py`** - edit this file to change:

- **GEMINI_API_KEY**: Your Google Gemini API key
- **GEMINI_MODEL_NAME**: Model to use (default: `gemini-flash-latest`)
- **DEFAULT_SURGE_DATA**: Default surge data file path
- **DEFAULT_INVENTORY**: Default inventory file path
- **DEFAULT_OUTPUT**: Default output report file path

### Available Models
- `gemini-flash-latest` (default - fast and efficient)
- `gemini-2.0-flash-lite` (lighter version)
- `gemini-2.5-flash-preview-09-2025` (preview version)
- `gemini-pro-latest` (more capable, slower)
- `gemini-2.0-pro-exp` (experimental pro version)

## File Structure

```
NESCO/
├── config.py                          # Configuration file (API key, model, defaults)
├── resourcing_agent.py                # Main agent script
├── list_models.py                     # List available Gemini models
├── mumbai_enhanced_report.json        # Latest generated report
└── data/
    ├── mumbai_hospitals_surge.csv     # Surge predictions for all hospitals
    ├── mumbai_hospitals_inventory.json # Inventory for all hospitals
    ├── mumbai_surge_data.csv          # Legacy surge data
    ├── mumbai_inventory.json          # Legacy inventory
    ├── surge_data.csv                 # Original surge data
    └── inventory.json                 # Original inventory
```

## Features

### Historical Data Integration (2019-2024)
- Disease trend analysis (Malaria, Dengue, Leptospirosis, Gastroenteritis)
- Resource consumption patterns per patient type
- Supply chain lessons from pandemic period
- Hospital-type-specific safety buffers (30% Municipal, 20% Private)

### Accurate Predictions
- Disease-specific supply calculations
- Critical status flagging (<50% stock = CRITICAL)
- Order quantities to reach 120% of projected need
- Per-patient consumption rates based on historical data

## Command-Line Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--surge_data` | `data/mumbai_hospitals_surge.csv` | Path to surge prediction CSV |
| `--inventory` | `data/mumbai_hospitals_inventory.json` | Path to inventory JSON |
| `--output` | `mumbai_enhanced_report.json` | Output report path |
| `--api_key` | From `config.py` | Google Gemini API key |
| `--model_name` | From `config.py` | Gemini model name |
| `--hospital_id` | None (all hospitals) | Specific hospital ID to analyze |

## Utilities

### List Available Models
```bash
python list_models.py
```

### Override API Key
```bash
python list_models.py --api_key YOUR_API_KEY
```

## Output Format

The generated JSON report includes for each hospital:
- Hospital ID and name
- Supply status for each item:
  - Current stock
  - Projected need
  - Status (OK/LOW/CRITICAL)
  - Action required
  - Quantity to order

## Mumbai Hospitals Covered

**Municipal Hospitals** (30% safety buffer):
- KEM_H1: King Edward Memorial Hospital (2,250 beds)
- LOK_H2: Lokmanya Tilak Hospital (1,422 beds)
- NAI_H3: BYL Nair Hospital (1,229 beds)
- JJ_H4: JJ Hospital (1,352 beds)
- COO_H14: Dr. R N Cooper Hospital (700 beds)
- HBT_H15: HBT Trauma Care (180 beds)

**Private Hospitals** (20% safety buffer):
- HIN_H5: Hinduja Hospital (337 beds)
- LIL_H6: Lilavati Hospital (320 beds)
- NAN_H7: Nanavati Hospital (350 beds)
- BOM_H8: Bombay Hospital (732 beds)
- JAS_H9: Jaslok Hospital (448 beds)
- BRE_H10: Breach Candy Hospital (213 beds)
- SAI_H11: Saifee Hospital (254 beds)
- JUP_H13: Jupiter Hospital (350 beds)
