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
import streamlit as st

from design.theme import AMBER, GREEN, MUTED, PRIMARY, RED, TEXT, inject_theme


# =============================================================================
# 1. SETUP
# =============================================================================

# set_page_config has to be the very first Streamlit call in the file.
st.set_page_config(
    page_title="EduRisk Analytics",
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

# The order the risk chart draws its three bars in: calmest first, so the eye
# reads Low -> Medium -> High instead of jumping from the alarming red bar.
RISK_CHART_ORDER = [LOW_RISK, MEDIUM_RISK, HIGH_RISK]
RISK_CHART_COLORS = [GREEN, AMBER, RED]

# Chart styling that the design fixed.
SCORE_BAR_COLOR = "#7d8dff"
# Scores run out of 100, so the histogram keeps that full width instead of
# zooming to whatever the current filters happen to cover.
SCORE_DOMAIN = [0, 100]
RISK_BAR_WIDTH = {"band": 0.45}
GRID_COLOR = "rgba(153, 161, 184, 0.16)"
AXIS_LABEL_COLOR = "#767e81"
CATEGORY_LABEL_COLOR = "#858c9e"
CHART_HEIGHT = 250

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


def risk_legend():
    """The little colour key that explains the three risk pills."""
    st.html(" ".join(risk_badge(level) for level in RISK_LEVELS))


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


def risk_x_axis():
    """The risk chart's category axis, with the labels hidden.

    The three bars are told apart by colour (green / amber / red) and the
    legend chip, so the "Low Risk / Medium Risk / High Risk" text under the
    chart is noise. ``labels=False`` keeps the axis *component* present - which
    Vega-Lite needs so it merges with the overlay layer instead of dropping
    every axis on the chart (see the ``axis=None`` note in ``risk_chart``).
    """
    return alt.Axis(
        title=None,
        domain=False,
        tickColor="transparent",
        labels=False,
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


def risk_chart(students):
    """How many students sit at each of the three risk levels.

    Each bar carries its own "count - share" label, so the reader gets the
    number and the percentage without hovering.
    """
    if not has_chart_data(students, "Risk Level"):
        return None

    counts = students["Risk Level"].value_counts()
    # Only the three levels the chart draws, so an unexpected value in the
    # column cannot quietly shrink every share away from adding up to 100%.
    total = sum(int(counts.get(level, 0)) for level in RISK_CHART_ORDER)

    def row(level):
        number = int(counts.get(level, 0))
        share = percent_of(number, total)
        # An empty bar gets no label, otherwise "0 - 0%" floats over nothing.
        label = f"{number} · {share}%" if number else ""
        return {
            "Risk Level": level,
            "Students": number,
            "Share": share,
            "Label": label,
        }

    rows = [row(level) for level in RISK_CHART_ORDER]
    ticks = nice_ticks(max(item["Students"] for item in rows))

    bars = (
        alt.Chart(alt.Data(values=rows))
        .mark_bar(cornerRadiusEnd=5, width=RISK_BAR_WIDTH)
        .encode(
            x=alt.X("Risk Level:N", axis=risk_x_axis(), sort=RISK_CHART_ORDER),
            y=alt.Y(
                "Students:Q",
                scale=alt.Scale(domain=[0, ticks[-1] * 1.12]),
                axis=y_axis(ticks),
            ),
            color=alt.Color(
                "Risk Level:N",
                scale=alt.Scale(domain=RISK_CHART_ORDER, range=RISK_CHART_COLORS),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("Risk Level:N"),
                alt.Tooltip("Students:Q"),
                alt.Tooltip("Share:Q", title="Share %", format=".0f"),
            ],
        )
        .properties(height=CHART_HEIGHT)
    )

    labels = (
        alt.Chart(alt.Data(values=rows))
        .mark_text(dy=-9, fontSize=10, color=CATEGORY_LABEL_COLOR)
        .encode(
            # Deliberately no ``axis`` here. Vega-Lite merges the axis into a
            # single component shared by every layer, so writing ``axis=None``
            # on the label layer does not hide *its* axis - it deletes the bars'
            # axes too and the chart renders with no scale at all. Leaving the
            # key out lets both layers agree, and the axes survive.
            x=alt.X("Risk Level:N", sort=RISK_CHART_ORDER),
            y=alt.Y("Students:Q"),
            text=alt.Text("Label:N"),
        )
    )

    return (bars + labels).configure_view(strokeWidth=0)


def chart_panel(key, title, description, legend, chart, score_legend=False):
    """A chart inside a titled card, or the empty-state note when there is none.

    ``score_legend`` picks the legend chip style: the score panel counts
    *students* in score bands, so it gets the score-coloured dot, while the risk
    panel gets the plain cohort dot.
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
        if chart is None:
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
            "Average score",
            f"{average_of(view, 'Score'):.2f}",
            "Out of 100 points",
        )

    with attendance_col:
        metric_card(
            "er-metric-attendance",
            "Attendance",
            f"{average_of(view, 'Attendance'):.1f}%",
            "Average attendance rate",
        )

    with risk_col:
        metric_card(
            "er-metric-risk",
            "High risk",
            high_risk,
            f"{percent_of(high_risk, len(view))}% of filtered students",
        )


def render_charts(view):
    """The two chart panels, side by side."""
    section_heading("Insights", "Performance patterns", "Updated with your filters")

    score_col, risk_col = st.columns([1.28, 0.92], vertical_alignment="top")

    with score_col:
        chart_panel(
            "er-chart-scores",
            "Score distribution",
            "How scores spread out, with the 60 and 75 risk thresholds",
            "Students",
            chart=score_chart(view),
            score_legend=True,
        )

    with risk_col:
        chart_panel(
            "er-chart-risk",
            "Risk distribution",
            "Students grouped by current risk level",
            "Cohort",
            chart=risk_chart(view),
            score_legend=False,
        )
        risk_legend()


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


# =============================================================================
# 6. PAGES - one function per screen
# =============================================================================


def page_home():
    """The landing screen."""
    topbar("Home")
    page_intro(
        "Welcome",
        "EduRisk Analytics",
        "Spot the students who need support before the term ends.",
        badge="Live prototype",
    )
    st.write(
        "EduRisk Analytics is a Streamlit dashboard for student academic "
        "monitoring. It reads a cohort CSV, turns score and attendance into a "
        "risk level, and lets you filter, chart and export the view."
    )
    st.write(
        "Open **Dashboard** for the cohort overview, **Student Data** for the "
        "full table, or **Risk Checker** to score one student by hand."
    )
    st.success(f"Dataset loaded: {len(df)} students read from students.csv.")


def page_dashboard():
    """Filters, metrics and the two charts."""
    # The export button sits in the top bar, above the filter card, so it reads
    # the filters from session_state rather than from the widgets.
    topbar("Dashboard", csv_data=apply_filters(df, *current_filters()).to_csv(index=False))

    page_intro(
        "Performance overview",
        "Student risk dashboard",
        "Monitor performance, attendance, and risk signals across your "
        "active courses.",
    )

    view = render_filter_card()
    render_metrics(view)
    render_charts(view)


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

    # Only the run after the button is clicked calculates a result.
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
            <p class="er-text">Web App Development for Data Science — Lab 03</p>
            <span class="eyebrow" style="margin-top:14px">Description</span>
            <p class="er-text">
              An interactive student risk monitoring dashboard. Student data is
              loaded from students.csv with Pandas, and the risk level is
              calculated from score and attendance.
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


# =============================================================================
# 7. RUN - draw the sidebar, then show the page that was clicked
# =============================================================================

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