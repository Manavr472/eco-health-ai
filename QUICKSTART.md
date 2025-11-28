# Eco-Health AI - Quick Start Commands

## ✅ Using Your Project Environment

All commands below use your project's conda environment located at:
`d:\Desktop\Mumbai_hacks\Agentic AI\.conda\`

---

## 🚀 Start Dashboard (EASIEST)

**Option 1: Double-click**
```
START_SERVER.bat
```
Then open: http://localhost:8000

**Option 2: Command line**
```powershell
cd "d:\Desktop\Mumbai_hacks\Agentic AI\eco-health-ai"
& "d:\Desktop\Mumbai_hacks\Agentic AI\.conda\python.exe" -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

---

## 📊 Run Demonstrations

### Demo 1: Full System Demo
```powershell
cd "d:\Desktop\Mumbai_hacks\Agentic AI\eco-health-ai"
& "d:\Desktop\Mumbai_hacks\Agentic AI\.conda\python.exe" demo/run_demo.py
```
Shows: Diwali surge, Monsoon scenario, Carbon credits

### Demo 2: Resource Agent
```powershell
& "d:\Desktop\Mumbai_hacks\Agentic AI\.conda\python.exe" demo/resource_agent_demo.py
```
Shows: Hospital optimization, Multi-hospital pooling

### Demo 3: Clinical Priority
```powershell
& "d:\Desktop\Mumbai_hacks\Agentic AI\.conda\python.exe" demo/clinical_priority_demo.py
```
Shows: Patient-first allocation (no cost constraints)

---

## 🔧 Training ML Models (Optional)

```powershell
cd "d:\Desktop\Mumbai_hacks\Agentic AI\eco-health-ai"
& "d:\Desktop\Mumbai_hacks\Agentic AI\.conda\python.exe" models/train_models.py
```

---

## 📝 System Status

✅ **Data Generated**: 5 years synthetic Mumbai data (2020-2024)
✅ **Packages Installed**: FastAPI, Uvicorn, Pandas, NumPy, Scikit-learn
✅ **API Ready**: Backend with agent integration
✅ **Dashboard Ready**: http://localhost:8000

---

## 🎯 What Works Now

1. **Dashboard** - Real-time KPIs, charts, AI recommendations  
2. **Agents** - ResourceRecommendationAgent for resource planning
3. **Data** - 168 surge events identified in generated data
4. **Demos** - All 3 demonstration scripts ready to run

---

## 🆘 Troubleshooting

**If port 8000 is busy:**
```powershell
& "d:\Desktop\Mumbai_hacks\Agentic AI\.conda\python.exe" -m uvicorn api.main:app --port 8001
```
Then open: http://localhost:8001

**Check what's installed:**
```powershell
& "d:\Desktop\Mumbai_hacks\Agentic AI\.conda\python.exe" -m pip list
```
