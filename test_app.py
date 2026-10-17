"""Smoke tests for the EduRisk Analytics dashboard.

These are Streamlit ``AppTest`` checks: instead of importing ``app.py`` (which
would run the whole page script), AppTest *runs* the app in bare mode and lets
the test poke the widgets and read the results back. That is the only way to
test a Streamlit script.

Run them either way::

    python test_app.py          # no pytest needed, prints one line per test
    pytest test_app.py          # if pytest is installed

Every check is written against the numbers in ``load_students()`` in app.py, so
if the placeholder dataset is ever replaced these need updating too.
"""

import json
import logging

from streamlit.testing.v1 import AppTest

# AppTest runs the script in bare mode, so Streamlit prints one
# ScriptRunContext warning per run. That is the test harness, not a fault in
# the app, and Streamlit installs its own handler, so a level alone is not
# enough - the record has to be filtered out.
_BARE_MODE = logging.getLogger("streamlit.runtime.scriptrunner_utils.script_run_context")
_BARE_MODE.addFilter(lambda record: False)

APP_FILE = "app.py"
TIMEOUT = 60
PAGES = ["Home", "Dashboard", "Student Data", "Risk Checker", "About"]

# The middle dot the risk chart labels use: "3 - 38%".
DOT = "\u00b7"


def open_page(page):
    """Return a finished AppTest sitting on ``page``."""
    at = AppTest.from_file(APP_FILE, default_timeout=TIMEOUT).run()
    at.session_state["page"] = page
    at.run()
    return at


def open_dashboard():
    """Return a finished AppTest on the Dashboard, with no filters applied."""
    return open_page("Dashboard")


def metric(app, label):
    """The value of one metric card, found by its label."""
    for card in app.metric:
        if card.label == label:
            return card.value
    raise AssertionError(f"no metric card labelled {label!r}")


def chart_spec(app, index):
    """The Vega-Lite spec Streamlit was handed for one of the dashboard charts.

    AppTest leaves the chart element's ``value`` as None, but the raw protobuf
    keeps the spec, which is the only way to inspect what Vega-Lite will draw.
    """
    charts = app.get("vega_lite_chart")
    assert len(charts) > index, f"expected more than {index} charts, found {len(charts)}"
    return json.loads(charts[index].proto.spec)


def risk_chart_rows(app):
    """The three rows the risk chart draws: level, count, share and label."""
    return chart_spec(app, 1)["layer"][0]["data"]["values"]


def test_every_page_renders():
    """All five screens build without raising."""
    at = AppTest.from_file(APP_FILE, default_timeout=TIMEOUT).run()

    for page in PAGES:
        at.session_state["page"] = page
        at.run()
        assert not at.exception, f"{page} raised: {at.exception}"


def test_course_filter_narrows_the_cohort():
    """Choosing a course keeps only that course's students."""
    at = open_dashboard()
    assert metric(at, "Students") == "8"

    at.selectbox(key="er-filter-course").set_value("Python").run()

    assert not at.exception
    assert metric(at, "Students") == "3"  # Dara, Vuthy, Chan
    assert metric(at, "High risk") == "1"  # only Vuthy (45 / 50)


def test_minimum_score_filter_narrows_the_cohort():
    """The score slider drops everyone below the chosen score."""
    at = open_dashboard()

    at.slider(key="er-filter-score").set_value(90).run()

    assert not at.exception
    assert metric(at, "Students") == "2"  # Malis 92, Sreyneang 91
    assert metric(at, "High risk") == "0"


def test_filters_that_match_nobody_show_the_empty_state():
    """An impossible filter combination empties the view instead of crashing."""
    at = open_dashboard()

    at.selectbox(key="er-filter-course").set_value("Web App").run()
    at.slider(key="er-filter-score").set_value(100).run()

    assert not at.exception
    assert metric(at, "Students") == "0"
    # Both charts stand down and the empty-state note takes their place.
    assert len(at.get("vega_lite_chart")) == 0


