# 🧠 AI-Powered Resume–Job Matching System

An intelligent system that automatically compares a candidate’s resume with multiple job descriptions and determines whether the candidate is a **Fit** or **No Fit** for each role using **Deep Learning and Large Language Models (LLMs)**.

This project simulates a real-world **Applicant Tracking System (ATS)** used by modern recruitment platforms.

---

## 🚀 Project Overview

Recruiters often spend hours manually screening resumes against job descriptions. This project automates that process by combining:

- **Deep Learning-based text matching**
- **LLM-powered semantic understanding**
- **Resume summarization**
- **Job scraping and analytics**

The system takes a **resume (PDF or text)** and a **job role**, fetches relevant job descriptions, compares them intelligently, and produces a structured fit analysis.

---

## ✨ Key Features

### 📄 Resume Processing
- Supports **PDF and TXT resumes**
- Extracts raw text using `pdfplumber`
- Summarizes long resumes using an **LLM (Ollama)** for faster comparison

### 📋 Job Description Handling
- Fetches real job descriptions (e.g., Indeed scraping)
- Cleans and preprocesses text
- Supports batch comparison (one resume vs many jobs)

### 🧠 Deep Learning-Based Matching
- Uses a **dual-input neural network**
- One input for resume text
- One input for job description text
- Learns semantic similarity between resumes and job roles

### 🤖 LLM-Based Semantic Evaluation
- Uses **Ollama (LLaMA family)** for reasoning-based comparison
- Evaluates:
  - Skills
  - Tools & technologies
  - Role relevance
  - Experience alignment
- Outputs: `Fit` or `No Fit`

### 🗳️ Intelligent Decision System
- ML model provides structured pattern recognition
- LLM provides contextual reasoning
- Can be extended to **voting-based or hybrid decisions**

### 📊 Analytics & Insights
- Total jobs analyzed
- Fit vs No Fit distribution
- Fit percentage
- Stored results for future analysis

### ☁️ Cloud Storage
- Resume metadata
- Job queries
- Prediction results
- Stored securely using **Supabase**

---

## 🏗️ Tech Stack Used

### 🔹 Programming Language
- **Python**

### 🔹 Deep Learning
- **TensorFlow / Keras**
- Dual-input neural network architecture
- Tokenization + padding for sequence modeling

### 🔹 Natural Language Processing (NLP)
- Text cleaning and normalization
- Tokenizer-based embeddings
- Sequence padding for variable-length text

### 🔹 Large Language Models (LLM)
- **Ollama**
- Model: `llama3.2:1b`
- Used for:
  - Resume summarization
  - Resume–Job semantic comparison

### 🔹 Data Handling
- **Pandas**
- **NumPy**

### 🔹 PDF Processing
- **pdfplumber**

### 🔹 Database & Backend
- **Supabase (PostgreSQL)**
- Stores resumes, job queries, and prediction results

---

## 📈 Model Performance

The Deep Learning model was trained on labeled resume–job pairs with the following results:

| Metric | Accuracy |
|------|---------|
| **Training Accuracy** | **80%** |
| **Validation Accuracy** | **85%** |

✔ Indicates good generalization  
✔ Reduced overfitting  
✔ Reliable for real-world screening tasks

---

## 🧪 Workflow

1. Upload Resume (PDF / TXT)
2. Resume text is extracted and summarized
3. Job descriptions are fetched
4. Resume is attached to each job
5. Deep Learning model predicts Fit / No Fit
6. LLM validates semantic relevance
7. Results are stored and analyzed
8. Final insights are returned to the user

---

## 🧩 Output Example

```json
{
  "total_fetched": 25,
  "jobs_fit": 9,
  "jobs_nofit": 16,
  "fit_percentage": 36.0
}
