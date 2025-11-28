# Eco-Health AI Platform

**Agentic AI for Resilient & Sustainable Hospital Operations - Mumbai Region**

An intelligent platform that predicts patient surges using real-time external data (AQI, weather, events) and autonomously generates actionable recommendations for hospitals. The system quantifies carbon emission reductions from optimized operations and tokenizes them as blockchain-based carbon credits.

## 🎯 Problem Statement

Hospitals face operational chaos during predictable crises (pollution spikes, monsoons, festivals), leading to:
- Inefficient resource allocation
- Excessive energy and supply waste  
- High carbon emissions
- Poor patient outcomes

## 💡 Solution

Eco-Health AI provides:
1. **Predictive Analytics**: 5-day advance surge predictions using external data
2. **Autonomous Recommendations**: Staff deployment, supply ordering, public advisories
3. **Carbon Credit Generation**: Quantify and tokenize emission reductions on blockchain
4. **Financial Sustainability**: New revenue stream from carbon credits

## 🏗️ Architecture

```
External Data → Predictive Models → AI Agent → Recommendations
                                         ↓
                            Carbon Calculator → Blockchain Tokenization
```

## 📦 Tech Stack

- **Backend**: Python 3.8+
- **ML Framework**: scikit-learn (RandomForest, GradientBoosting)
- **API**: FastAPI
- **Database**: SQLite
- **Blockchain**: Python-based simulation
- **Frontend**: HTML/CSS/JavaScript

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate Synthetic Data (5 years for Mumbai)

```bash
cd data_generators
python generate_all.py
```

This generates:
- AQI data for 10 Mumbai stations
- Weather patterns (monsoon, summer, winter)
- Festival calendar (Diwali, Ganesh Chaturthi, etc.)
- Patient admission data with realistic surges

### 3. Train ML Models

```bash
cd models
python train_models.py
```

Trains:
- Surge prediction model (ensemble: RF + GB)
- Resource forecasting model

### 4. Run the API Server

```bash
uvicorn api.main:app --reload
```

Access dashboard at: `http://localhost:8000`

### 5. Run Demonstrations

```bash
cd demo
python run_demo.py
```

## 📊 Key Features

### Predictive Models
- **Surge Predictor**: >75% accuracy, 7-day forecast horizon
- **Resource Forecaster**: Staff, supplies, beds requirements
- Features: Lag variables, rolling statistics, interaction terms

### Agentic AI
- **Autonomous Monitoring**: Continuous 5-minute cycle
- **Risk Assessment**: Identifies high-risk surge events
- **Action Planning**: Generates comprehensive recommendations
- **Confidence Scoring**: Only acts above 70% confidence

### Recommendations

**Resource Recommendation Agent** 🆕

**Dual Operation Modes:**
- **CLINICAL_PRIORITY** (Default): Patient safety first - meets 100% of requirements regardless of cost
- **BUDGET_AWARE**: Cost-conscious allocation when budget constraints apply

**Features:**
- Priority scoring based on patient impact (0-100)
- Lead time consideration for procurement
- Multi-hospital resource pooling (up to 40% cost savings)
- Automated action timelines
- Readiness scoring (0-100)

1. **Staff Deployment**
   - Doctors, nurses, support staff allocation
   - On-call activation protocols
   - Inter-facility coordination

2. **Supply Pre-ordering**
   - PPE kits, oxygen, IV fluids, medications
   - Buffer stock calculations
   - Emergency procurement

3. **Public Advisories**
   - AQI alerts, safety measures
   - Hospital capacity management
   - Distribution via social media, SMS, radio

4. **Facility Management**
   - Bed expansion protocols
   - Ward conversions
   - Discharge optimization

### Carbon Credits

- **Baseline Calculation**: Chaotic emissions (40-60% waste)
- **Optimized Calculation**: AI-driven efficiency
- **Reduction Tracking**: 25-40% emission reduction per surge
- **Blockchain Tokenization**: Verifiable, immutable credits
- **Revenue Generation**: ~$25 USD per ton CO2

## 📁 Project Structure

