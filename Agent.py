import pickle
import string
import numpy as np
import pandas as pd
import ollama
import pdfplumber
import re

from tensorflow.keras.preprocessing.sequence import pad_sequences
from supabase import create_client


# ---------------- SUMMARIZER ---------------- #
def summarizer(description):
    INSTRUCTION = (
        "You are a helpful AI Assistant. "
        "Summarize the input text. "
        "Return only summarized content. "
        "Length < 500 words. No symbols. No new lines."
    )

    response = ollama.chat(
        model="llama3.2:1b",
        messages=[
            {"role": "system", "content": INSTRUCTION},
            {"role": "user", "content": description}
        ]
    )
    return response["message"]["content"]


# ---------------- MODEL LOADER ---------------- #
def initialize():
    with open("model_type1.pkl", "rb") as f:
        model = pickle.load(f)

    with open("tokenier.pkl", "rb") as f:
        tokenizer = pickle.load(f)

    supabase = create_client(
        "YOUR CLIENT URL",
        "YOUR SECRET KEY"
    )

    return model, tokenizer, supabase


# ---------------- TEXT CLEANING ---------------- #
def clean_text(text):
    text = str(text).lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    words = [w for w in text.split() if w.isalpha() and len(w) > 1]
    return " ".join(words)


# ---------------- ML PREDICT (UNCHANGED) ---------------- #
def predict(batch_data, model, tokenizer):
    label_map = {0: "Fit", 1: "No Fit"}
    results = []

    for _, row in batch_data.iterrows():
        resume = clean_text(row["resume"])
        jd = clean_text(row["description"])

        resume_seq = pad_sequences(
            tokenizer.texts_to_sequences([resume]),
            maxlen=3028
        )
        jd_seq = pad_sequences(
            tokenizer.texts_to_sequences([jd]),
            maxlen=1055
        )

        prediction = model.predict([resume_seq, jd_seq], verbose=0)
        pred_id = np.argmax(prediction)
        results.append(label_map[pred_id])

    batch_data["prediction"] = results
    return batch_data


# ---------------- ANALYTICS ---------------- #
def analytics(data):
    return {
        "data": data,
        "total fetched": len(data),
        "jobs fit": (data["prediction"] == "Fit").sum(),
        "fit mean": (data["prediction"] == "Fit").mean() * 100,
        "jobs nofit": (data["prediction"] == "No Fit").sum(),
        "nofit mean": (data["prediction"] == "No Fit").mean() * 100,
    }


# ---------------- PDF READER ---------------- #
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + " "
    return text.strip()


# ---------------- SUPABASE STORE ---------------- #
def backend_store(supabase, resume_text, filepath, position, location, data):
    supabase.table("resume").insert({
        "resume_text": resume_text,
        "file_url": filepath
    }).execute()

    supabase.table("job_queries").insert({
        "job_role": position,
        "location": location
    }).execute()

    supabase.table("job_results").insert(
        data[["company_name", "company_url", "prediction"]].to_dict("records")
    ).execute()


# ---------------- AGENT ---------------- #
def agent_main(resume_file, position, location, is_txt=False):
    resume_text = (
        resume_file.read().decode("utf-8", errors="ignore")
        if is_txt else extract_text_from_pdf(resume_file)
    )

    model, tokenizer, supabase = initialize()

    resume_summary = summarizer(resume_text)

    fetched_data = pd.read_csv("/home/arun-raja/Documents/VSC/indeed_jobs.csv")
    fetched_data["resume"] = resume_summary
    fetched_data.rename(columns={"url": "company_url"}, inplace=True)

    output = predict(fetched_data, model, tokenizer)

    backend_store(
        supabase,
        resume_text,
        "/home/arun-raja/Documents/VSC/resume.pdf",
        position,
        location,
        output
    )

    return analytics(output)


# ---------------- MAIN (CLI TEST) ---------------- #
if __name__ == "__main__":
    with open("resume.pdf", "rb") as f:
        result = agent_main(f, "AI Engineer", "India")
        print(result)