def test_risk_rule_boundaries():
    """The 60 / 75 rule classifies all eight students correctly.

    Rithy sits right on the boundary: attendance 60 is not *below* 60, but a
    score of 58 is, so the student is High Risk. Sophea's attendance of 75 is
    not below 75 either, so only the score of 68 decides, giving Medium.
    """
    at = open_dashboard()
    assert metric(at, "High risk") == "2"  # Vuthy (45/50), Rithy (58/60)

    for level, expected in [("Low Risk", "3"), ("Medium Risk", "3"), ("High Risk", "2")]:
        one = open_dashboard()
        one.selectbox(key="er-filter-risk").set_value(level).run()
        assert not one.exception
        assert metric(one, "Students") == expected, f"{level} count"

    # The chart reads calmest first, and labels every bar with count and share.
    rows = risk_chart_rows(at)
    assert [row["Risk Level"] for row in rows] == [
        "Low Risk",
        "Medium Risk",
        "High Risk",
    ]
    assert [row["Label"] for row in rows] == [
        f"3 {DOT} 38%",
        f"3 {DOT} 38%",
        f"2 {DOT} 25%",
    ]


def test_risk_checker_form_wiring():
    """The form only calculates a result once the button is clicked."""
    at = open_page("Risk Checker")
    assert "risk_result" not in at.session_state

    at.text_input(key="er-check-name").set_value("Thay")
    at.number_input(key="er-check-score").set_value(59)
    at.number_input(key="er-check-attendance").set_value(95)
    at.button(key="er-submit").click().run()

    assert not at.exception
    # 59 is one point under the high-risk cut-off, however good the attendance.
    # The banner itself is st.html, which AppTest cannot read back, so the rule
    # it applies is covered by test_risk_rule_boundaries instead.
    assert at.session_state["risk_result"] == ("Thay", 59, 95)


def test_both_charts_keep_their_axes():
    """No layer may set ``axis=None``, because that deletes the whole chart's axes.

    Vega-Lite merges the axis into one component shared by every layer of a
    layered chart. So ``axis=None`` on an overlay layer does not hide that
    layer's axis - it makes the merge give up and the chart renders with no
    category names, no numbers and no gridlines.
    """
    at = open_dashboard()
    charts = at.get("vega_lite_chart")
    assert len(charts) == 2

    for index, chart in enumerate(charts):
        spec = json.loads(chart.proto.spec)
        for number, layer in enumerate(spec["layer"]):
            for field, encoding in layer.get("encoding", {}).items():
                # tooltip is a list of entries; only channels carry an axis.
                if not isinstance(encoding, dict):
                    continue
                assert encoding.get("axis", "kept") is not None, (
                    f"chart {index}, layer {number} sets axis=None on {field} - "
                    "that deletes this chart's axes entirely"
                )

        base = spec["layer"][0].get("encoding", {})
        assert base["x"].get("axis"), f"chart {index} lost its x axis"
        assert base["y"].get("axis"), f"chart {index} lost its y axis"


def test_score_histogram_keeps_the_full_out_of_100_scale():
    """The histogram is pinned to 0-100 and carries both risk thresholds.

    Without the pinned scale the x domain follows the filtered data, so Vega
    throws away the axis ticks outside it and the 60/75 rules slide away from
    the scores they are meant to annotate.
    """
    at = open_dashboard()
    spec = json.loads(at.get("vega_lite_chart")[0].proto.spec)

    x = spec["layer"][0]["encoding"]["x"]
    assert x["bin"] == {"step": 5}
    assert x.get("scale", {}).get("domain") == [0, 100], (
        "the score axis is not pinned to 0-100, so the ticks and the 60/75 "
        "rules follow whatever the filters cover"
    )
    assert x["axis"]["values"] == [0, 20, 40, 60, 80, 100]

    # The overlay layer is the pair of dashed rules at the two risk cut-offs.
    rules = spec["layer"][1]
    assert rules["mark"]["type"] == "rule"
    assert rules["encoding"]["x"].get("scale", {}).get("domain") == [0, 100]
    assert rules["data"]["values"] == [
        {"Score": 60, "Threshold": "High"},
        {"Score": 75, "Threshold": "Medium"},
    ]


def main():
    """Run every test_* function here and report, so pytest stays optional."""
    tests = [
        (name, func)
        for name, func in sorted(globals().items())
        if name.startswith("test_") and callable(func)
    ]

    passed = 0
    for name, func in tests:
        try:
            func()
        except Exception as exc:  # noqa: BLE001 - a test runner reports anything
            print(f"FAIL  {name}: {exc}")
        else:
            passed += 1
            print(f"ok    {name}")

    print(f"\n{passed}/{len(tests)} passed")
    return 0 if passed == len(tests) else 1


if __name__ == "__main__":
    raise SystemExit(main())