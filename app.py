"""EduRisk Analytics - Lab 02.

A native Streamlit build of the Figma Make design (``Clone Frontend Design.zip``).
Every screen is plain Streamlit layout - ``st.columns``, ``st.container``,
``st.metric``, ``st.slider``, ``st.dataframe`` - with the design system applied
from :mod:`theme` and the reusable chunks in the component helpers below.

Data is intentionally left as a placeholder: replace ``df`` below with your own
Pandas dataframe (or model output) and the dashboard renders from it.
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

import altair as alt

sys.path.insert(0, str(Path(__file__).parent / 'design'))
from theme import AMBER, GREEN, MUTED, PRIMARY, RED, TEXT, inject_theme

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

# ==========================================================================
# components (merged from components.py)
# ==========================================================================



PAGES = ["Home", "Dashboard", "Student Data", "Risk Checker", "About"]

RISK_LEVELS = ["Low Risk", "Medium Risk", "High Risk"]

PAGE_SLUGS = {
    "Home": "home",
    "Dashboard": "dashboard",
    "Student Data": "student-data",
    "Risk Checker": "risk-checker",
    "About": "about",
}

BRAND_HTML = """
<div class="brand">
  <span class="brand-mark">E</span>
  <span>
    <strong>EduRisk</strong>
    <small>Student Intelligence</small>
  </span>
</div>
"""

FIELD_LABEL_HTML = '<p class="field-label">Workspace</p>'

TOPBAR_CONTEXT_HTML = """
<div class="topbar-context"><span>Overview</span><strong>{page}</strong></div>
"""

INTRO_HTML = """
<div class="intro">
  <div>
    <span class="eyebrow">{eyebrow}</span>
    <h2>{title}</h2>
    <p>{description}</p>
  </div>
  <div class="intro-summary"><span class="live-dot"></span>{badge}</div>
</div>
"""

SECTION_HEADING_HTML = """
<div class="section-heading{modifier}">
  <div>
    <span class="eyebrow">{eyebrow}</span>
    <h3>{title}</h3>
  </div>
  <span class="section-note">{note}</span>
</div>
"""

FILTER_FOOTER_HTML = """
<div class="filter-footer">
  <span>Showing <strong>{shown}</strong> of {total} students</span>
  {chip}
</div>
"""

CHART_HEADING_HTML = """
<div class="chart-heading">
  <div>
    <h4>{title}</h4>
    <p>{description}</p>
  </div>
  <span class="legend{modifier}">{legend}</span>
</div>
"""

DATASET_HEADING_HTML = """
<div class="section-heading dataset-heading">
  <div>
    <span class="eyebrow">Student data</span>
    <h3>Students at a glance</h3>
    <p>{count} records match the current view</p>
  </div>
</div>
"""

STATUS_HTML = """
<div class="sidebar-status">
  <span class="status-dot"></span>
  <span>
    <strong>Data synced</strong>
    <small>{count} student records</small>
  </span>
</div>
"""

EMPTY_STATE_HTML = """
<div style="display:flex;height:84px;align-items:center;justify-content:center;
            color:#9298aa;font-size:13px">
  No records match the current view.
</div>
"""

RISK_BADGE_COLORS = {
    "Low Risk": {"bg": "rgba(72, 201, 149, 0.16)", "fg": "#70dcaf"},
    "Medium Risk": {"bg": "rgba(234, 182, 82, 0.16)", "fg": "#f0c66d"},
    "High Risk": {"bg": "rgba(242, 99, 112, 0.16)", "fg": "#f9848e"},
}

RISK_CHART_ORDER = ["High Risk", "Low Risk", "Medium Risk"]
RISK_CHART_COLORS = [RED, GREEN, AMBER]

SCORE_BAR_COLOR = "#7d8dff"
SCORE_BAR_WIDTH = {"band": 0.38}
RISK_BAR_WIDTH = {"band": 0.45}

GRID_COLOR = "rgba(153, 161, 184, 0.16)"
AXIS_LABEL_COLOR = "#767e81"
CATEGORY_LABEL_COLOR = "#858c9e"

CHART_HEIGHT = 250


def has_columns(frame, *columns):
    """True when ``frame`` can actually be plotted (placeholder-safe)."""
    return not frame.empty and all(column in frame.columns for column in columns)


def y_axis(ticks):
    """Value axis with the design's dashed grid lines and muted labels."""
    return alt.Axis(
        title=None,
        values=ticks,
        domain=False,
        tickColor="transparent",
        labelColor=AXIS_LABEL_COLOR,
        labelFontSize=10,
        labelPadding=6,
        grid=True,
        gridColor=GRID_COLOR,
        gridDash=[3, 3],
        gridWidth=1,
    )


