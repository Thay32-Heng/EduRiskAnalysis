import streamlit as st
import pandas as pd
import csv

st.set_page_config(
    page_title="EduRisk Analytics - Lab 02",
    page_icon="🎓",
    layout="wide"
)

student_df = pd.DataFrame({
    "Student Name": ["Dara", "Sophea", "Vuthy", "Malis", "Rithy", "Sreyneang", "Chan", "Bopha"],
    "Course": ["Python", "Statistics", "Python", "Database", "Web App", "Database", "Python", "Statistics"],
    "Score": [85, 68, 45, 92, 58, 91, 72, 62],
    "Attendance": [90, 75, 50, 95, 60, 94, 80, 88],
    "Study Hours": [12, 8, 3, 15, 5, 14, 9, 7]
})

# Create a function that classifies each student into a risk levl
def get_risk_level(score, attendance):
    if score < 60 or attendance < 60:
        return "High Risk"
    elif score < 75 or attendance < 75:
        return "Medium Risk"
    else:
        return "Low Risk"

student_df["Risk Level"] = student_df.apply(
    lambda row: get_risk_level(row["Score"], row["Attendance"]),
    axis=1
)

total_students = len(student_df)
average_score = student_df["Score"].mean()
average_attendance = student_df["Attendance"].mean()
low_score_students = student_df[student_df["Score"] < 60].shape[0]

with st.sidebar:
    st.title("EduRisk Menu")
    selected_page = st.radio(
        "Select Page",
        ["Home", "Dashboard", "Student Data", "Risk Checker","About"]
    )

if selected_page == "Home":
    st.title("🎓 EduRisk Analytics")
    st.subheader("Interactive Student Risk Monitoring Dashboard")
    st.write("Welcome to Lab 02.")
    st.write("In this lab, you will use Streamlit widgets to explore student performance data.")
    st.success("Lab 02 app is running successfully!")
    if st.button("Click Me!"):
        st.write("Welcome❤️")

# add information to the dashboard
elif selected_page == "Dashboard":
    st.title("Interactive Dashboard")

    st.write("Use the filters below to explore student performance.")
    #add course to dashboard
    selected_course = st.selectbox(
        "Select Course",
        ["ALL"] + list(student_df["Course"].unique())
    )
    #add risk to dashboard
    selected_risk=st.selectbox(
       "selected_risk",
       ["ALL","Low Risk","Medium Risk","Hight Risk"],
    )
    # add a slider to fitler student by minimun attendacne 
    min_attendance=st.slider(
        "Minimun Attendance",
        0, 100, 0
    )
    # add a slider to fitler student by minimun score 
    min_score=st.slider(
        "Minimun Score",
        0, 100, 0
    )

    # Create a filtered version of the student dataset based on the dasboard widgets.
    filtered_df = student_df.copy()

    if selected_course != ["ALL"]:
        filtered_df= filtered_df[filtered_df["Course"] == selected_course]
         
    if selected_risk != ["ALL"]:
        filtered_df= filtered_df[filtered_df["Risk Level"] == selected_risk]

    filtered_df = filtered_df[
        filtered_df["Attendance"] >= min_attendance
    ]

    filtered_df = filtered_df[
        filtered_df["Score"] >= min_score
    ]

    # add dashboard metrics that update based on the filtered data.
    total_students = len(filtered_df)

    if len(filtered_df) > 0:
        average_score = filtered_df["Score".mean()]
        average_attendance = filtered_df["Attendance".mean()]
    else:
        average_score = 0
        average_attendance = 0
    high_risk_student = filtered_df[
        filtered_df["Risk Level"] == "High Risk"
    ].shape[0]
    st.subheader("Dashboard Metrics")

    col1,col2,col3,col4 = st.columns(4)

    with col1:
        st.metric("Students", total_students)

    with col2:
        st.metric("Average Score", round(average_score,2))

    with col3:
        st.metric("Average Attendance", f"{round(average_attendance,2)}%")

    with col4:
        st.metric("High Risk", high_risk_student)

    # add a checkbox that allows the user to show or hide the filtered dataset.
    show_data = st.checkbox("Show Filtered Dataset", True)

    if show_data:
        st.subheader("Filtered Student Dataset")
        st.dataframe(filtered_df)

        #add a button to download the filtered dataset as a CSV file.
        csv = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Filtered Data",
            data=csv,
            file_name="filtered_student_data.csv",
            mime="text/csv"
        )

    else:
        st.info("Filtered dataset is hidden.")




elif selected_page == "Student Data":
    st.title("Student Data")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total Students", total_students)
        st.metric("Average Score", round(average_score, 2))

    with col2:
        st.metric("Average Attendance", f"{round(average_attendance, 2)}%")
        st.metric("Low Score Students", low_score_students)

    st.dataframe(student_df)

else:
    st.title("About")
    st.write("This app is part of Lab 01.")
    st.write("Course: Web App Development for Data Science")
    st.write("Project Theme: EduRisk Analytics")