"""EduRisk Analytics.

An interactive student-risk dashboard built with Streamlit.

HOW TO READ THIS FILE
---------------------
Streamlit re-runs this entire file from the top every time you click anything,
so it is written as one straight top-to-bottom script in seven labelled steps:

    1. SETUP     - imports, the page title, and loading the design
    2. DATA      - the student table and the risk rule
    3. SETTINGS  - names, colours and the HTML blocks the design reuses
    4. WIDGETS   - small pieces like labels, headings, cards and charts
    5. PAGE PARTS- the sidebar and the bigger blocks pages share
    6. PAGES     - one function per screen
    7. RUN       - draw the sidebar and show whichever page is active

Two things live outside this file:

* ``design/theme.py``      - the colours and the stylesheet (paint only)
* ``.streamlit/config.toml`` - the same colours for Streamlit's own widgets

The only piece of real logic is :func:`classify_risk`. Swap that one function
for a model call and the whole dashboard becomes model-driven.
"""

import altair as alt
import math

import pandas as pd
import plotly.express as px
import streamlit as st

from design.theme import AMBER, GREEN, MUTED, PRIMARY, RED, TEXT, inject_theme


# =============================================================================
# 1. SETUP
# =============================================================================

# set_page_config has to be the very first Streamlit call in the file.
st.set_page_config(
    page_title="EduRisk Analytics - Lab 05",
    page_icon="🎓",
    layout="wide",
)

# inject_theme() injects the stylesheet from design/theme.py.
inject_theme()


# =============================================================================
# 2. DATA - the student table and the risk rule
# =============================================================================

# The courses that appear in the dataset.
COURSES = ["Python", "Statistics", "Database", "Web App"]

# The three risk levels, in the order the filter dropdown lists them.
LOW_RISK, MEDIUM_RISK, HIGH_RISK = "Low Risk", "Medium Risk", "High Risk"
RISK_LEVELS = [LOW_RISK, MEDIUM_RISK, HIGH_RISK]

# What "no filter chosen" looks like in the dropdowns.
ALL = "All"


def classify_risk(score, attendance):
    """Turn one student's numbers into a risk level.

    The rule has two thresholds:

    * either number below 60        -> High Risk
    * otherwise either below 75     -> Medium Risk
    * otherwise                     -> Low Risk

    A missing value cannot be cleared, so it is treated as High Risk rather than
    falling through to the safest label.
    """
    if pd.isna(score) or pd.isna(attendance):
        return HIGH_RISK
    if score < 60 or attendance < 60:
        return HIGH_RISK
    if score < 75 or attendance < 75:
        return MEDIUM_RISK
    return LOW_RISK


def load_student_data():
    """Load the student table from students.csv, with a clear error if it is missing.

    The dataset lives in students.csv next to app.py, so the app reads its data
    from disk instead of from Python literals.
    """
    try:
        students = pd.read_csv("students.csv")
    except FileNotFoundError:
        st.error(
            "students.csv was not found. Run the app from the project folder "
            "that contains students.csv."
        )
        st.stop()

    # Apply the risk rule to every loaded row.
    students["Risk Level"] = students.apply(
        lambda row: classify_risk(row["Score"], row["Attendance"]),
        axis=1,
    )
    return students


# get_risk_level is the name used in the original notebook; keep classify_risk
# as the implementation so nothing else in this file has to change.
get_risk_level = classify_risk

# Lab 04: the recent risk checks live in session state. These are the four
# columns the history table shows, in the order the lab asks for them.
HISTORY_COLUMNS = ["Student Name", "Score", "Attendance", "Risk Level"]

# The supportive message shown after a check: the alert style, the headline and
# the sentence that goes with it (Lab 04, Step 25).
RISK_FEEDBACK = {
    LOW_RISK: ("success", "Risk Level: Low Risk", "Student appears on track."),
    MEDIUM_RISK: (
        "warning",
        "Risk Level: Medium Risk",
        "Monitor progress and provide guidance.",
    ),
    HIGH_RISK: (
        "error",
        "Risk Level: High Risk",
        "Student may need additional support.",
    ),
}


def clean_student_name(name):
    """The name as typed, without the spaces around it.

    A missing name - ``None``, a NaN from a CSV, or pandas' own ``NA`` - comes
    back as ``""`` so it fails validation instead of turning into the string
    ``"nan"`` and slipping through.
    """
    if name is None or pd.isna(name):
        return ""
    return str(name).strip()


def is_valid_student_name(name):
    """True when the name is not empty once the surrounding spaces are gone."""
    return clean_student_name(name) != ""


def build_risk_record(name, score, attendance):
    """One history row: the submitted name, its numbers and the risk level.

    ``score`` and ``attendance`` come from the form's number inputs, which only
    ever hand over whole numbers inside 0-100.
    """
    return {
        "Student Name": clean_student_name(name),
        "Score": int(score),
        "Attendance": int(attendance),
        "Risk Level": classify_risk(score, attendance),
    }


def history_frame(history):
    """The session history as a table, with the four columns even when empty."""
    return pd.DataFrame(history, columns=HISTORY_COLUMNS)


def risk_feedback(level):
    """(alert style, headline, supportive sentence) for one risk level."""
    return RISK_FEEDBACK[level]


# The one shared dataset that every page reads from.
df = load_student_data()


