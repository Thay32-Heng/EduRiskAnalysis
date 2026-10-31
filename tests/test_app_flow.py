"""End-to-end tests for the Lab 04 Risk Checker flow.

``test_logic.py`` covers the plain functions. These tests drive the real app
with Streamlit's ``AppTest``, because the things Lab 04 is graded on only exist
as a *flow*: a form submit, a rejected empty name, the session-state history and
a Clear History click that must empty the table in one go.

No browser is needed - ``AppTest`` runs ``app.py`` headlessly, the same way the
tests import it, but with widget clicks.

Run from the repository root:

    python -m unittest discover -s tests -t . -v
"""

import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).resolve().parent.parent / "app.py")

# The exact sentences the lab expects each alert to carry.
LOW_RISK_MESSAGE = "Risk Level: Low Risk"
MEDIUM_RISK_MESSAGE = "Risk Level: Medium Risk"
HIGH_RISK_MESSAGE = "Risk Level: High Risk"


def start_app():
    """Open the app at its Home page."""
    app = AppTest.from_file(APP_PATH, default_timeout=30)
    app.run()
    return app


def open_risk_checker():
    """Open the app and click through to the Risk Checker page."""
    app = start_app()
    app.button(key="er-nav-risk-checker").click().run()
    return app


def submit(app, name, score, attendance):
    """Fill the form and click Check risk, the way a student would."""
    app.text_input(key="er-check-name").set_value(name)
    app.number_input(key="er-check-score").set_value(score)
    app.number_input(key="er-check-attendance").set_value(attendance)
    app.button(key="er-submit").click().run()
    return app


class AppBootTests(unittest.TestCase):
    def test_app_starts_without_an_exception(self):
        app = start_app()
        self.assertFalse(app.exception, app.exception)

    def test_home_page_confirms_that_lab_04_is_running(self):
        app = start_app()
        self.assertTrue(
            any("running successfully" in message.value for message in app.success)
        )


class FormValidationTests(unittest.TestCase):
    """Step 21-22: a submitted form with no name is stopped before the rule."""

    def test_empty_name_shows_the_warning_and_stores_nothing(self):
        app = submit(open_risk_checker(), "", 90, 95)
        self.assertFalse(app.exception, app.exception)

        warnings = [message.value for message in app.warning]
        self.assertIn("Please enter the student name.", warnings)
        self.assertEqual(app.session_state["risk_history"], [])

    def test_whitespace_only_name_is_rejected_too(self):
        app = submit(open_risk_checker(), "   ", 90, 95)
        warnings = [message.value for message in app.warning]
        self.assertIn("Please enter the student name.", warnings)
        self.assertEqual(app.session_state["risk_history"], [])

    def test_a_rejected_submit_does_not_leave_the_last_result_on_screen(self):
        app = open_risk_checker()
        submit(app, "Student A", 90, 95)
        submit(app, "", 90, 95)

        successes = [message.value for message in app.success]
        self.assertFalse(
            any(LOW_RISK_MESSAGE in message for message in successes), successes
        )


class HistoryTests(unittest.TestCase):
    """Steps 23-28: one submit adds exactly one row, and the table shows it."""

    def test_one_submit_appends_exactly_one_trimmed_row(self):
        app = submit(open_risk_checker(), "  Student A  ", 90, 95)
        self.assertFalse(app.exception, app.exception)

        self.assertEqual(
            app.session_state["risk_history"],
            [
                {
                    "Student Name": "Student A",
                    "Score": 90,
                    "Attendance": 95,
                    "Risk Level": "Low Risk",
                }
            ],
        )

    def test_each_submit_adds_one_row_and_never_more(self):
        app = open_risk_checker()
        submit(app, "Student A", 90, 95)
        app.button(key="er-submit").click().run()
        app.button(key="er-submit").click().run()

        self.assertEqual(len(app.session_state["risk_history"]), 3)

    def test_history_keeps_the_submission_order(self):
        app = open_risk_checker()
        submit(app, "Student A", 90, 95)
        submit(app, "Student B", 70, 80)

        names = [row["Student Name"] for row in app.session_state["risk_history"]]
        self.assertEqual(names, ["Student A", "Student B"])

    def test_history_table_is_drawn_from_the_history_list(self):
        app = open_risk_checker()
        submit(app, "Student A", 90, 95)
        submit(app, "Student B", 70, 80)
        self.assertFalse(app.exception, app.exception)

        # The table must be the two submitted rows, not the eight-row cohort
        # table: same widget, very different meaning.
        rendered = app.dataframe[0].value
        self.assertEqual(
            list(rendered.columns),
            ["Student Name", "Score", "Attendance", "Risk Level"],
        )
        self.assertEqual(
            list(rendered["Student Name"]), ["Student A", "Student B"]
        )

    def test_history_starts_empty_with_a_placeholder(self):
        app = open_risk_checker()
        self.assertEqual(app.session_state["risk_history"], [])
        self.assertTrue(
            any("No risk checks yet." in message.value for message in app.info)
        )


