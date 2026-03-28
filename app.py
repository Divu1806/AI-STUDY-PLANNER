import streamlit as st
import pandas as pd
import os
from datetime import datetime

from ai_engine import (
    calculate_completion_percent,
    calculate_difficulty,
    calculate_priority,
    get_remaining_topics
)

from scheduler import allocate_time_and_topics


# ---------------------------------------------------
# 🌄 SAFE BACKGROUND (No input styling issues)
# ---------------------------------------------------
def set_background():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(
                rgba(0, 50, 0, 0.6),
                rgba(0, 0, 0, 0.7)
            ),
            url("https://images.unsplash.com/photo-1501785888041-af3ef285b470");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }

        h1 {
            color: white;
            text-align: center;
            font-size: 42px;
        }

        h2, h3, label {
            color: white !important;
        }

        /* Button Styling Only (Safe) */
        .stButton>button {
            background-color: #2ecc71;
            color: white;
            border-radius: 10px;
            font-size: 18px;
            padding: 10px 25px;
            transition: 0.3s ease;
        }

        .stButton>button:hover {
            background-color: #27ae60;
            transform: scale(1.05);
        }

        /* Transparent Dataframe Background */
        .stDataFrame {
            background-color: rgba(255,255,255,0.95);
        }

        </style>
        """,
        unsafe_allow_html=True
    )

set_background()


# ---------------------------------------------------
# 🌍 TITLE + THEME QUOTE
# ---------------------------------------------------
st.title("🌿 AI Adaptive Study Journey Planner")

st.markdown(
    "<h3 style='color:white; text-align:center;'>"
    "🏔 Learning is a journey. Every topic completed grows your knowledge tree."
    "</h3>",
    unsafe_allow_html=True
)

st.write("")

# ---------------------------------------------------
# 📚 SUBJECT INPUT
# ---------------------------------------------------
num_subjects = st.number_input("Enter number of subjects:", min_value=1, step=1)

subjects = []

for i in range(num_subjects):
    st.subheader(f"📘 Subject {i+1}")

    name = st.text_input(f"Subject Name {i+1}", key=f"name{i}")

    total_marks_input = st.text_input(
        f"Full Marks for {name}",
        key=f"total{i}"
    )

    obtained_marks_input = st.text_input(
        f"Marks Obtained in Last Exam for {name}",
        key=f"obt{i}"
    )

    # Safe conversion
    try:
        total_marks = float(total_marks_input)
    except:
        total_marks = 0

    try:
        obtained_marks = float(obtained_marks_input)
    except:
        obtained_marks = 0

    if total_marks > 0 and obtained_marks > total_marks:
        st.warning("⚠ Obtained marks cannot be greater than full marks.")

    exam_date = st.date_input(
        f"Exam Date for {name}",
        key=f"date{i}"
    )

    syllabus_input = st.text_area(
        f"Enter Entire Syllabus Topics for {name} (comma separated)",
        key=f"syllabus{i}"
    )

    completed_input = st.text_area(
        f"Enter Topics Completed So Far for {name} (comma separated)",
        key=f"completed{i}"
    )

    # ---- Performance Calculation ----
    if total_marks > 0:
        performance_percent = (obtained_marks / total_marks) * 100
    else:
        performance_percent = 0

    total_topics = [t.strip() for t in syllabus_input.split(",") if t.strip()]
    completed_topics = [t.strip() for t in completed_input.split(",") if t.strip()]

    completion_percent = calculate_completion_percent(total_topics, completed_topics)
    remaining_topics = get_remaining_topics(total_topics, completed_topics)

    days_remaining = (exam_date - datetime.today().date()).days

    difficulty_score = calculate_difficulty(
        performance_percent,
        completion_percent
    )

    priority = calculate_priority(
        difficulty_score,
        days_remaining
    )

    subjects.append({
        "name": name,
        "performance_percent": performance_percent,
        "completion_percent": completion_percent,
        "difficulty_score": difficulty_score,
        "days_remaining": days_remaining,
        "priority": priority,
        "remaining_topics": remaining_topics
    })


# ---------------------------------------------------
# ⏳ STUDY HOURS INPUT
# ---------------------------------------------------
available_hours_input = st.text_input(
    "Enter Available Study Hours Per Day:"
)

try:
    available_hours = float(available_hours_input)
except:
    available_hours = 0


# ---------------------------------------------------
# 🚀 GENERATE PLAN
# ---------------------------------------------------
if st.button("🌄 Generate Today's Study Plan"):

    if available_hours <= 0:
        st.error("Please enter valid study hours.")
    else:
        results = allocate_time_and_topics(subjects, available_hours)

        st.subheader("📅 Topics To Complete Today")

        df = pd.DataFrame(results)
        st.dataframe(df)

        # Save history
        today_str = datetime.today().strftime("%Y-%m-%d")

        for row in results:
            row["Date"] = today_str

        history_df = pd.DataFrame(results)

        os.makedirs("data", exist_ok=True)
        file_path = "data/study_history.csv"

        if os.path.exists(file_path):
            history_df.to_csv(file_path, mode='a', header=False, index=False)
        else:
            history_df.to_csv(file_path, index=False)

        st.success("🌿 Today's Study Plan Saved Successfully!")