def apply_filters(rows, course, risk, min_attendance, min_score):
    """Keep only the students who pass all four filters.

    A filter is skipped when it is switched off ("All" or 0), so the same call
    works no matter which columns the table happens to have. A row with a
    missing measure is kept: hiding it would silently drop the students the
    dashboard exists to surface.
    """
    view = rows
    if view.empty:
        return view

    if course != ALL and "Course" in view.columns:
        view = view[view["Course"] == course]

    if risk != ALL and "Risk Level" in view.columns:
        view = view[view["Risk Level"] == risk]

    if "Attendance" in view.columns:
        view = view[
            view["Attendance"].isna() | (view["Attendance"] >= min_attendance)
        ]

    if "Score" in view.columns:
        view = view[view["Score"].isna() | (view["Score"] >= min_score)]

    # .copy() keeps pandas from treating later rows as a view onto this one.
    return view.copy()


def count_active_filters(course, risk, min_attendance, min_score):
    """How many of the four filters are currently narrowing the cohort."""
    return sum(
        [
            course != ALL,
            risk != ALL,
            min_attendance > 0,
            min_score > 0,
        ]
    )


def average_of(rows, column):
    """The mean of one column, or 0.0 when it is missing or there are no rows."""
    if rows.empty or column not in rows.columns:
        return 0.0
    return float(rows[column].mean())


def count_risk(rows, level):
    """How many students sit at this risk level."""
    if rows.empty or "Risk Level" not in rows.columns:
        return 0
    return int((rows["Risk Level"] == level).sum())


def percent_of(part, whole):
    """``part`` as a whole-number percentage of ``whole``, and 0 when whole is 0."""
    if not whole:
        return 0
    # Half-up rounding, not Python's round() - round(12.5) is 12, so 1 of 8
    # would read "12%" when the reader expects 13%.
    return math.floor(part / whole * 100 + 0.5)


# ---------------------------------------------------------------- summaries
# Lab 05: a grouped summary splits the rows into groups, calculates a statistic
# for each group, then compares the groups. Both tables below are plain pandas,
# not screen code, so they can be tested without a browser.

# Every summary table keeps these columns even when there are no rows, so an
# empty filter draws headings instead of raising.
COURSE_SUMMARY_COLUMNS = [
    "Course",
    "Students",
    "Average_Score",
    "Average_Attendance",
    "Average_Study_Hours",
]
RISK_SUMMARY_COLUMNS = ["Risk Level", "Students"]


def course_summary(rows):
    """One row per course: the student count and the average measures.

    ``groupby()`` splits the rows, ``agg()`` calculates one statistic per group.
    The table is sorted weakest average score first, because the dashboard
    question is "which course needs support?" - sorting the other way would bury
    the answer at the bottom of the table.
    """
    if rows.empty or "Course" not in rows.columns:
        return pd.DataFrame(columns=COURSE_SUMMARY_COLUMNS)

    # "size" counts rows, not non-null names: a blank name must not shrink the
    # class size. dropna=False keeps a row with no course in its own group
    # instead of deleting it from the summary.
    aggregations = {"Students": ("Course", "size")}
    for label, column in (
        ("Average_Score", "Score"),
        ("Average_Attendance", "Attendance"),
        ("Average_Study_Hours", "Study Hours"),
    ):
        if column in rows.columns:
            aggregations[label] = (column, "mean")

    summary = rows.groupby("Course", dropna=False, as_index=False).agg(**aggregations)

    if "Average_Score" not in summary.columns:
        return summary.reset_index(drop=True)

    return summary.sort_values("Average_Score", kind="stable").reset_index(drop=True)


def risk_summary(rows):
    """How many students sit at each risk level.

    ``value_counts()`` counts the levels, but its order follows the data and its
    column name changes between pandas versions. So the counts are re-read in a
    fixed Low -> Medium -> High order by name: the table reads the same way every
    render, and a level nobody is on stays visible with a zero instead of
    vanishing.
    """
    if rows.empty or "Risk Level" not in rows.columns:
        return pd.DataFrame(columns=RISK_SUMMARY_COLUMNS)

    counts = rows["Risk Level"].value_counts()

    return pd.DataFrame(
        {
            "Risk Level": RISK_LEVELS,
            "Students": [int(counts.get(level, 0)) for level in RISK_LEVELS],
        }
    )


# ------------------------------------------------------------------- figures
# The Plotly charts are built in their own functions so the *figure* can be
# tested: a chart that draws the wrong bars is a bug the browser cannot reveal.
def plotly_layout(fig, show_legend=False):
    """Paint a Plotly figure in the dashboard's dark palette.

    Streamlit would otherwise apply its own light template over the custom
    colours, so the charts are rendered with ``theme=None`` and styled here.
    """
    # The margins are not decoration: at l=8 the y tick labels were sliced in
    # half, and at b=8 the x labels fell outside the card. These values were
    # measured on the rendered page.
    fig.update_layout(
        height=CHART_HEIGHT,
        margin=dict(l=44, r=14, t=16, b=34),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=show_legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        font=dict(color=CATEGORY_LABEL_COLOR, size=11),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            tickfont=dict(color=AXIS_LABEL_COLOR, size=10),
        ),
        yaxis=dict(
            gridcolor=PLOTLY_GRID_COLOR,
            zeroline=False,
            tickfont=dict(color=AXIS_LABEL_COLOR, size=10),
        ),
    )
    return fig


def risk_distribution_figure(rows):
    """Interactive bars counting students per risk level, in risk colours."""
    counts = risk_summary(rows)
    fig = px.bar(
        counts,
        x="Risk Level",
        y="Students",
        color="Risk Level",
        color_discrete_map=RISK_COLOR_MAP,
        category_orders={"Risk Level": RISK_LEVELS},
        text="Students",
        labels={"Risk Level": ""},
    )
    # The number on the bar means the value is never encoded by colour alone.
    fig.update_traces(textposition="outside", cliponaxis=False)
    return plotly_layout(fig)