def x_axis():
    """Category axis with the design's angled labels."""
    return alt.Axis(
        title=None,
        domain=False,
        tickColor="transparent",
        labelAngle=-45,
        labelColor=CATEGORY_LABEL_COLOR,
        labelFontSize=10,
        labelLimit=90,
        labelPadding=6,
    )


def risk_badge(risk_level):
    """Return the HTML pill used in the prototype's table rows."""
    slug = risk_level.lower().replace(" ", "-")
    return f'<span class="risk-badge {slug}">{risk_level}</span>'


def card(key):
    """Return a styled card container (``st.container`` + a design key)."""
    return st.container(key=key)


def select_filter(label, key, options):
    """``st.selectbox`` whose default lives in ``session_state``.

    Setting the default before the widget is created keeps Streamlit from
    warning about a widget that has both a default and a session state value.
    """
    st.session_state.setdefault(key, options[0])
    return st.selectbox(label, options, key=key, label_visibility="collapsed")


def topbar(page_label, csv_data=None, file_name="filtered_student_data.csv"):
    """Sticky topbar with the breadcrumb, the export action and the menu."""
    with st.container(key="er-topbar"):
        breadcrumb, export, menu = st.columns([6, 1, 1], vertical_alignment="center")

        with breadcrumb:
            st.html(TOPBAR_CONTEXT_HTML.format(page=page_label))

        with export:
            if csv_data is not None:
                st.download_button(
                    "Export report",
                    data=csv_data,
                    file_name=file_name,
                    mime="text/csv",
                    key="er-export",
                )
            else:
                st.empty()


def page_intro(eyebrow, title, description, badge="Live dataset"):
    """Hero block at the top of every page."""
    st.html(
        INTRO_HTML.format(
            eyebrow=eyebrow, title=title, description=description, badge=badge
        )
    )


def section_heading(eyebrow, title, note="", compact=False):
    """Eyebrow + title (+ optional right aligned note) row."""
    st.html(
        SECTION_HEADING_HTML.format(
            eyebrow=eyebrow,
            title=title,
            note=note,
            modifier=" compact" if compact else "",
        )
    )


def field_header(label, value=None):
    """Label row that replaces the native widget labels."""
    value_html = f'<span class="field-value">{value}</span>' if value is not None else ""
    st.html(f'<div class="field-header"><span>{label}</span>{value_html}</div>')


def labeled_slider(label, key, min_value=0, max_value=100, value=0, step=1):
    """``st.slider`` with the design's label row and right aligned value.

    The value is mirrored into ``session_state`` by the widget callback because
    the header is rendered before the slider exists.
    """
    mirror = f"{key}_display"
    st.session_state.setdefault(key, value)
    st.session_state.setdefault(mirror, value)

    def sync():
        st.session_state[mirror] = st.session_state[key]

    field_header(label, st.session_state[mirror])
    return st.slider(
        label,
        min_value=min_value,
        max_value=max_value,
        step=step,
        key=key,
        label_visibility="collapsed",
        on_change=sync,
    )


def filter_card_header(reset_callback, disabled):
    """Filter card title plus the ``Reset filters`` action."""
    title, action = st.columns([6, 1], vertical_alignment="center")
    with title:
        section_heading("Filters", "Refine the cohort", compact=True)
    with action:
        st.button(
            "Reset filters",
            key="er-reset",
            type="tertiary",
            disabled=disabled,
            on_click=reset_callback,
            width="stretch",
        )


