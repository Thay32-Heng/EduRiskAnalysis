"""EduRisk Analytics - Lab 02.

A native Streamlit build of the Figma Make design (``Clone Frontend Design.zip``).
Every screen is plain Streamlit layout - ``st.columns``, ``st.container``,
``st.metric``, ``st.slider``, ``st.dataframe`` - with the design system applied
from :mod:`theme` and the reusable chunks in :mod:`components`.

Data is intentionally left as a placeholder: replace ``df`` below with your own
Pandas dataframe (or model output) and the dashboard renders from it.
"""

import pandas as pd
import streamlit as st

import components as ui
from theme import inject_theme

st.set_page_config(
    page_title="EduRisk Analytics - Lab 02",
    page_icon="🎓",
    layout="wide",
)

# --------------------------------------------------------------- placeholders
# TODO: replace with your own dataframe / model output.
df = pd.DataFrame(
    {
        "Student Name": ["Dara", "Sophea", "Vuthy", "Malis", "Rithy", "Sreyneang", "Chan", "Bopha"],
        "Course": ["Python", "Statistics", "Python", "Database", "Web App", "Database", "Python", "Statistics"],
        "Score": [85, 68, 45, 92, 58, 91, 72, 62],
        "Attendance": [90, 75, 50, 95, 60, 94, 80, 88],
        "Study Hours": [12, 8, 3, 15, 5, 14, 9, 7],
    }
)

# Options for the course filter.
COURSES = ["Python", "Statistics", "Database", "Web App"]

HIGH_RISK = "High Risk"

COURSE_KEY = "er-filter-course"
RISK_KEY = "er-filter-risk"
ATTENDANCE_KEY = "er-filter-attendance"
SCORE_KEY = "er-filter-score"

CSV_NAME = "filtered_student_data.csv"

inject_theme()


# ------------------------------------------------------------------- helpers
def classify_risk(score, attendance):
    """Placeholder risk rule - swap in your own logic or model call."""
    if score < 60 or attendance < 60:
        return HIGH_RISK
    if score < 75 or attendance < 75:
        return "Medium Risk"
    return "Low Risk"


def mean_of(frame, column):
    """Average of ``column``, or ``0`` when the column is missing."""
    if frame.empty or column not in frame.columns:
        return 0.0
    return float(frame[column].mean())


def count_risk(frame, level):
    """Number of rows at ``level``, or ``0`` when the column is missing."""
    if frame.empty or "Risk Level" not in frame.columns:
        return 0
    return int((frame["Risk Level"] == level).sum())


# TODO: replace with your model's output if it produces the risk level.
df["Risk Level"] = [
    classify_risk(score, attendance)
    for score, attendance in zip(df["Score"], df["Attendance"])
]


def apply_filters(frame, course, risk, min_attendance, min_score):
    """Row subset for the current filter selection."""
    view = frame
    if view.empty:
        return view
    if course != "All" and "Course" in view.columns:
        view = view[view["Course"] == course]
    if risk != "All" and "Risk Level" in view.columns:
        view = view[view["Risk Level"] == risk]
    if "Attendance" in view.columns:
        view = view[view["Attendance"] >= min_attendance]
    if "Score" in view.columns:
        view = view[view["Score"] >= min_score]
    return view


def active_filter_count(course, risk, min_attendance, min_score):
    """How many filters are currently narrowing the cohort."""
    return sum(
        [
            course != "All",
            risk != "All",
            min_attendance > 0,
            min_score > 0,
        ]
    )


# --------------------------------------------------------------- navigation
def navigate(page):
    st.session_state.page = page


def reset_filters():
    """Callback for the filter card's ``Reset filters`` button."""
    st.session_state[COURSE_KEY] = "All"
    st.session_state[RISK_KEY] = "All"
    st.session_state[ATTENDANCE_KEY] = 0
    st.session_state[SCORE_KEY] = 0
    st.session_state[f"{ATTENDANCE_KEY}_display"] = 0
    st.session_state[f"{SCORE_KEY}_display"] = 0