def score_by_risk_figure(rows):
    """Interactive bars of each student's score, coloured by risk level."""
    fig = px.bar(
        rows,
        x="Student Name",
        y="Score",
        color="Risk Level",
        color_discrete_map=RISK_COLOR_MAP,
        category_orders={"Risk Level": RISK_LEVELS},
        labels={"Student Name": "", "Score": "Score out of 100"},
    )
    return plotly_layout(fig, show_legend=True)


# =============================================================================
# 3. SETTINGS - names, colours and the HTML blocks the design reuses
# =============================================================================

# The sidebar buttons, in order.
PAGES = ["Home", "Dashboard", "Student Data", "Risk Checker", "About"]

# Turns a page name into a CSS-friendly slug for the button's key.
PAGE_SLUGS = {
    "Home": "home",
    "Dashboard": "dashboard",
    "Student Data": "student-data",
    "Risk Checker": "risk-checker",
    "About": "about",
}

# Streamlit stores every widget's value in session_state under its key, so each
# filter needs a fixed key. The reset button writes back to these same keys.
COURSE_KEY = "er-filter-course"
RISK_KEY = "er-filter-risk"
ATTENDANCE_KEY = "er-filter-attendance"
SCORE_KEY = "er-filter-score"

CSV_FILE_NAME = "filtered_student_data.csv"

# The risk pill colours: a soft background and a brighter text, per level.
RISK_BADGE_COLORS = {
    "Low Risk": {"bg": "rgba(72, 201, 149, 0.16)", "fg": "#70dcaf"},
    "Medium Risk": {"bg": "rgba(234, 182, 82, 0.16)", "fg": "#f0c66d"},
    "High Risk": {"bg": "rgba(242, 99, 112, 0.16)", "fg": "#f9848e"},
}

# Chart styling that the design fixed.
SCORE_BAR_COLOR = "#7d8dff"
# Scores run out of 100, so the histogram keeps that full width instead of
# zooming to whatever the current filters happen to cover.
SCORE_DOMAIN = [0, 100]
GRID_COLOR = "rgba(153, 161, 184, 0.16)"
AXIS_LABEL_COLOR = "#767e81"
CATEGORY_LABEL_COLOR = "#858c9e"
CHART_HEIGHT = 250

# Lab 05: Plotly reads the same palette as the Altair charts, so "High Risk" is
# the same red in every chart on the page instead of a new colour per library.
RISK_COLOR_MAP = {LOW_RISK: GREEN, MEDIUM_RISK: AMBER, HIGH_RISK: RED}
PLOTLY_GRID_COLOR = "rgba(153, 161, 184, 0.12)"

# The four numbers the summary tables show, formatted for display only - the
# underlying frames stay numeric so the tests can compare them.
SUMMARY_COLUMN_CONFIG = {
    "Average_Score": st.column_config.NumberColumn("Average Score", format="%.2f"),
    "Average_Attendance": st.column_config.NumberColumn(
        "Average Attendance", format="%.1f%%"
    ),
    "Average_Study_Hours": st.column_config.NumberColumn(
        "Average Study Hours", format="%.1f"
    ),
    "Students": st.column_config.NumberColumn("Students", format="%d"),
}


# The HTML blocks below are the parts of the design that Streamlit has no
# widget for. Each one is a small chunk of markup that theme.py styles.

BRAND_HTML = """
<div class="brand">
  <span class="brand-mark">E</span>
  <span>
    <strong>EduRisk</strong>
    <small>Student Intelligence</small>
  </span>
</div>
"""

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

# The summary tables carry no legend pill, so they get the same heading
# without the empty pill on the right.
SUMMARY_HEADING_HTML = """
<div class="chart-heading">
  <div>
    <h4>{title}</h4>
    <p>{description}</p>
  </div>
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

HISTORY_HEADING_HTML = """
<div class="section-heading dataset-heading">
  <div>
    <span class="eyebrow">Session history</span>
    <h3>Recent risk checks</h3>
    <p>{note}</p>
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


# =============================================================================
# 4. WIDGETS - the reusable pieces the pages are built from
# =============================================================================


# ---------------------------------------------------------------- small pieces
def field_label(text, value=None):
    """The label above a filter. Shows ``value`` on the right when given."""
    shown = f'<span class="field-value">{value}</span>' if value is not None else ""
    st.html(f'<div class="field-header"><span>{text}</span>{shown}</div>')


def filter_select(label, key, options):
    """A dropdown under the design's own label. Returns what was chosen."""
    # Setting the default first stops Streamlit warning that the widget has
    # both a default and a value already sitting in session_state.
    st.session_state.setdefault(key, options[0])

    field_label(label)
    return st.selectbox(label, options, key=key, label_visibility="collapsed")


def filter_slider(label, key, default=0):
    """A slider under the design's own label, showing its value live. Returns it.

    Streamlit paints a widget only after the line that creates it, but this
    label has to sit *above* the slider and show the number. So we print the
    value we saw on the previous run, and the slider's on-change callback
    stores the new one ready for next time.
    """
    shown_key = f"{key}_shown"
    st.session_state.setdefault(key, default)
    st.session_state.setdefault(shown_key, default)

    def remember_value():
        st.session_state[shown_key] = st.session_state[key]

    field_label(label, st.session_state[shown_key])
    return st.slider(
        label,
        min_value=0,
        max_value=100,
        step=1,
        key=key,
        label_visibility="collapsed",
        on_change=remember_value,
    )


