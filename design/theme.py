"""EduRisk Analytics visual theme for Streamlit.

Ported from the Figma Make design (``src/index.css``). Every rule that styled a
custom class in the prototype is kept as-is and simply reused by the HTML
snippets in :mod:`components`, and the rules that styled real widgets (nav
buttons, select boxes, sliders, tables, cards) are re-targeted at Streamlit's
``data-testid`` DOM instead.

The palette constants below are the single source of truth for the design and
are mirrored in ``.streamlit/config.toml`` so Streamlit's own widgets use the
same colours.
"""

import streamlit as st

BACKGROUND = "#0c0e14"
SURFACE = "#141720"
SURFACE_RAISED = "#191d28"
BORDER = "rgba(224, 228, 241, 0.09)"
MUTED = "#9298aa"
PRIMARY = "#7282ff"
PRIMARY_SOFT = "rgba(114, 130, 255, 0.13)"
GREEN = "#48c995"
AMBER = "#eab652"
RED = "#f26370"
TEXT = "#eef0f6"

CSS = """
@import url("https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&display=swap");

:root {
  --er-background: #0c0e14;
  --er-surface: #141720;
  --er-surface-raised: #191d28;
  --er-border: rgba(224, 228, 241, 0.09);
  --er-muted: #9298aa;
  --er-primary: #7282ff;
  --er-primary-soft: rgba(114, 130, 255, 0.13);
  --er-green: #48c995;
  --er-amber: #eab652;
  --er-red: #f26370;
  --er-text: #eef0f6;
}

.stApp,
.stApp * {
  font-family: "Source Sans 3", "Segoe UI", system-ui, -apple-system, sans-serif;
}

/* the blanket font-family above also hits Streamlit's icon ligatures */
[data-testid="stIconMaterial"] {
  font-family: "Material Symbols Rounded" !important;
}

/* ---------------------------------------------------------------- chrome */
header[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stAppDeployButton"],
#MainMenu,
footer {
  display: none !important;
}

.stApp {
  color: var(--er-text);
  background:
    radial-gradient(circle at 88% 0%, rgba(114, 130, 255, 0.08), transparent 26rem),
    var(--er-background);
}

[data-testid="stAppViewContainer"] > .main {
  background: transparent;
}

[data-testid="stMain"] {
  padding-top: 0;
}

[data-testid="stMainBlockContainer"] {
  max-width: 1180px;
  padding: 0 32px 80px;
}

[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"] {
  gap: 0.9rem;
}

/* --------------------------------------------------------------- sidebar */
/* Streamlit writes the sidebar width inline and drops it to 0 when the sidebar
   is collapsed, so the design width is only forced while it is expanded -
   otherwise the collapsed panel leaves a 248px hole in the layout. */
section[data-testid="stSidebar"][aria-expanded="true"] {
  width: 248px !important;
  min-width: 248px !important;
  max-width: 248px !important;
}

section[data-testid="stSidebar"] {
  background: rgba(17, 19, 27, 0.96);
  border-right: 1px solid var(--er-border);
}

section[data-testid="stSidebar"] > div {
  background: transparent;
}

[data-testid="stSidebarContent"] {
  display: flex;
  flex-direction: column;
  padding: 28px 20px 24px;
}

[data-testid="stSidebarUserContent"] {
  display: flex;
  flex: 1 1 auto;
  flex-direction: column;
  width: 100%;
  min-height: 0;
  padding-bottom: 24px;
}

[data-testid="stSidebarResizer"] {
  background: transparent;
}

/* Streamlit wraps the sidebar content in two block wrappers; they have to
   stretch so the status card can be pushed to the bottom of the viewport. */
[data-testid="stSidebarUserContent"] > div {
  display: flex;
  flex: 1 1 auto;
  flex-direction: column;
  min-height: 0;
}

[data-testid="stSidebarUserContent"] > div > [data-testid="stVerticalBlock"] {
  display: flex;
  flex: 1 1 auto;
  flex-direction: column;
}

[data-testid="stSidebarUserContent"] div:has(> .st-key-er-sidebar-status) {
  margin-top: auto;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 42px;
}

.brand-mark {
  display: grid;
  width: 38px;
  height: 38px;
  place-items: center;
  border: 1px solid rgba(132, 145, 255, 0.45);
  border-radius: 11px;
  color: #fff;
  background: linear-gradient(145deg, #8190ff, #5968db);
  box-shadow: 0 8px 24px rgba(89, 104, 219, 0.24);
  font-size: 18px;
  font-weight: 700;
}

.brand > span:last-child,
.sidebar-status > span:last-child {
  display: grid;
}

.brand strong {
  font-size: 18px;
  line-height: 21px;
  font-weight: 600;
}

.brand small,
.sidebar-status small {
  color: var(--er-muted);
  font-size: 12px;
  line-height: 17px;
}

.field-label {
  margin: 0 10px 10px;
  color: #747b8f;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

/* nav: Streamlit buttons styled as the prototype's .nav-item */
.st-key-er-nav {
  gap: 5px !important;
}

.st-key-er-nav button {
  justify-content: flex-start !important;
  gap: 11px;
  padding: 10px 11px;
  border: 0;
  border-radius: 9px;
  background: transparent;
  box-shadow: none;
  color: #aeb3c2;
  font-size: 14px;
  font-weight: 400;
  text-align: left;
  transition: color 160ms ease, background 160ms ease;
}

.st-key-er-nav button::before {
  display: grid;
  width: 26px;
  height: 26px;
  flex: 0 0 auto;
  place-items: center;
  border: 1px solid var(--er-border);
  border-radius: 7px;
  background: rgba(255, 255, 255, 0.025);
  color: #9299ad;
  font-size: 10px;
  font-weight: 600;
}

.st-key-er-nav button > div {
  justify-content: flex-start !important;
}

.st-key-er-nav button:hover {
  background: rgba(255, 255, 255, 0.035);
  color: #f6f7fb;
}

.st-key-er-nav button[data-testid="stBaseButton-primary"] {
  background: var(--er-primary-soft);
  color: #fff;
  box-shadow: inset -3px 0 0 var(--er-primary);
}

.st-key-er-nav button[data-testid="stBaseButton-primary"]::before {
  border-color: rgba(114, 130, 255, 0.32);
  background: rgba(114, 130, 255, 0.12);
  color: #aeb7ff;
}

.st-key-er-nav-home button::before { content: "H"; }
.st-key-er-nav-dashboard button::before { content: "D"; }
.st-key-er-nav-student-data button::before { content: "S"; }
.st-key-er-nav-risk-checker button::before { content: "R"; }
.st-key-er-nav-about button::before { content: "A"; }

.sidebar-status {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px;
  border: 1px solid var(--er-border);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.02);
}

.sidebar-status strong {
  font-size: 13px;
  font-weight: 400;
}

.status-dot,
.live-dot {
  width: 7px;
  height: 7px;
  flex: 0 0 auto;
  border-radius: 50%;
  background: var(--er-green);
  box-shadow: 0 0 0 4px rgba(72, 201, 149, 0.1);
}

/* ---------------------------------------------------------------- topbar */
.topbar {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0 -32px 0;
  padding: 14px 32px;
  border-bottom: 1px solid var(--er-border);
  background: rgba(12, 14, 20, 0.78);
  backdrop-filter: blur(18px);
}

.st-key-er-topbar > div {
  align-items: center;
  gap: 10px;
}

.topbar-context {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.topbar-context span {
  color: #6f7586;
}

.topbar-context span::after {
  margin-left: 8px;
  color: #484d5c;
  content: "/";
}

.topbar-context strong {
  font-weight: 600;
}

/* ----------------------------------------------------------------- intro */
.intro {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
  margin: 34px 0 30px;
}

.eyebrow {
  display: block;
  margin-bottom: 6px;
  color: #71798e;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.13em;
}

.intro h2 {
  margin: 0;
  font-size: 42px;
  font-weight: 700;
  letter-spacing: -0.035em;
  line-height: 1.08;
}

.intro p {
  margin: 12px 0 0;
  color: var(--er-muted);
  font-size: 16px;
  line-height: 25px;
}

.intro-summary {
  display: flex;
  flex: 0 0 auto;
  align-items: center;
  gap: 9px;
  margin-top: 22px;
  padding: 9px 12px;
  border: 1px solid var(--er-border);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.02);
  color: #adb3c3;
  font-size: 12px;
  white-space: nowrap;
}

/* ------------------------------------------------------- cards / panels */
.filter-card,
.metric-card,
.chart-panel,
.dataset-section,
.er-card {
  border: 1px solid var(--er-border);
  border-radius: 14px;
  background: linear-gradient(145deg, rgba(25, 29, 40, 0.94), rgba(18, 21, 29, 0.94));
  box-shadow: 0 18px 50px rgba(0, 0, 0, 0.12);
}

.st-key-er-filter-card,
.st-key-er-metric-students,
.st-key-er-metric-score,
.st-key-er-metric-attendance,
.st-key-er-metric-risk,
.st-key-er-chart-scores,
.st-key-er-chart-risk,
.st-key-er-dataset,
.st-key-er-card {
  position: relative;
  padding: 20px 22px;
  border: 1px solid var(--er-border);
  border-radius: 14px;
  background: linear-gradient(145deg, rgba(25, 29, 40, 0.94), rgba(18, 21, 29, 0.94));
  box-shadow: 0 18px 50px rgba(0, 0, 0, 0.12);
}

.st-key-er-metric-students,
.st-key-er-metric-score,
.st-key-er-metric-attendance,
.st-key-er-metric-risk {
  padding: 19px 19px 17px;
  border-radius: 12px;
  overflow: hidden;
}

.section-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  margin: 38px 0 16px;
}

.section-heading.compact {
  align-items: center;
  margin: 0 0 18px;
}

.section-heading h3 {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  letter-spacing: -0.02em;
}

.section-heading .eyebrow {
  margin-bottom: 3px;
}

.section-note,
.dataset-heading p {
  margin: 0;
  color: var(--er-muted);
  font-size: 13px;
}

.dataset-heading {
  align-items: center;
  margin: 0 0 20px;
}

.dataset-heading p {
  margin-top: 5px;
}

/* -------------------------------------------------------------- filters */
.field-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 7px;
}

.field-header span {
  color: #b8bdcb;
  font-size: 12px;
}

.field-header .field-value {
  color: #aeb7ff;
  font-size: 12px;
  font-weight: 600;
}

.filter-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 15px;
  padding-top: 13px;
  border-top: 1px solid var(--er-border);
  color: var(--er-muted);
  font-size: 12px;
}

.filter-footer strong {
  color: #d9dce6;
  font-weight: 400;
}

.filter-chip {
  padding: 4px 8px;
  border: 1px solid rgba(114, 130, 255, 0.18);
  border-radius: 12px;
  background: var(--er-primary-soft);
  color: #aeb7ff;
}

/* select box */
[data-testid="stSelectbox"] div[role="group"] {
  min-height: 40px;
  border: 1px solid var(--er-border) !important;
  border-radius: 8px !important;
  background: #10131a !important;
}

[data-testid="stSelectbox"] div[role="group"]:hover {
  border-color: rgba(114, 130, 255, 0.5) !important;
}

[data-testid="stSelectbox"] input[role="combobox"] {
  color: #e8eaf1 !important;
  font-size: 13px !important;
}

[data-testid="stSelectbox"] svg {
  fill: rgba(238, 240, 246, 0.62);
}

/* dropdown list */
[role="listbox"] {
  padding: 6px;
  border: 1px solid var(--er-border) !important;
  border-radius: 10px !important;
  background: #1a1d27 !important;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.38) !important;
}

[role="option"] {
  border-radius: 6px;
  color: #c8ccda !important;
  font-size: 13px;
}

[role="option"][data-hovered],
[role="option"]:hover {
  background: rgba(255, 255, 255, 0.05) !important;
}

[role="option"][aria-selected="true"] {
  background: var(--er-primary-soft) !important;
  color: #aeb7ff !important;
}

/* slider: Streamlit paints an opaque block behind the track */
[data-testid="stSlider"] div[role="group"] > div {
  background: transparent !important;
}

[data-testid="stSlider"] div[role="group"] > div > div:first-child {
  height: 4px !important;
  border-radius: 4px !important;
  background-color: #303543 !important;
}

[data-testid="stSlider"] div[role="group"] > div > div:nth-child(2) {
  width: 14px !important;
  height: 14px !important;
  border: 3px solid #e7e9ff;
  border-radius: 50% !important;
  background: var(--er-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35);
}

[data-testid="stSliderTickBar"] {
  visibility: hidden;
  height: 0;
}

[data-testid="stSliderThumbValue"] {
  display: none;
}

/* checkbox */
[data-testid="stCheckbox"] label {
  align-items: center;
  gap: 8px;
  color: #aeb3c2;
  font-size: 12px;
  cursor: pointer;
}

[data-testid="stCheckbox"] label > div:not([data-testid]) {
  width: 16px !important;
  height: 16px !important;
  border: 1px solid rgba(224, 228, 241, 0.16) !important;
  border-radius: 4px !important;
  background: transparent !important;
}

[data-testid="stCheckbox"] input:checked + span + div:not([data-testid]),
[data-testid="stCheckbox"] input:checked ~ div:not([data-testid]) {
  border-color: var(--er-primary) !important;
  background: var(--er-primary) !important;
}

/* -------------------------------------------------------------- buttons */
[data-testid="stBaseButton-primary"] {
  border-radius: 8px;
  background: var(--er-primary);
  box-shadow: 0 8px 22px rgba(82, 98, 218, 0.2);
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  transition: transform 160ms ease, background 160ms ease;
}

[data-testid="stBaseButton-primary"]:hover {
  background: #8190ff;
  color: #fff;
  transform: translateY(-1px);
}

.st-key-er-reset button {
  padding: 7px 9px;
  border: 0;
  border-radius: 7px;
  background: transparent;
  box-shadow: none;
  color: #aeb7ff;
  font-size: 13px;
}

.st-key-er-reset button:hover:enabled {
  background: var(--er-primary-soft);
  color: #aeb7ff;
}

.st-key-er-reset button:disabled {
  background: transparent;
  color: #53596a;
}

.st-key-er-download button,
.st-key-er-check button {
  padding: 8px 11px;
  border: 1px solid var(--er-border);
  border-radius: 7px;
  background: #202431;
  box-shadow: none;
  color: #d7dae4;
  font-size: 12px;
}

.st-key-er-download button:hover,
.st-key-er-check button:hover {
  border-color: rgba(114, 130, 255, 0.4);
  background: #252a39;
}

.st-key-er-download button:disabled,
.st-key-er-check button:disabled {
  background: #171a24;
  color: #53596a;
}

/* menu popover */
[data-testid="stPopoverButton"] {
  width: 34px;
  min-height: 34px;
  padding: 0;
  border: 0;
  border-radius: 8px;
  background: transparent;
  box-shadow: none;
  color: #aeb3c2;
}

[data-testid="stPopoverButton"]:hover {
  background: var(--er-surface-raised);
}

[data-testid="stPopoverButton"] [data-testid="stMarkdownContainer"],
[data-testid="stPopoverButton"] > div > div[aria-hidden="true"] {
  display: none;
}

[data-testid="stPopoverBody"] {
  padding: 10px 12px;
  border: 1px solid var(--er-border);
  border-radius: 10px;
  background: #1a1d27;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.38);
}

/* -------------------------------------------------------------- metrics */
.st-key-er-metric-students,
.st-key-er-metric-score,
.st-key-er-metric-attendance,
.st-key-er-metric-risk {
  min-height: 148px;
}

.st-key-er-metric-students::before,
.st-key-er-metric-score::before,
.st-key-er-metric-attendance::before,
.st-key-er-metric-risk::before {
  position: absolute;
  inset: 0 auto 0 0;
  width: 3px;
  background: var(--er-metric-color, var(--er-primary));
  content: "";
}

.st-key-er-metric-students { --er-metric-color: #8593ff; }
.st-key-er-metric-score { --er-metric-color: #ac81f5; }
.st-key-er-metric-attendance { --er-metric-color: #48c995; }
.st-key-er-metric-risk { --er-metric-color: #f26370; }

[data-testid="stMetric"] {
  gap: 0;
}

[data-testid="stMetricLabel"] {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  color: #aeb3c2;
  font-size: 13px;
}

[data-testid="stMetricLabel"]::after {
  display: grid;
  width: 30px;
  height: 30px;
  place-items: center;
  border-radius: 8px;
  background: color-mix(in srgb, var(--er-metric-color) 13%, transparent);
  color: var(--er-metric-color);
  font-size: 9px;
  font-weight: 600;
  letter-spacing: 0.04em;
}

.st-key-er-metric-students [data-testid="stMetricLabel"]::after { content: "ST"; }
.st-key-er-metric-score [data-testid="stMetricLabel"]::after { content: "SC"; }
.st-key-er-metric-attendance [data-testid="stMetricLabel"]::after { content: "AT"; }
.st-key-er-metric-risk [data-testid="stMetricLabel"]::after { content: "HR"; }

[data-testid="stMetricValue"] {
  margin-top: 13px;
}

[data-testid="stMetricValue"] p,
[data-testid="stMetricValue"] div {
  font-size: 34px;
  font-weight: 600;
  letter-spacing: -0.035em;
  line-height: 38px;
}

[data-testid="stMetricDelta"] {
  display: none;
}

.er-metric-caption {
  display: block;
  margin-top: 5px;
  color: #747b8e;
  font-size: 12px;
}

/* --------------------------------------------------------------- charts */
.chart-panel {
  min-width: 0;
}

.chart-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.chart-heading h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.chart-heading p {
  margin: 3px 0 0;
  color: var(--er-muted);
  font-size: 12px;
}

.legend {
  position: relative;
  padding-left: 14px;
  color: var(--er-muted);
  font-size: 11px;
}

.legend::before {
  position: absolute;
  top: 5px;
  left: 0;
  width: 7px;
  height: 7px;
  border-radius: 2px;
  background: var(--er-amber);
  content: "";
}

.legend-score::before {
  background: #7d8dff;
}

.st-key-er-chart-scores,
.st-key-er-chart-risk {
  border-radius: 12px;
}

.st-key-er-chart-scores [data-testid="stVegaLiteChart"],
.st-key-er-chart-risk [data-testid="stVegaLiteChart"] {
  margin-top: 14px;
}

/* Streamlit paints an opaque background on the chart svg */
[data-testid="stVegaLiteChart"] svg {
  background: transparent !important;
}

/* --------------------------------------------------------------- tables */
.risk-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 600;
}

.risk-badge.low-risk {
  background: rgba(72, 201, 149, 0.12);
  color: #70dcaf;
}

.risk-badge.medium-risk {
  background: rgba(234, 182, 82, 0.12);
  color: #f0c66d;
}

.risk-badge.high-risk {
  background: rgba(242, 99, 112, 0.12);
  color: #f9848e;
}

.dataset-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* ------------------------------------------------------- forms + alerts */
[data-testid="stForm"] {
  padding: 20px 22px;
  border: 1px solid var(--er-border);
  border-radius: 14px;
  background: linear-gradient(145deg, rgba(25, 29, 40, 0.94), rgba(18, 21, 29, 0.94));
}

[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label {
  color: #b8bdcb;
  font-size: 12px;
}

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
  border: 1px solid var(--er-border);
  border-radius: 8px;
  background: #10131a;
  color: #e8eaf1;
  font-size: 13px;
}

[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
  border-color: rgba(114, 130, 255, 0.5);
}

[data-testid="stAlert"] {
  border: 1px solid var(--er-border);
  border-radius: 10px;
  background: var(--er-surface);
  color: var(--er-text);
  font-size: 13px;
}

/* Streamlit paints the alert body in its own status colour */
[data-testid="stAlertContainer"] {
  background: var(--er-surface-raised) !important;
  border-radius: 10px;
}

[data-testid="stAlertContentSuccess"] {
  color: #70dcaf;
}

[data-testid="stAlertContentInfo"] {
  color: #9aa4ff;
}

[data-testid="stAlertContentWarning"] {
  color: #f0c66d;
}

[data-testid="stAlertContentError"] {
  color: #f9848e;
}

[data-testid="stAlert"] strong,
[data-testid="stAlert"] b {
  font-weight: 600;
}

/* --------------------------------------------------------------- helper */
.er-text {
  margin: 0;
  color: var(--er-muted);
  font-size: 13px;
  line-height: 21px;
}

.er-list {
  margin: 0;
  padding-left: 18px;
  color: var(--er-muted);
  font-size: 14px;
  line-height: 26px;
}

.er-list strong {
  color: #d9dce6;
  font-weight: 600;
}

.er-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin: 0 8px 8px 0;
  padding: 5px 10px;
  border: 1px solid var(--er-border);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.02);
  color: #adb3c3;
  font-size: 12px;
}

/* --------------------------------------------------- collapsed sidebar */
/* Streamlit keeps the reopen control inside the header, so the header stays in
   the layout (invisible and click-through) and only that one button is turned
   back on - and only while the sidebar is actually collapsed. */
header[data-testid="stHeader"] {
  display: block !important;
  pointer-events: none;
  background: transparent;
}

[data-testid="stToolbar"] {
  display: flex !important;
  pointer-events: none;
  background: transparent;
}

[data-testid="stToolbar"] div:not(:has(button[data-testid="stExpandSidebarButton"])) {
  display: none !important;
}

[data-testid="stMainMenu"],
[data-testid="stMainMenuButton"],
[data-testid="stStatusWidget"],
[data-testid="stDecoration"],
[data-testid="stAppDeployButton"],
#MainMenu,
footer {
  display: none !important;
}

[data-testid="stAppViewContainer"]:has(section[data-testid="stSidebar"][aria-expanded="false"])
  button[data-testid="stExpandSidebarButton"] {
  display: flex !important;
  position: fixed;
  top: 12px;
  left: 12px;
  z-index: 1000001;
  width: 34px;
  min-width: 34px;
  height: 34px;
  padding: 0;
  border: 1px solid var(--er-border);
  border-radius: 9px;
  background: var(--er-surface-raised);
  color: var(--er-muted);
  pointer-events: auto;
}

/* keep the breadcrumb clear of the reopen button */
[data-testid="stAppViewContainer"]:has(section[data-testid="stSidebar"][aria-expanded="false"])
  [data-testid="stMainBlockContainer"] {
  padding-left: 60px;
}

/* --------------------------------------------------------- breakpoints */
/* The sidebar keeps its fixed width at every size: Streamlit slides it off
   canvas when the viewport is narrow, and forcing a percentage width here
   would turn it into a full screen overlay. */
@media (max-width: 820px) {
  [data-testid="stMainBlockContainer"] {
    padding: 0 18px 60px;
  }

  .intro h2 {
    font-size: 32px;
  }

  [data-testid="stSidebarUserContent"] div:has(> .st-key-er-sidebar-status) {
    margin-top: 0;
  }

  /* the sidebar overlays the page when expanded on a small screen */
  section[data-testid="stSidebar"] {
    box-shadow: 24px 0 48px rgba(0, 0, 0, 0.45);
  }

  [data-testid="stSidebarCollapseButton"] {
    visibility: visible !important;
  }
}

@media (max-width: 620px) {
  .intro {
    display: block;
  }

  .topbar-context {
    display: none;
  }
}
"""


def inject_theme():
    """Load the EduRisk stylesheet into the running Streamlit app."""
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)