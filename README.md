
# Traffic Prediction Project

A machine learning–based Python project to predict traffic conditions using historical data. This repository includes model training artifacts, source code, data files, and scripts to run predictions and analyze results.

## 📌 Project Structure

traffic_prediction_project
├── app/                      # Application code (frontend / API)
├── data/                     # Dataset files
├── src/                      # Source scripts and utilities
├── best_cls_model.pkl        # Trained classification model
├── best_ml_model.pkl         # Trained regression model
├── feature_columns.pkl       # Feature configuration
├── label_encoder.pkl         # Encoded label mappings
├── classification_results.csv# Classification predictions
├── model_results.csv         # Regression or evaluation results
├── main.py                  # Entry point for execution
├── requirements.txt         # Python dependencies
└── .env                     # Environment variables

## 🧠 Project Overview

Traffic prediction plays a critical role in intelligent transportation systems. This project applies machine learning models to predict traffic behavior using historical datasets.

## 🚀 Features

- Machine learning–based traffic prediction  
- Pre-trained classification and regression models  
- CSV-based result outputs  
- Modular and extensible project structure  

## 📦 Installation

1. Clone the repository:
   git clone https://github.com/172-21019/traffic_prediction_project.git

2. Navigate to the project directory:
   cd traffic_prediction_project

3. (Optional) Create a virtual environment:
   python -m venv venv

4. Activate the virtual environment:
   - Windows: venv\Scripts\activate
   - Linux/macOS: source venv/bin/activate

5. Install required dependencies:
   pip install -r requirements.txt

## ▶️ Usage

Run the main script:
python main.py

The script loads trained models and generates prediction results as CSV files.

## 📊 Output Files

- classification_results.csv – Classification predictions  
- model_results.csv – Model evaluation or regression output  

## 🧪 Model Training

You can retrain models by modifying the scripts in the src/ directory and saving updated models using pickle.

## 🔧 Configuration

Use the .env file to manage environment-specific variables such as paths or API keys.

## 🤝 Contributing

Contributions are welcome:
1. Fork the repository  
2. Create a feature branch  
3. Commit changes  
4. Open a pull request  

## 📄 License

This project is open-source and available for educational and research purposes.