def current_filters():
    """Filter values from the previous run, falling back to the defaults."""
    return (
        st.session_state.get(COURSE_KEY, "All"),
        st.session_state.get(RISK_KEY, "All"),
        st.session_state.get(ATTENDANCE_KEY, 0),
        st.session_state.get(SCORE_KEY, 0),
    )


def render_sidebar(active_page):
    with st.sidebar:
        st.html(ui.BRAND_HTML)
        st.html(ui.FIELD_LABEL_HTML)

        with st.container(key="er-nav"):
            for page in ui.PAGES:
                st.button(
                    page,
                    key=f"er-nav-{ui.PAGE_SLUGS[page]}",
                    type="primary" if page == active_page else "tertiary",
                    on_click=navigate,
                    args=(page,),
                    width="stretch",
                )

        with st.container(key="er-sidebar-status"):
            st.html(ui.STATUS_HTML.format(count=len(df)))


# ----------------------------------------------------------------- sections
def render_filter_card():
    """The design's filter card with its four fields."""
    course, risk, min_attendance, min_score = current_filters()
    active = active_filter_count(course, risk, min_attendance, min_score)

    with ui.card("er-filter-card"):
        ui.filter_card_header(reset_filters, disabled=active == 0)

        course_col, risk_col, attendance_col, score_col = st.columns(4)

        with course_col:
            ui.field_header("Course")
            ui.select_filter("Course", COURSE_KEY, ["All", *COURSES])

        with risk_col:
            ui.field_header("Risk level")
            ui.select_filter("Risk level", RISK_KEY, ["All", *ui.RISK_LEVELS])

        with attendance_col:
            min_attendance = ui.labeled_slider("Minimum attendance", ATTENDANCE_KEY)

        with score_col:
            min_score = ui.labeled_slider("Minimum score", SCORE_KEY)

        filtered = apply_filters(
            df, course, risk, min_attendance, min_score
        )
        ui.filter_footer(len(filtered), len(df), active)

    return filtered


def render_metrics(view):
    """The design's four metric cards."""
    ui.section_heading("At a glance", "Key metrics", "Based on current filters")

    average_score = mean_of(view, "Score")
    average_attendance = mean_of(view, "Attendance")
    high_risk = count_risk(view, HIGH_RISK)
    high_risk_share = round(high_risk / len(view) * 100) if len(view) else 0

    students_col, score_col, attendance_col, risk_col = st.columns(4)

    with students_col:
        ui.metric_card(
            "er-metric-students",
            "Students",
            len(view),
            f"{len(df)} enrolled in total",
        )

    with score_col:
        ui.metric_card(
            "er-metric-score",
            "Average score",
            f"{average_score:.2f}",
            "Out of 100 points",
        )

    with attendance_col:
        ui.metric_card(
            "er-metric-attendance",
            "Attendance",
            f"{average_attendance:.1f}%",
            "Average attendance rate",
        )

    with risk_col:
        ui.metric_card(
            "er-metric-risk",
            "High risk",
            high_risk,
            f"{high_risk_share}% of filtered students",
        )


def render_charts(view):
    """The design's score and risk distribution panels."""
    ui.section_heading("Insights", "Performance patterns", "Updated with your filters")

    score_col, risk_col = st.columns([1.28, 0.92], vertical_alignment="top")

    with score_col:
        ui.chart_panel(
            "er-chart-scores",
            "Student scores",
            "Individual performance out of 100",
            "Score",
            score_legend= False,
            chart=ui.score_chart(view),
        )

    with risk_col:
        ui.chart_panel(
            "er-chart-risk",
            "Risk distribution",
            "Students grouped by current risk level",
            "Cohort",
            score_legend=False,
            chart=ui.risk_chart(view),
        )
        ui.risk_legend()


def render_table_card(frame, key, download_label="Download CSV", height=None):
    """Table card: heading row, CSV download and the table itself."""
    with ui.card("er-dataset"):
        heading, actions = st.columns([3, 2], vertical_alignment="center")

        with heading:
            st.html(ui.DATASET_HEADING_HTML.format(count=len(frame)))

        with actions:
            st.download_button(
                download_label,
                data=frame.to_csv(index=False),
                file_name=CSV_NAME,
                mime="text/csv",
                key="er-download",
            )

        ui.student_table(frame, key=key, height=height)