def filter_footer(shown, total, active):
    """``Showing N of M students`` line plus the active filter chip."""
    if active:
        plural = "filter" if active == 1 else "filters"
        chip = f'<span class="filter-chip">{active} active {plural}</span>'
    else:
        chip = ""
    st.html(FILTER_FOOTER_HTML.format(shown=shown, total=total, chip=chip))


def metric_card(key, label, value, caption):
    """Design metric card built on the native ``st.metric`` element."""
    with st.container(key=key):
        st.metric(label, value)
        st.html(f'<span class="er-metric-caption">{caption}</span>')


def score_chart(students):
    """``ScoreChart`` from the prototype: per-student bars out of 100."""
    if not has_columns(students, "Student Name", "Score"):
        return None

    ordered = students.sort_values("Student Name")

    bars = (
        alt.Chart(ordered)
        .mark_bar(color=SCORE_BAR_COLOR, cornerRadiusEnd=5, width=SCORE_BAR_WIDTH)
        .encode(
            x=alt.X("Student Name:N", axis=x_axis(), sort=list(ordered["Student Name"])),
            y=alt.Y(
                "Score:Q",
                scale=alt.Scale(domain=[0, 100]),
                axis=y_axis([0, 20, 40, 60, 80, 100]),
            ),
            tooltip=[
                alt.Tooltip("Student Name:N", title="Student"),
                alt.Tooltip("Course:N"),
                alt.Tooltip("Score:Q", format=".0f"),
                alt.Tooltip("Risk Level:N"),
            ],
        )
        .properties(height=CHART_HEIGHT)
    )

    return bars.configure_view(strokeWidth=0)


def risk_chart(students):
    """``RiskChart`` from the prototype: counts per risk level."""
    if not has_columns(students, "Risk Level"):
        return None

    counts = students["Risk Level"].value_counts()
    rows = [
        {"Risk Level": level, "Students": int(counts.get(level, 0))}
        for level in RISK_CHART_ORDER
    ]
    top = max(3, max(row["Students"] for row in rows))

    bars = (
        alt.Chart(alt.Data(values=rows))
        .mark_bar(cornerRadiusEnd=5, width=RISK_BAR_WIDTH)
        .encode(
            x=alt.X("Risk Level:N", axis=x_axis(), sort=RISK_CHART_ORDER),
            y=alt.Y(
                "Students:Q",
                scale=alt.Scale(domain=[0, top]),
                axis=y_axis(list(range(0, top + 1))),
            ),
            color=alt.Color(
                "Risk Level:N",
                scale=alt.Scale(domain=RISK_CHART_ORDER, range=RISK_CHART_COLORS),
                legend=None,
            ),
            tooltip=[alt.Tooltip("Risk Level:N"), alt.Tooltip("Students:Q")],
        )
        .properties(height=CHART_HEIGHT)
    )

    return bars.configure_view(strokeWidth=0)


def chart_panel(key, title, description, legend, score_legend, chart):
    """Chart panel card: heading, legend chip and the chart itself."""
    with st.container(key=key):
        st.html(
            CHART_HEADING_HTML.format(
                title=title,
                description=description,
                legend=legend,
                modifier=" legend-score" if score_legend else "",
            )
        )
        if chart is None:
            st.html(EMPTY_STATE_HTML)
        else:
            st.altair_chart(chart, width="stretch", key=f"{key}-chart")


def student_table(students, key="er-dataset-table", height=None):
    """The prototype's table, with risk level badges as cell colours."""
    if students.empty:
        st.html(EMPTY_STATE_HTML)
        return

    def badge(value):
        colors = RISK_BADGE_COLORS.get(value, {"bg": "transparent", "fg": MUTED})
        return f"background-color: {colors['bg']}; color: {colors['fg']}; font-weight: 600;"

    if "Risk Level" in students.columns:
        table = students.style.map(badge, subset=["Risk Level"])
    else:
        table = students

    table_args = {}
    if height is not None:
        table_args["height"] = height

    st.dataframe(
        table,
        key=key,
        column_config={
            "Score": st.column_config.NumberColumn("Score", format="%.0f"),
            "Attendance": st.column_config.NumberColumn("Attendance", format="%.0f"),
            "Study Hours": st.column_config.NumberColumn("Study Hours", format="%.0f"),
            "Risk Level": st.column_config.TextColumn("Risk Level", width="small"),
        },
        **table_args,
    )


