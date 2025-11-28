# Sensor-Labs
# SensorLab — PyQt6 Desktop Application  
A modern macOS-inspired interface for multi-channel material sensor experiments.  
Built using **PyQt6**, **pyqtgraph**, and designed as a complete workflow tool for **gas-sensing research**, **ML datasets**, and **model deployment**.

---

## 🚀 Overview
SensorLab is a fully featured desktop application for researchers working on **material sensors**, **gas classification**, and **data-driven modeling pipelines**.  
It provides:

- Clean, consistent macOS-style UI  
- Live multi-channel sensor visualization  
- Metadata logging  
- Analysis utilities  
- ML-ready data export  
- Light/Dark theme  
- Custom heater profiles  
- Extensible architecture for advanced gas-sensing research  

Developed as part of an active PhD-level research workflow.

---

# 🔥 **NEW: Built-in ML Modeling Integration (Research-Grade)**

SensorLab is not just a UI — it is intentionally designed as a **data pipeline hub** for:

### ✔ Machine Learning  
### ✔ Explainable AI  
### ✔ Gas Classification & Concentration Prediction  
### ✔ Experimental Dataset Generation  
### ✔ Inference Support (Real-Time & Offline)

This makes the system **research-ready** and directly relevant for:

- **Gas sensing materials research**  
- **Multi-channel sensor characterization**  
- **Industrial gas monitoring**  
- **AI-based drift compensation**  
- **Deep learning modeling of sensor response curves**  
- **XAI (SHAP, LIME, Force plots)**  
- **Research papers + experimental reproducibility**

---

## 🧠 **Modeling Workflow (How SensorLab Integrates with ML)**

SensorLab is designed so researchers can:

### **1. Acquire Clean, Timestamped, Multi-Channel Data**  
- Each channel is plotted live  
- Metadata is automatically saved  
- Periodic sampling ensures consistent ML-friendly structure  

---

### **2. Pre-process Data in Real-Time or After Export**  
SensorLab can be extended to compute:
- Baseline shifts  
- ∆R/R₀  
- Feature extraction  
- Temperature / humidity compensation  
- Heater-cycle feature vectors  

These are required inputs for:
- SVM, XGBoost, Random Forest  
- CNN/LSTM deep models  
- Hybrid/ensemble architectures  
- Your custom **SXGA architecture**  
- Time-series forecasting models  

---

### **3. Export ML-Ready Datasets**
The app exports structured data including:
- Channel values  
- Heater profiles  
- Timestamp formats (epoch or ISO-8601)  
- Experimental metadata  
- Notes and environmental annotations  

This ensures **traceability**, **replicability**, and **clean integration** into:
- Python + NumPy + Pandas workflows  
- Scikit-learn pipelines  
- PyTorch or TensorFlow models  
- XAI tooling (SHAP/LIME)  

---

### **4. (Future) Integrated Model Inference**
The architecture allows adding on-device ML prediction:
- Load saved `.pkl` model  
- Real-time prediction from sensor stream  
- Drift correction models  
- Concentration estimation  
- Confidence scores  
- SHAP local explanations per sample  

SensorLab is therefore model-ready and aligns directly with modern **AI-driven gas sensing systems**.

---

# ⭐ Why Modeling Integration Matters  
This modeling pipeline is crucial because **modern gas sensors produce complex temporal patterns**.  
Deep lear