def risk_badge(level):
    """The coloured 'High Risk' pill used in the legend and the result panel."""
    slug = level.lower().replace(" ", "-")
    return f'<span class="risk-badge {slug}">{level}</span>'


def filter_footer(shown, total, active):
    """The 'Showing 8 of 8 students' line, with a chip counting active filters."""
    if active:
        word = "filter" if active == 1 else "filters"
        chip = f'<span class="filter-chip">{active} active {word}</span>'
    else:
        chip = ""

    st.html(FILTER_FOOTER_HTML.format(shown=shown, total=total, chip=chip))


# -------------------------------------------------------------------- headings
def topbar(page_label, csv_data=None):
    """The sticky bar at the top: the page name, plus the CSV export button."""
    with st.container(key="er-topbar"):
        breadcrumb, export = st.columns([6, 2], vertical_alignment="center")

        with breadcrumb:
            st.html(TOPBAR_CONTEXT_HTML.format(page=page_label))

        with export:
            if csv_data is not None:
                st.download_button(
                    "Export report",
                    data=csv_data,
                    file_name=CSV_FILE_NAME,
                    mime="text/csv",
                    key="er-export",
                )
            else:
                st.empty()


def page_intro(eyebrow, title, description, badge="Live dataset"):
    """The big hero block at the top of every page."""
    st.html(
        INTRO_HTML.format(
            eyebrow=eyebrow, title=title, description=description, badge=badge
        )
    )


def section_heading(eyebrow, title, note="", compact=False):
    """A smaller heading row that separates the sections of a page."""
    st.html(
        SECTION_HEADING_HTML.format(
            eyebrow=eyebrow,
            title=title,
            note=note,
            modifier=" compact" if compact else "",
        )
    )


def metric_card(key, label, value, caption):
    """One of the four number cards, with a small caption underneath."""
    with st.container(key=key):
        st.metric(label, value)
        st.html(f'<span class="er-metric-caption">{caption}</span>')


# ---------------------------------------------------------------------- charts
def y_axis(ticks):
    """A number axis with the design's dashed grid lines and muted labels."""
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
    """A category axis with the design's angled labels."""
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


def has_chart_data(rows, *columns):
    """True when the table actually has the columns a chart needs."""
    return not rows.empty and all(column in rows.columns for column in columns)


def histogram_axis():
    """A flat number axis for the score histogram, so the bins read as a scale."""
    return alt.Axis(
        title=None,
        values=[0, 20, 40, 60, 80, 100],
        domain=False,
        tickColor="transparent",
        labelColor=CATEGORY_LABEL_COLOR,
        labelFontSize=10,
        labelPadding=6,
        grid=False,
    )


def nice_ticks(max_value, divisions=5):
    """Rounded whole-number ticks covering ``0`` up to ``max_value``.

    Counts are small integers, so a fixed axis like ``range(0, top + 1)`` ends
    up crowded or stops short of the tallest bar. Rounding the step to a "nice"
    number (1, 2, 5, 10 ...) keeps roughly ``divisions`` gridlines whatever the
    cohort size is.
    """
    if max_value <= 0:
        return [0, 1]

    step = 10 ** math.floor(math.log10(max_value / divisions))
    for multiplier in (1, 2, 2.5, 5, 10, 20):
        if multiplier * step >= max_value / divisions:
            step = max(1, int(multiplier * step))
            break

    end = math.ceil(max_value / step) * step
    return list(range(0, end + 1, step))


