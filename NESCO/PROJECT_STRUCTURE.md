# NESCO Resourcing Agent - Final Project Structure

## 📁 Clean Project Structure

```
NESCO/
├── resourcing_agent.py                    # Main agent script
├── config.py                              # Configuration (API key, model, defaults)
├── hospital_mapping.py                    # Hospital ID/name mapping
├── Hsupply.json                           # Hospital inventory data
├── CALCULATION_LOGIC.md                   # Medical calculation documentation
├── README.md                              # Project documentation
└── data/
    └── mumbai_hospitals_surge_categories.csv  # Surge predictions (5 categories)
```

## 🎯 Core Files

### 1. **resourcing_agent.py**
Main agent that:
- Loads inventory from Hsupply.json
- Loads surge data from CSV
- Calculates supply needs for 10 supply types
- Generates JSON reports

### 2. **config.py**
Configuration settings:
- `GEMINI_API_KEY` - Your Google Gemini API key
- `GEMINI_MODEL_NAME` - Model to use (gemini-flash-latest)
- `DEFAULT_SURGE_DATA` - Default surge data path
- `DEFAULT_INVENTORY` - Default inventory path
- `DEFAULT_OUTPUT` - Default output file name

### 3. **hospital_mapping.py**
Maps hospital IDs to full names:
- `HOSPITAL_NAME_MAPPING` - ID to name mapping
- `HOSPITAL_TYPES` - Municipal vs Private classification

### 4. **Hsupply.json**
Current inventory for 14 Mumbai hospitals with 10 supply types:
- Oxygen Cylinders
- Ventilators
- Oxygen Masks
- Humidifiers
- Trauma Stretchers
- IV Stand Kits
- Defibrillators
- Gloves/Aprons/PPE
- Cooling Pads/Ice Packs
- Thermometers

### 5. **data/mumbai_hospitals_surge_categories.csv**
Predicted admissions by category:
- Airborne (TB, Influenza, COVID-19, Pneumonia)
- Waterborne (Cholera, Typhoid, Leptospirosis, Gastroenteritis)
- Heat-related (Heat stroke, Heat exhaustion)
- Trauma (Accidents, Falls, Burns, Fractures)
- Other (Cardiac, Stroke, Diabetes, Chronic diseases)

### 6. **CALCULATION_LOGIC.md**
Medical justification for all calculations based on WHO/ICMR/CDC guidelines

### 7. **README.md**
Project documentation and usage instructions

## 🚀 Usage

### Run for All Hospitals
```bash
python resourcing_agent.py
```

### Run for Single Hospital
```bash
python resourcing_agent.py --hospital_id KEM_H1
```

### Custom Files
```bash
python resourcing_agent.py --surge_data path/to/surge.csv --inventory path/to/inventory.json --output report.json
```

## 📊 Output Format

```json
{
  "reports": [
    {
      "hospital_id": "KEM_H1",
      "hospital_name": "King Edward Memorial Hospital, Parel",
      "hospital_type": "Municipal",
      "safety_buffer_applied": "30%",
      "supplies_status": [
        {
          "item_name": "Oxygen Cylinders",
          "current_stock": 650,
          "projected_need": 440,
          "calculation_note": "Formula details",
          "status": "OK",
          "action_required": "None",
          "quantity_to_order": 0
        }
      ]
    }
  ]
}
```

## 🔧 Customization

### Update API Key
Edit `config.py`:
```python
GEMINI_API_KEY = "your-new-api-key"
```

### Change Model
Edit `config.py`:
```python
GEMINI_MODEL_NAME = "gemini-pro-latest"
```

### Update Inventory
Replace `Hsupply.json` with new data (maintain same format)

### Update Surge Predictions
Replace `data/mumbai_hospitals_surge_categories.csv` with new predictions

## 📋 Hospital Coverage

**14 Mumbai Hospitals:**
- 6 Municipal: KEM, Lokmanya Tilak, BYL Nair, JJ, Cooper, HBT
- 8 Private: Hinduja, Lilavati, Nanavati, Bombay, Jaslok, Breach Candy, Saifee, Jupiter

## ✅ Features

- ✅ Category-based admission predictions (5 categories)
- ✅ 10 supply types from actual inventory
- ✅ WHO/ICMR/CDC medical guidelines
- ✅ Hospital-type-specific safety buffers (30% Municipal, 20% Private)
- ✅ CRITICAL/LOW/OK status flagging
- ✅ Exact order quantity calculations
- ✅ Transparent calculation formulas in output

## 🎓 Medical Accuracy

All calculations based on:
- WHO clinical treatment guidelines
- ICMR India-specific protocols
- CDC international standards
- Mumbai historical admission data (2019-2024)
- Category-based disease classification

See `CALCULATION_LOGIC.md` for complete medical justification.