```
eco-health-ai/
├── config.py                  # Central configuration
├── requirements.txt           # Dependencies
│
├── data_generators/          # Synthetic data generation
│   ├── aqi_generator.py
│   ├── weather_generator.py
│   ├── event_generator.py
│   ├── patient_surge_generator.py
│   └── generate_all.py
│
├── models/                   # ML models
│   ├── surge_predictor.py
│   ├── resource_forecaster.py
│   └── train_models.py
│
├── agent/                    # Agentic AI system
│   ├── eco_health_agent.py
│   └── recommendation_engine.py
│
├── sustainability/           # Carbon credits
│   ├── carbon_calculator.py
│   └── blockchain_tokenizer.py
│
├── api/                      # FastAPI backend
│   ├── main.py
│   └── routes/
│
├── dashboard/                # Web interface
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── demo/                     # Demonstrations
│   ├── scenarios.py
│   └── run_demo.py
│
└── tests/                    # Unit tests
```

## 🧪 Demo Scenarios

1. **Diwali Pollution Surge** (Nov 2024)
   - AQI spike to 450+ (Severe)
   - 2.0x patient surge (respiratory)
   - 2.5 tons CO2 reduction

2. **Monsoon Healthcare Crisis** (June-Sept)
   - Heavy rainfall (>50mm/day)
   - 1.6x surge (waterborne, accidents)
   - 1.8 tons CO2 reduction

3. **Summer Heatwave** (April-May)
   - Temperature >38°C
   - 1.5x surge (heat-related)
   - 1.2 tons CO2 reduction

4. **Festival Crowd Management** (Ganesh Chaturthi)
   - Large gatherings
   - 1.6x surge (trauma, injuries)
   - 1.5 tons CO2 reduction

## 📈 Performance Metrics

- **Prediction Accuracy**: 75-85%
- **Carbon Reduction**: 25-45% per surge event
- **Resource Optimization**: 20-40% waste reduction
- **Advance Warning**: 5-7 days
- **Response Time**: <5 minutes (agent monitoring cycle)

## 🔬 Validation

```bash
# Run all tests
pytest tests/ -v

# Test data generators
python data_generators/aqi_generator.py
python data_generators/weather_generator.py

# Test models
python models/surge_predictor.py
python models/resource_forecaster.py

# Test agent
python agent/eco_health_agent.py

# Test sustainability
python sustainability/carbon_calculator.py
python sustainability/blockchain_tokenizer.py
```

## 🌍 Environmental Impact

**Per Major Surge Event (2.0x, 300 patients):**
- Baseline emissions: ~5,000 kg CO2
- Optimized emissions: ~2,500 kg CO2
- **Reduction: 2.5 tons CO2**
- **Revenue: ~$62.50 USD**

**Annual Impact (5 hospitals, ~20 major surges):**
- **Total reduction: ~50 tons CO2/year**
- **Revenue potential: ~$1,250 USD/year**

## 🎓 Mumbai-Specific Adaptations

- **10 AQI monitoring stations**: Bandra, Andheri, Colaba, Worli, etc.
- **Monsoon season**: June-September rainfall patterns
- **Major festivals**: Diwali, Ganesh Chaturthi, Holi, Navratri
- **Temperature ranges**: 18-38°C seasonal variations
- **5 major hospitals**: Simulated network

## 🔮 Future Enhancements

1. **Real-time Data Integration**
   - Live AQI feeds from SAFAR/CPCB
   - IMD weather data API
   - Hospital EMR integration

2. **Advanced ML Models**
   - LSTM/Transformer for time-series
   - Multi-task learning
   - Uncertainty quantification

3. **Blockchain Deployment**
   - Ethereum/Polygon integration
   - Smart contracts for automatic issuance
   - Carbon credit marketplace

4. **Mobile Application**
   - Hospital admin dashboard
   - Public health alerts
   - Real-time notifications

## 📝 License

MIT License - Free for research and commercial use

## 👥 Contributors

Built for Mumbai Hackathon 2025

## 📧 Contact

For questions or collaboration: [Your contact info]

---

**Eco-Health AI** - Turning Operational Efficiency into Environmental Sustainability