def risk_banner(risk_level, name, score, attendance):
    """Result panel for the single student risk checker."""
    colors = RISK_BADGE_COLORS[risk_level]
    reasons = {
        "Low Risk": "Score and attendance are both above the medium risk thresholds.",
        "Medium Risk": "One of the two measures is between the medium and high thresholds.",
        "High Risk": "Score or attendance fell below 60, so early support is advised.",
    }[risk_level]

    st.html(
        f"""
        <div style="border:1px solid {colors['bg']};border-radius:14px;
                    padding:20px 22px;background:{colors['bg']}">
          <span class="eyebrow" style="color:{colors['fg']}">Risk level</span>
          <div style="display:flex;align-items:center;gap:12px;margin-top:4px">
            <strong style="font-size:34px;letter-spacing:-0.035em;color:{TEXT}">
              {risk_level}
            </strong>
            {risk_badge(risk_level)}
          </div>
          <p style="margin:10px 0 0;color:{MUTED};font-size:13px;line-height:21px">
            {reasons}
          </p>
          <p style="margin:14px 0 0;color:{MUTED};font-size:13px">
            {name or "Unnamed student"} &middot; score {score} &middot;
            attendance {attendance}%
          </p>
        </div>
        """
    )


def feature_card(title, description):
    """Small card used on the Home page."""
    st.html(
        f"""
        <div style="border:1px solid rgba(224, 228, 241, 0.09);border-radius:12px;
                    padding:17px 18px;background:rgba(255, 255, 255, 0.02)">
          <span class="eyebrow" style="color:{PRIMARY}">{title}</span>
          <p style="margin:6px 0 0;color:{MUTED};font-size:13px;line-height:21px">
            {description}
          </p>
        </div>
        """
    )


def risk_legend():
    """Colour key for the three risk levels."""
    st.html(" ".join(risk_badge(level) for level in RISK_LEVELS))


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
        st.html(BRAND_HTML)
        st.html(FIELD_LABEL_HTML)

        with st.container(key="er-nav"):
            for page in PAGES:
                st.button(
                    page,
                    key=f"er-nav-{PAGE_SLUGS[page]}",
                    type="primary" if page == active_page else "tertiary",
                    on_click=navigate,
                    args=(page,),
                    width="stretch",
                )

        with st.container(key="er-sidebar-status"):
            st.html(STATUS_HTML.format(count=len(df)))


# ----------------------------------------------------------------- sections
def render_filter_card():
    """The design's filter card with its four fields."""
    course, risk, min_attendance, min_score = current_filters()
    active = active_filter_count(course, risk, min_attendance, min_score)

    with card("er-filter-card"):
        filter_card_header(reset_filters, disabled=active == 0)

        course_col, risk_col, attendance_col, score_col = st.columns(4)

        with course_col:
            field_header("Course")
            select_filter("Course", COURSE_KEY, ["All", *COURSES])

        with risk_col:
            field_header("Risk level")
            select_filter("Risk level", RISK_KEY, ["All", *RISK_LEVELS])

        with attendance_col:
            min_attendance = labeled_slider("Minimum attendance", ATTENDANCE_KEY)

        with score_col:
            min_score = labeled_slider("Minimum score", SCORE_KEY)

        filtered = apply_filters(
            df, course, risk, min_attendance, min_score
        )
        filter_footer(len(filtered), len(df), active)

    return filtered