def score_chart(students):
    """How the cohort's scores spread out, as a histogram out of 100.

    The two dashed rules mark the thresholds :func:`classify_risk` uses - red at
    60 (below it a student is High Risk) and amber at 75 (below it, Medium) -
    so a bar sitting left of a line reads as "this group needs support".
    """
    if not has_chart_data(students, "Score"):
        return None

    # Vega bins step by 5 and its last bin is [100, 105), so a perfect score
    # would sit in a bar of its own past the 100 mark. Capping the edge at 95
    # folds 100 into the 95-100 band, which only ever makes the tallest bar
    # taller than Vega's own - so the y axis can be generous, never too short.
    counts: dict[int, int] = {}
    for value in students["Score"]:
        # A blank score in a real CSV would raise on int(); skip it instead of
        # taking the whole page down.
        if pd.isna(value):
            continue
        edge = min(int(value // 5) * 5, 95)
        counts[edge] = counts.get(edge, 0) + 1

    if not counts:
        return None

    ticks = nice_ticks(max(counts.values()))

    bars = (
        alt.Chart(students)
        .mark_bar(color=SCORE_BAR_COLOR, cornerRadiusEnd=4)
        .encode(
            x=alt.X(
                "Score:Q",
                bin=alt.Bin(step=5),
                scale=alt.Scale(domain=SCORE_DOMAIN),
                axis=histogram_axis(),
            ),
            y=alt.Y(
                "count():Q",
                scale=alt.Scale(domain=[0, ticks[-1] * 1.12]),
                axis=y_axis(ticks),
            ),
            tooltip=[
                alt.Tooltip("Score:Q", bin=alt.Bin(step=5), title="Score band"),
                alt.Tooltip("count():Q", title="Students"),
            ],
        )
        .properties(height=CHART_HEIGHT)
    )

    thresholds = (
        alt.Chart(
            alt.Data(
                values=[
                    {"Score": 60, "Threshold": "High"},
                    {"Score": 75, "Threshold": "Medium"},
                ]
            )
        )
        .mark_rule(strokeDash=[4, 3], strokeWidth=1.2, opacity=0.7)
        .encode(
            # The same fixed scale as the bars, so 60 and 75 sit at their real
            # positions instead of sliding around with the filtered data.
            x=alt.X("Score:Q", scale=alt.Scale(domain=SCORE_DOMAIN)),
            color=alt.Color(
                "Threshold:N",
                scale=alt.Scale(domain=["High", "Medium"], range=[RED, AMBER]),
                legend=None,
            ),
        )
    )

    # Some breathing room above the tallest bar, so the "n - pct" text drawn
    # over it is never clipped by the frame.
    return (bars + thresholds).configure_view(strokeWidth=0)


def chart_panel(
    key,
    title,
    description,
    legend,
    chart=None,
    score_legend=False,
    render=None,
):
    """A chart inside a titled card, or the empty-state note when there is none.

    ``score_legend`` picks the legend chip style: the score panel counts
    *students* in score bands, so it gets the score-coloured dot, while the risk
    panel gets the plain cohort dot.

    ``render`` is for the charts that cannot be handed over as one object - the
    Streamlit and Plotly charts draw themselves through a small function, and an
    empty view still falls back to the same empty-state note.
    """
    with st.container(key=key):
        st.html(
            CHART_HEADING_HTML.format(
                title=title,
                description=description,
                legend=legend,
                modifier=" legend-score" if score_legend else "",
            )
        )
        if render is not None:
            render()
        elif chart is None:
            st.html(EMPTY_STATE_HTML)
        else:
            st.altair_chart(chart, width="stretch", key=f"{key}-chart")


# ----------------------------------------------------------------------- table
def student_table(students, key="er-dataset-table", height=None):
    """The student table, with each risk level painted as a coloured cell."""
    if students.empty:
        st.html(EMPTY_STATE_HTML)
        return

    def paint_cell(level):
        colors = RISK_BADGE_COLORS.get(level, {"bg": "transparent", "fg": MUTED})
        return f"background-color: {colors['bg']}; color: {colors['fg']}; font-weight: 600;"

    table = students
    if "Risk Level" in students.columns:
        table = students.style.map(paint_cell, subset=["Risk Level"])

    # Only pass a height when one was asked for, so the table sizes itself.
    sizing = {"height": height} if height is not None else {}

    st.dataframe(
        table,
        key=key,
        column_config={
            "Score": st.column_config.NumberColumn("Score", format="%.0f"),
            "Attendance": st.column_config.NumberColumn("Attendance", format="%.0f"),
            "Study Hours": st.column_config.NumberColumn("Study Hours", format="%.0f"),
            "Risk Level": st.column_config.TextColumn("Risk Level", width="small"),
        },
        **sizing,
    )


# --------------------------------------------------------------------- results
def risk_banner(level, name, score, attendance):
    """The big result panel on the Risk Checker page."""
    colors = RISK_BADGE_COLORS[level]

    # Why this level was chosen, in one sentence.
    reasons = {
        "Low Risk": "Score and attendance are both above the medium risk thresholds.",
        "Medium Risk": "One of the two measures is between the medium and high thresholds.",
        "High Risk": "Score or attendance fell below 60, so early support is advised.",
    }[level]

    st.html(
        f"""
        <div style="border:1px solid {colors['bg']};border-radius:14px;
                    padding:20px 22px;background:{colors['bg']}">
          <span class="eyebrow" style="color:{colors['fg']}">Risk level</span>
          <div style="display:flex;align-items:center;gap:12px;margin-top:4px">
            <strong style="font-size:34px;letter-spacing:-0.035em;color:{TEXT}">
              {level}
            </strong>
            {risk_badge(level)}
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


def show_risk_feedback(level):
    """The colour-coded supportive message that follows a risk check.

    Low Risk is a green success message, Medium Risk a yellow warning and High
    Risk a red error, so the result reads the same way whether it is scanned by
    a lecturer or read by the student it is about.
    """
    kind, headline, advice = risk_feedback(level)
    message = f"**{headline}** — {advice}"

    if kind == "success":
        st.success(message)
    elif kind == "warning":
        st.warning(message)
    else:
        st.error(message)


# ============================================================================
# 5. PAGE PARTS
# ============================================================================


def navigate(page):
    """Sidebar button callback: remember which page was clicked."""
    st.session_state.page = page


def reset_filters():
    """Reset button callback: put all four filters back to their defaults."""
    st.session_state[COURSE_KEY] = ALL
    st.session_state[RISK_KEY] = ALL
    st.session_state[ATTENDANCE_KEY] = 0
    st.session_state[SCORE_KEY] = 0
    # The two labels showing the slider values need clearing too.
    st.session_state[f"{ATTENDANCE_KEY}_shown"] = 0
    st.session_state[f"{SCORE_KEY}_shown"] = 0


def clear_risk_history():
    """Clear History callback: empty the history and drop the last result."""
    st.session_state["risk_history"] = []
    st.session_state.risk_result = None
    # Read once by render_risk_history to confirm the click, then thrown away.
    st.session_state["er-history-cleared"] = True


def current_filters():
    """The four filter values as they stand right now.

    The top bar's export button is drawn *above* the filter card, so it cannot
    ask the widgets themselves for their values yet. Streamlit keeps every
    widget's value in ``st.session_state``, so read them from there instead.
    """
    return (
        st.session_state.get(COURSE_KEY, ALL),
        st.session_state.get(RISK_KEY, ALL),
        st.session_state.get(ATTENDANCE_KEY, 0),
        st.session_state.get(SCORE_KEY, 0),
    )


def render_sidebar(active_page):
    """The brand, the five navigation buttons and the status card."""
    with st.sidebar:
        st.html(BRAND_HTML)
        st.html('<p class="field-label">Workspace</p>')

        with st.container(key="er-nav"):
            for page in PAGES:
                # The active page gets the primary button style.
                is_active = page == active_page
                st.button(
                    page,
                    key=f"er-nav-{PAGE_SLUGS[page]}",
                    type="primary" if is_active else "tertiary",
                    on_click=navigate,
                    args=(page,),
                    width="stretch",
                )

        with st.container(key="er-sidebar-status"):
            st.html(STATUS_HTML.format(count=len(df)))


def render_filter_card():
    """Draw the four filters and return the rows that pass them."""
    # The Reset button is drawn before the four filter widgets, so it cannot ask
    # them for their values yet. Read them from session_state instead.
    filters_already_set = count_active_filters(*current_filters())

    with st.container(key="er-filter-card"):
        heading, action = st.columns([6, 1], vertical_alignment="center")

        with heading:
            section_heading("Filters", "Refine the cohort", compact=True)

        with action:
            st.button(
                "Reset filters",
                key="er-reset",
                type="tertiary",
                disabled=filters_already_set == 0,
                on_click=reset_filters,
                width="stretch",
            )

        course_col, risk_col, attendance_col, score_col = st.columns(4)

        # Each filter returns its own value, so read all four filters straight
        # off the widgets that produced them.
        with course_col:
            course = filter_select("Course", COURSE_KEY, [ALL, *COURSES])

        with risk_col:
            risk = filter_select("Risk level", RISK_KEY, [ALL, *RISK_LEVELS])

        with attendance_col:
            min_attendance = filter_slider("Minimum attendance", ATTENDANCE_KEY)

        with score_col:
            min_score = filter_slider("Minimum score", SCORE_KEY)

        view = apply_filters(df, course, risk, min_attendance, min_score)
        filter_footer(
            len(view),
            len(df),
            count_active_filters(course, risk, min_attendance, min_score),
        )

    return view


def render_metrics(view):
    """The four number cards across the top of the dashboard."""
    section_heading("At a glance", "Key metrics", "Based on current filters")

    high_risk = count_risk(view, HIGH_RISK)

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
            "Average Score",
            f"{average_of(view, 'Score'):.2f}",
            "Out of 100 points",
        )

    with attendance_col:
        metric_card(
            "er-metric-attendance",
            "Average Attendance",
            f"{average_of(view, 'Attendance'):.1f}%",
            "Average attendance rate",
        )

    with risk_col:
        metric_card(
            "er-metric-risk",
            "High Risk",
            high_risk,
            f"{percent_of(high_risk, len(view))}% of filtered students",
        )


def render_summaries(view):
    """The two grouped summary tables, side by side.

    A grouped summary answers "how do the courses compare?", which a list of
    individual students cannot: the rows are already reduced to one row per
    group before they reach the screen.
    """
    section_heading(
        "Grouped summaries",
        "Course and risk summaries",
        "One row per group, calculated from the filtered rows",
    )

    course_col, risk_col = st.columns([1.22, 0.78], vertical_alignment="top")

    with course_col:
        with st.container(key="er-summary-course"):
            st.html(
                SUMMARY_HEADING_HTML.format(
                    title="Course summary",
                    description="Average score, attendance and study hours per course",
                )
            )
            table = course_summary(view)
            if table.empty:
                st.html(EMPTY_STATE_HTML)
            else:
                st.dataframe(
                    table,
                    hide_index=True,
                    width="stretch",
                    column_config=SUMMARY_COLUMN_CONFIG,
                )

    with risk_col:
        with st.container(key="er-summary-risk"):
            st.html(
                SUMMARY_HEADING_HTML.format(
                    title="Risk level summary",
                    description="How the filtered students split across the three levels",
                )
            )
            table = risk_summary(view)
            if table.empty:
                st.html(EMPTY_STATE_HTML)
            else:
                st.dataframe(
                    table,
                    hide_index=True,
                    width="stretch",
                    column_config=SUMMARY_COLUMN_CONFIG,
                )


def render_streamlit_charts(view):
    """The two basic Streamlit charts: they need no figure object at all."""
    section_heading(
        "Streamlit charts",
        "Quick charts",
        "Built straight from the filtered dataframe",
    )

    score_col, course_col = st.columns(2, vertical_alignment="top")
    empty = view.empty
    can_score = has_chart_data(view, "Student Name", "Score")
    can_count = has_chart_data(view, "Course")

    with score_col:
        chart_panel(
            "er-chart-streamlit-scores",
            "Student scores",
            "Every filtered student's score, out of 100",
            "Students",
            score_legend=True,
            render=None
            if empty or not can_score
            else lambda: st.bar_chart(
                # Horizontal bars keep eight student names readable; vertical
                # bars forced the labels to rotate on their side.
                view.set_index("Student Name")["Score"],
                color=PRIMARY,
                height=CHART_HEIGHT,
                horizontal=True,
            ),
        )

    with course_col:
        chart_panel(
            "er-chart-streamlit-courses",
            "Students by course",
            "How many filtered students each course holds",
            "Cohort",
            score_legend=False,
            render=None
            if empty or not can_count
            else lambda: st.bar_chart(
                view["Course"].value_counts(),
                color=PRIMARY,
                height=CHART_HEIGHT,
                horizontal=True,
            ),
        )


def render_plotly_charts(view):
    """The interactive Plotly charts: hover for the exact numbers."""
    section_heading(
        "Interactive Plotly charts",
        "Hover to explore",
        "Same data as above, with tooltips and risk-coloured bars",
    )

    risk_col, score_col = st.columns([0.8, 1.2], vertical_alignment="top")
    empty = view.empty
    can_risk = has_chart_data(view, "Risk Level")
    can_score = has_chart_data(view, "Student Name", "Score", "Risk Level")

    with risk_col:
        chart_panel(
            "er-chart-plotly-risk",
            "Risk level distribution",
            "Students per risk level, counted from the filtered rows",
            "Cohort",
            render=None
            if empty or not can_risk
            else lambda: st.plotly_chart(
                risk_distribution_figure(view),
                theme=None,
                width="stretch",
                config={"displayModeBar": False},
            ),
        )

    with score_col:
        chart_panel(
            "er-chart-plotly-scores",
            "Student scores by risk level",
            "Each student's score, coloured by the risk level it produced",
            "Cohort",
            render=None
            if empty or not can_score
            else lambda: st.plotly_chart(
                score_by_risk_figure(view),
                theme=None,
                width="stretch",
                config={"displayModeBar": False},
            ),
        )


def render_charts(view):
    """The score distribution, with both risk thresholds drawn in."""
    section_heading(
        "Distribution",
        "Where the scores fall",
        "The 60 and 75 lines are the risk thresholds",
    )

    chart_panel(
        "er-chart-scores",
        "Score distribution",
        "How the filtered scores spread out, band by band",
        "Students",
        chart=score_chart(view),
        score_legend=True,
    )


def render_records(view):
    """Every filtered student, in full, so a chart can always be checked."""
    section_heading(
        "Filtered records",
        "Filtered student records",
        "The rows behind every number above",
    )

    with st.container(key="er-records"):
        if view.empty:
            st.html(EMPTY_STATE_HTML)
        else:
            student_table(view, key="er-filtered-records-table")


def render_table_card(rows, table_key, button_label, height=None):
    """A titled card holding the table and its download button."""
    with st.container(key="er-dataset"):
        heading, actions = st.columns([3, 2], vertical_alignment="center")

        with heading:
            st.html(DATASET_HEADING_HTML.format(count=len(rows)))

        with actions:
            st.download_button(
                button_label,
                data=rows.to_csv(index=False),
                file_name=CSV_FILE_NAME,
                mime="text/csv",
                key="er-download",
            )

        student_table(rows, key=table_key, height=height)


def render_risk_history():
    """The Recent Risk Checks card: the session table and its Clear button.

    Clearing runs as the button's callback, before the table is drawn, so one
    click empties the table and the page falls straight back to "No risk checks
    yet." instead of needing a second page load.
    """
    history = st.session_state["risk_history"]

    with st.container(key="er-card"):
        heading, action = st.columns([4, 1], vertical_alignment="center")

        with heading:
            if history:
                note = (
                    f"{len(history)} check"
                    f"{'' if len(history) == 1 else 's'} stored in this session"
                )
            else:
                note = "Nothing checked yet"
            st.html(HISTORY_HEADING_HTML.format(note=note))

        with action:
            st.button(
                "Clear History",
                key="er-clear",
                type="tertiary",
                on_click=clear_risk_history,
                disabled=not history,
                width="stretch",
            )

        if history:
            student_table(history_frame(history), key="er-history-table")
        else:
            st.info("No risk checks yet.")

        # The callback above clears the list before this content is drawn, so
        # the click is confirmed on the same page load instead of the next one.
        if st.session_state.pop("er-history-cleared", False):
            st.success("Risk check history cleared.")


# =============================================================================
# 6. PAGES - one function per screen
# =============================================================================


def page_home():
    """The landing screen."""
    topbar("Home")
    page_intro(
        "Welcome",
        "EduRisk Analytics",
        "Interactive Dashboard with Visualization and Filters",
        badge="Live prototype",
    )
    st.write("Welcome to Lab 05.")
    st.write(
        "EduRisk Analytics is a Streamlit dashboard for student academic "
        "monitoring. It reads a cohort CSV, turns score and attendance into a "
        "risk level, and lets you filter, summarise, chart and export the view."
    )
    st.write(
        "Open **Dashboard** for the interactive view — filters, metric cards, "
        "grouped summary tables, Streamlit charts and Plotly charts. "
        "**Student Data** shows the full table, and **Risk Checker** scores one "
        "student by hand through a validated form with session history."
    )
    st.success(
        f"Lab 05 app is running successfully — {len(df)} students read from "
        "students.csv."
    )


def page_dashboard():
    """The Lab 05 analytical dashboard: filter, summarise, visualise, inspect."""
    # The export button sits in the top bar, above the filter card, so it reads
    # the filters from session_state rather than from the widgets.
    topbar("Dashboard", csv_data=apply_filters(df, *current_filters()).to_csv(index=False))

    page_intro(
        "Performance overview",
        "Student risk dashboard",
        "Filter the cohort by course, risk level and attendance, then read the "
        "summary tables and charts that answer the four dashboard questions.",
    )

    view = render_filter_card()

    # One warning for the whole page, before any section is drawn: every block
    # below also guards itself, so an empty filter never shows a stray 0 or a
    # chart of nothing.
    if view.empty:
        st.warning(
            "No students match the selected filters. Please adjust the filters."
        )

    render_metrics(view)
    render_summaries(view)
    render_streamlit_charts(view)
    render_plotly_charts(view)
    render_charts(view)
    render_records(view)

    section_heading("Ethics", "Support, not punishment")
    st.warning(
        "Ethics Reminder: Visualizations should support students and guide "
        "academic support decisions, not label or punish students."
    )


def page_student_data():
    """Every student in one table, with no filters, plus a data-inspection view."""
    topbar("Student Data")
    page_intro(
        "Student data",
        "Full cohort overview",
        "Every record in the dataset with its calculated risk level.",
        badge=f"{len(df)} records",
    )

    # Data inspection block: shape, columns and a preview of the raw table.
    st.subheader("Data Inspection")
    st.write("Rows and Columns:", df.shape)
    st.write("Column Names:", df.columns.tolist())
    st.write("First 5 Rows:")
    st.dataframe(df.head())

    render_table_card(
        df,
        table_key="er-student-data-table",
        button_label="Download all records",
        height=560,
    )


def page_risk_checker():
    """Check a single student, entered by hand."""
    topbar("Risk Checker")
    page_intro(
        "Risk checker",
        "Single student risk checker",
        "Enter one student's results to see the risk level and the reasoning "
        "behind it.",
        badge="Instant result",
    )

    st.info(
        "This tool is for academic support. Risk results should help students, "
        "not label or punish them."
    )

    # A form collects all three inputs before anything is calculated.
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

    # Only the run after the button is clicked validates and calculates. An
    # empty name is stopped here, so it can never reach the history table.
    if submitted:
        if not is_valid_student_name(name):
            # Drop the previous result too: leaving it on screen next to the
            # warning would read as if the rejected submit had produced it.
            st.session_state.risk_result = None
            st.warning("Please enter the student name.")
        else:
            record = build_risk_record(name, score, attendance)
            st.session_state["risk_history"].append(record)
            st.session_state.risk_result = record

    # The last check stays on screen until the next valid check, a rejected
    # empty-name submit, or a Clear History.
    latest = st.session_state.get("risk_result")
    if isinstance(latest, dict):
        level = latest["Risk Level"]
        risk_banner(
            level,
            latest["Student Name"],
            latest["Score"],
            latest["Attendance"],
        )
        show_risk_feedback(level)

    render_risk_history()

    section_heading("Ethics", "Use the result responsibly")
    st.warning(
        "Ethics Reminder: Risk results should be used as guidance for support, "
        "not as final judgment about a student."
    )


def page_about():
    """Project details and the author."""
    topbar("About")
    page_intro(
        "About",
        "About this project",
        "A student risk monitoring dashboard built with Streamlit and Pandas.",
        badge="Course project",
    )

    with st.container(key="er-card"):
        st.html(
            """
            <span class="eyebrow">Project theme</span>
            <p class="er-text">EduRisk Analytics</p>
            <span class="eyebrow" style="margin-top:14px">Course</span>
            <p class="er-text">Web App Development for Data Science — Lab 05</p>
            <span class="eyebrow" style="margin-top:14px">Topic</span>
            <p class="er-text">Visualization and Interactivity</p>
            <span class="eyebrow" style="margin-top:14px">Description</span>
            <p class="er-text">
              An interactive student risk monitoring dashboard. Student data is
              loaded from students.csv with Pandas, and the risk level is
              calculated from score and attendance. This version turns the
              Dashboard into an analytical view: filters, filtered metric cards,
              grouped summary tables, Streamlit charts and interactive Plotly
              charts, with the reliable Risk Checker from Lab 04 kept intact.
            </p>
            <span class="eyebrow" style="margin-top:14px">Live demo</span>
            <p class="er-text">
              <a href="https://thay-edurisk.streamlit.app/"
                 target="_blank" rel="noopener">thay-edurisk.streamlit.app</a>
            </p>
            """
        )

    st.info(
        "This version improves the Dashboard page using grouped summaries, "
        "interactive filters, Streamlit charts, and Plotly charts."
    )

    section_heading("Tools used", "Stack")
    st.html(
        '<span class="er-chip">Python</span>'
        '<span class="er-chip">Streamlit</span>'
        '<span class="er-chip">Pandas</span>'
        '<span class="er-chip">Altair</span>'
        '<span class="er-chip">Plotly</span>'
        '<span class="er-chip">VS Code</span>'
    )

    section_heading("Student information", "Author")
    st.html(
        '<span class="er-chip">Heng Sengthay</span>'
        '<span class="er-chip">Student ID 73191</span>'
        '<span class="er-chip">Class M2</span>'
    )


# =============================================================================
# 7. RUN - draw the sidebar, then show the page that was clicked
# =============================================================================

# Lab 04: the recent risk checks are temporary memory. Session state is created
# once per browser session and dropped on reload, which is exactly the lifetime
# the lab asks for — nothing is written back to students.csv.
if "risk_history" not in st.session_state:
    st.session_state["risk_history"] = []

if "page" not in st.session_state:
    st.session_state.page = "Home"

active_page = st.session_state.page
render_sidebar(active_page)

# The page name is the key, so the sidebar and the router can never disagree.
PAGE_FUNCTIONS = {
    "Home": page_home,
    "Dashboard": page_dashboard,
    "Student Data": page_student_data,
    "Risk Checker": page_risk_checker,
    "About": page_about,
}

PAGE_FUNCTIONS[active_page]()