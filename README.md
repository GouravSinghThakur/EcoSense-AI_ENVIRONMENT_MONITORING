---
title: EcoSense AI Environment Monitoring
emoji: 🌍
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: "1.32.0"
python_version: 3.10
app_file: app.py
pinned: false
---

<p align="center">
  <img src="https://img.icons8.com/color/96/earth-planet.png" width="90"/>
</p>

<h1 align="center">🌍 EcoSense AI</h1>

<p align="center">
  <b>Your smart companion for real-time weather and air quality monitoring!</b>
</p>

---

## 👋 Welcome to EcoSense AI!

Ever wondered if it's safe to go for a run outside? Or if a storm is coming? **EcoSense AI** takes the guesswork out of your local environment. 

It is an easy-to-use, fully automated dashboard that gathers live weather and air quality data, uses Artificial Intelligence to predict what will happen next, and warns you if conditions become dangerous.

---

## ✨ What Can It Do?

* **📡 Live Environment Tracking:** Get real-time updates on temperature, humidity, wind speed, and the Air Quality Index (AQI) for your exact location.
* **🤖 AI Predictions:** Our smart AI looks at the past 90 days of weather to predict the temperature and air quality for the next 48 hours.
* **🚨 Smart Alerts:** If pollution spikes or a storm approaches, a bright warning banner appears instantly to keep you safe.
* **📊 Beautiful Charts:** Easily understand your local climate with simple, interactive charts showing daily patterns and 5-day forecasts.
* **🌙 Dark Mode Design:** A sleek, modern "glass" design that is easy on the eyes.

---

## 🚀 How to Run It Yourself

You don't need to be an expert to get EcoSense AI running on your own computer. Just follow these simple steps:

### Step 1: Download the Project
Download this folder or run this command in your terminal:
```bash
git clone https://github.com/GouravSinghThakur/AI-ENVIRONMENT-MONITORING.git
cd AI-ENVIRONMENT-MONITORING
```

### Step 2: Install the Requirements
Make sure you have Python installed, then install the required tools:
```bash
pip install -r requirements.txt
```

### Step 3: Get Your Free API Key
EcoSense AI gets its live data from OpenWeatherMap. 
1. Go to [OpenWeatherMap](https://openweathermap.org/) and create a free account.
2. Copy your free API Key.
3. Open the `config/` folder, duplicate the `.env.template` file, and rename it to `.env`.
4. Open your new `.env` file and paste your API key:
   `OPENWEATHERMAP_API_KEY=your_key_here`

> **Note:** If you skip this step, the app will just run in "Demo Mode" with fake data so you can still see how it looks!

### Step 4: Start the Dashboard
Run this final command:
```bash
streamlit run app.py
```
A browser window will automatically open with your live dashboard!

---

## 🌐 Live Web Version

Don't want to install anything? You can view the fully running version of EcoSense AI right on the web via Hugging Face Spaces!

🔗 **[Click here to view the live dashboard](https://huggingface.co/spaces/GouravSinghThakur/AI_ENVIRONMENT_MONITORING)**

---

## 👨‍💻 About the Project
Created by **Gourav Singh Thakur** as an advanced exploration into combining real-time data APIs with machine learning models to create useful, everyday tools. 