# -------------------------------------------------------------------- pages
def page_dashboard():
    ui.topbar(
        "Dashboard",
        csv_data=apply_filters(df, *current_filters()).to_csv(index=False),
        file_name=CSV_NAME,
    )
    ui.page_intro(
        "Performance overview",
        "Student risk dashboard",
        "Monitor performance, attendance, and risk signals across your "
        "active courses.",
    )

    view = render_filter_card()
    render_metrics(view)
    render_charts(view)


def page_home():
    ui.topbar("Home")
    ui.page_intro(
        "Welcome",
        "EduRisk Analytics",
        "Interactive student risk monitoring dashboard built with Streamlit.",
        badge="Lab 02",
    )

    st.success("Lab 02 app is running successfully!")


def page_student_data():
    ui.topbar("Student Data")
    ui.page_intro(
        "Student data",
        "Full cohort overview",
        "Every record in the dataset with its calculated risk level.",
        badge=f"{len(df)} records",
    )

    render_table_card(
        df, "er-student-data-table", download_label="Download all records", height=560
    )


def page_risk_checker():
    ui.topbar("Risk Checker")
    ui.page_intro(
        "Risk checker",
        "Single student risk checker",
        "Enter one student's results to see the risk level and the reasoning "
        "behind it.",
        badge="Instant result",
    )

    with st.form("er-risk-form", border=False):
        name_col, score_col, attendance_col = st.columns(3)

        with name_col:
            name = st.text_input("Student Name", key="er-check-name")

        with score_col:
            score = st.number_input(
                "Score", min_value=0, max_value=100, value=50, key="er-check-score"
            )

        with attendance_col:
            attendance = st.number_input(
                "Attendance",
                min_value=0,
                max_value=100,
                value=50,
                key="er-check-attendance",
            )

        _, _, submit_col = st.columns([2, 1, 1])
        with submit_col:
            submitted = st.form_submit_button(
                "Check risk", key="er-submit", width="stretch"
            )

    if submitted:
        st.session_state.risk_result = (name, int(score), int(attendance))

    result = st.session_state.get("risk_result")
    if result:
        student_name, student_score, student_attendance = result
        ui.risk_banner(
            classify_risk(student_score, student_attendance),
            student_name,
            student_score,
            student_attendance,
        )

    ui.section_heading("Ethics", "Use the result responsibly")
    st.info(
        "Risk prediction should support students, not punish them. "
        "Discuss every flag with the student before acting on it."
    )


def page_about():
    ui.topbar("About")
    ui.page_intro(
        "About",
        "About this project",
        "Lab 02 of the Web App Development for Data Science course.",
        badge="Lab 02",
    )

    with ui.card("er-card"):
        st.html(
            """
            <span class="eyebrow">Project theme</span>
            <p class="er-text">EduRisk Analytics</p>
            <span class="eyebrow" style="margin-top:14px">Topic</span>
            <p class="er-text">Streamlit interactive dashboard</p>
            <span class="eyebrow" style="margin-top:14px">Description</span>
            <p class="er-text">
              An interactive student risk monitoring dashboard. The layout and
              design system come from a Figma Make prototype that was rebuilt
              with native Streamlit widgets.
            </p>
            """
        )

    ui.section_heading("Tools used", "Stack")
    st.html(
        '<span class="er-chip">Python</span>'
        '<span class="er-chip">Streamlit</span>'
        '<span class="er-chip">Pandas</span>'
        '<span class="er-chip">Altair</span>'
        '<span class="er-chip">VS Code</span>'
    )

    ui.section_heading("Student information", "Author")
    st.html(
        '<span class="er-chip">Heng Sengthay</span>'
        '<span class="er-chip">Student ID 73191</span>'
        '<span class="er-chip">Class M2</span>'
    )


# --------------------------------------------------------------------- main
if "page" not in st.session_state:
    st.session_state.page = "Home"

active_page = st.session_state.page
render_sidebar(active_page)

pages = {
    "Home": page_home,
    "Dashboard": page_dashboard,
    "Student Data": page_student_data,
    "Risk Checker": page_risk_checker,
    "About": page_about,
}

pages[active_page]()