def render_metrics(view):
    """The design's four metric cards."""
    section_heading("At a glance", "Key metrics", "Based on current filters")

    average_score = mean_of(view, "Score")
    average_attendance = mean_of(view, "Attendance")
    high_risk = count_risk(view, HIGH_RISK)
    high_risk_share = round(high_risk / len(view) * 100) if len(view) else 0

    students_col, score_col, attendance_col, risk_col = st.columns(4)

    with students_col:
        metric_card(
            "er-metric-students",
            "Students",
            len(view),
            f"{len(df)} enrolled in total",
        )

    with score_col:
        metric_card(
            "er-metric-score",
            "Average score",
            f"{average_score:.2f}",
            "Out of 100 points",
        )

    with attendance_col:
        metric_card(
            "er-metric-attendance",
            "Attendance",
            f"{average_attendance:.1f}%",
            "Average attendance rate",
        )

    with risk_col:
        metric_card(
            "er-metric-risk",
            "High risk",
            high_risk,
            f"{high_risk_share}% of filtered students",
        )


def render_charts(view):
    """The design's score and risk distribution panels."""
    section_heading("Insights", "Performance patterns", "Updated with your filters")

    score_col, risk_col = st.columns([1.28, 0.92], vertical_alignment="top")

    with score_col:
        chart_panel(
            "er-chart-scores",
            "Student scores",
            "Individual performance out of 100",
            "Score",
            score_legend= False,
            chart=score_chart(view),
        )

    with risk_col:
        chart_panel(
            "er-chart-risk",
            "Risk distribution",
            "Students grouped by current risk level",
            "Cohort",
            score_legend=False,
            chart=risk_chart(view),
        )
        risk_legend()


def render_table_card(frame, key, download_label="Download CSV", height=None):
    """Table card: heading row, CSV download and the table itself."""
    with card("er-dataset"):
        heading, actions = st.columns([3, 2], vertical_alignment="center")

        with heading:
            st.html(DATASET_HEADING_HTML.format(count=len(frame)))

        with actions:
            st.download_button(
                download_label,
                data=frame.to_csv(index=False),
                file_name=CSV_NAME,
                mime="text/csv",
                key="er-download",
            )

        student_table(frame, key=key, height=height)


# -------------------------------------------------------------------- pages
def page_dashboard():
    topbar(
        "Dashboard",
        csv_data=apply_filters(df, *current_filters()).to_csv(index=False),
        file_name=CSV_NAME,
    )
    page_intro(
        "Performance overview",
        "Student risk dashboard",
        "Monitor performance, attendance, and risk signals across your "
        "active courses.",
    )

    view = render_filter_card()
    render_metrics(view)
    render_charts(view)


def page_home():
    topbar("Home")
    page_intro(
        "Welcome",
        "EduRisk Analytics",
        "Interactive student risk monitoring dashboard built with Streamlit.",
        badge="Lab 02",
    )

    st.success("Lab 02 app is running successfully!")


def page_student_data():
    topbar("Student Data")
    page_intro(
        "Student data",
        "Full cohort overview",
        "Every record in the dataset with its calculated risk level.",
        badge=f"{len(df)} records",
    )

    render_table_card(
        df, "er-student-data-table", download_label="Download all records", height=560
    )


def page_risk_checker():
    topbar("Risk Checker")
    page_intro(
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
        risk_banner(
            classify_risk(student_score, student_attendance),
            student_name,
            student_score,
            student_attendance,
        )

    section_heading("Ethics", "Use the result responsibly")
    st.info(
        "Risk prediction should support students, not punish them. "
        "Discuss every flag with the student before acting on it."
    )


def page_about():
    topbar("About")
    page_intro(
        "About",
        "About this project",
        "Lab 02 of the Web App Development for Data Science course.",
        badge="Lab 02",
    )

    with card("er-card"):
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

    section_heading("Tools used", "Stack")
    st.html(
        '<span class="er-chip">Python</span>'
        '<span class="er-chip">Streamlit</span>'
        '<span class="er-chip">Pandas</span>'
        '<span class="er-chip">Altair</span>'
        '<span class="er-chip">VS Code</span>'
    )

    section_heading("Student information", "Author")
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