class FeedbackTests(unittest.TestCase):
    """Step 25: the alert style follows the risk level."""

    def test_low_risk_is_a_success_message(self):
        app = submit(open_risk_checker(), "Student A", 90, 95)
        messages = [message.value for message in app.success]
        self.assertTrue(any("Student appears on track." in m for m in messages))
        self.assertTrue(any(LOW_RISK_MESSAGE in m for m in messages))

    def test_medium_risk_is_a_warning(self):
        app = submit(open_risk_checker(), "Student B", 70, 80)
        messages = [message.value for message in app.warning]
        self.assertTrue(any(MEDIUM_RISK_MESSAGE in m for m in messages))

    def test_high_risk_is_an_error(self):
        app = submit(open_risk_checker(), "Student C", 50, 85)
        messages = [message.value for message in app.error]
        self.assertTrue(any(HIGH_RISK_MESSAGE in m for m in messages))

    def test_low_attendance_alone_is_high_risk(self):
        app = submit(open_risk_checker(), "Student D", 80, 55)
        messages = [message.value for message in app.error]
        self.assertTrue(any(HIGH_RISK_MESSAGE in m for m in messages))


class ClearHistoryTests(unittest.TestCase):
    """Steps 29: one click empties the table and confirms it."""

    def test_clear_history_empties_the_table_in_one_click(self):
        app = submit(open_risk_checker(), "Student A", 90, 95)
        app.button(key="er-clear").click().run()
        self.assertFalse(app.exception, app.exception)

        self.assertEqual(app.session_state["risk_history"], [])
        self.assertTrue(
            any("No risk checks yet." in message.value for message in app.info)
        )

    def test_clear_history_confirms_itself_once(self):
        app = submit(open_risk_checker(), "Student A", 90, 95)
        app.button(key="er-clear").click().run()

        self.assertTrue(
            any(
                "Risk check history cleared." in message.value
                for message in app.success
            )
        )

        # A later rerun must not repeat the confirmation.
        app.run()
        self.assertFalse(
            any(
                "Risk check history cleared." in message.value
                for message in app.success
            )
        )

    def test_clear_history_also_drops_the_last_result(self):
        app = submit(open_risk_checker(), "Student A", 90, 95)
        app.button(key="er-clear").click().run()

        self.assertIsNone(app.session_state["risk_result"])
        self.assertFalse(
            any(LOW_RISK_MESSAGE in message.value for message in app.success)
        )


class PageRoutingTests(unittest.TestCase):
    """Every page in the sidebar still renders after the Lab 04 changes."""

    def test_every_page_renders_without_an_exception(self):
        app = start_app()
        for key in (
            "er-nav-dashboard",
            "er-nav-student-data",
            "er-nav-risk-checker",
            "er-nav-about",
            "er-nav-home",
        ):
            app.button(key=key).click().run()
            self.assertFalse(app.exception, (key, app.exception))

    def test_the_dashboard_matches_the_lab_expected_table(self):
        """Pins the numbers the notebook lists for the shipped sample cohort."""
        app = start_app()
        app.button(key="er-nav-dashboard").click().run()

        values = {metric.label: metric.value for metric in app.metric}
        self.assertEqual(values["Students"], "8")
        self.assertEqual(values["Average score"], "71.62")
        self.assertEqual(values["Attendance"], "79.0%")
        self.assertEqual(values["High risk"], "2")

    def test_the_dashboard_carries_an_ethics_reminder(self):
        app = start_app()
        app.button(key="er-nav-dashboard").click().run()

        self.assertTrue(
            any("Ethics Reminder" in message.value for message in app.info)
        )


if __name__ == "__main__":
    unittest.main()
