# 🏠 House Price Prediction API

This project is a machine learning API built using FastAPI that predicts house prices based on input features.

## 🚀 Features
- Predict house price using REST API
- Batch prediction using CSV upload
- Input validation using Pydantic
- Returns predictions as CSV file

## 🛠 Tech Stack
- Python
- FastAPI
- Scikit-learn
- Pandas

## 📌 API Endpoints
- `GET /` → Home
- `GET /health` → Health check
- `POST /predict` → Single prediction
- `POST /predict-file` → Batch prediction (CSV upload)

## 📥 Input Features
- MedInc
- HouseAge
- AveRooms
- AveBedrms
- Population
- AveOccup
- Latitude
- Longitude

## ▶️ How to Run

```bash
pip install -r requirements.txt
uvicorn main:app --reload