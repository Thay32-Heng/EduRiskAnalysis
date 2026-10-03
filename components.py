"""Streamlit equivalents of the React components in ``src/App.tsx``.

Mapping of the prototype to Streamlit:

===========================  ==================================================
React                        Streamlit
===========================  ==================================================
``navItems.map`` sidebar     ``st.button`` per page, keyed for CSS targeting
``topbar`` / breadcrumb      :func:`topbar` (HTML + ``st.download_button``)
``.filter-card``             ``st.container(key="er-filter-card")`` + widgets
``SelectField``              ``st.selectbox`` + :func:`field_header`
``RangeField``               ``st.slider`` + :func:`labeled_slider`
``.metric-card``             ``st.metric`` inside ``st.container(key=...)``
``ScoreChart`` / ``RiskChart``  Altair charts themed with the design tokens
``<table>``                  ``st.dataframe`` with a pandas ``Styler``
``risk-badge``               ``Styler`` cell colours / :func:`risk_badge` HTML
===========================  ==================================================
"""

import altair as alt
import streamlit as st

from theme import AMBER, GREEN, MUTED, PRIMARY, RED, TEXT

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