"""Unit tests for the pure logic in app.py.

The dashboard itself is a UI layer; everything worth testing lives in plain
functions: the risk rule, the cohort filters, the metric helpers, and the Lab 04
form logic (name validation, the history record and the feedback messages).
The form-to-table flow itself is covered in test_app_flow.py.

Run from the repository root:

    python -m unittest discover -s tests -t . -v
"""

import unittest

import pandas as pd

# The tests package silences Streamlit's "missing ScriptRunContext" warning when
# it is imported, which happens before this module.
import app  # noqa: E402  (imported by path from the repository root)


def make_rows():
    """A small fixture with the same columns as students.csv, plus a blank score."""
    return pd.DataFrame(
        {
            "Student Name": ["Dara", "Vuthy", "Malis", "Rithy"],
            "Course": ["Python", "Python", "Statistics", "Database"],
            "Score": [90.0, 55.0, 80.0, float("nan")],
            "Attendance": [95.0, 50.0, 70.0, 88.0],
            "Study Hours": [12, 3, 15, 5],
        }
    )


def with_risk_level(rows):
    rows = rows.copy()
    rows["Risk Level"] = [
        app.classify_risk(score, attendance)
        for score, attendance in zip(rows["Score"], rows["Attendance"])
    ]
    return rows


class ClassifyRiskTests(unittest.TestCase):
    """The two-threshold rule: 60 for high risk, 75 for medium."""

    def test_below_sixty_on_either_measure_is_high_risk(self):
        self.assertEqual(app.classify_risk(59.9, 90), app.HIGH_RISK)
        self.assertEqual(app.classify_risk(90, 59.9), app.HIGH_RISK)

    def test_sixty_is_not_high_risk(self):
        self.assertEqual(app.classify_risk(60, 90), app.MEDIUM_RISK)
        self.assertEqual(app.classify_risk(90, 60), app.MEDIUM_RISK)

    def test_between_sixty_and_seventy_five_is_medium_risk(self):
        self.assertEqual(app.classify_risk(74.9, 90), app.MEDIUM_RISK)
        self.assertEqual(app.classify_risk(90, 74.9), app.MEDIUM_RISK)

    def test_seventy_five_and_above_is_low_risk(self):
        self.assertEqual(app.classify_risk(75, 75), app.LOW_RISK)
        self.assertEqual(app.classify_risk(100, 100), app.LOW_RISK)

    def test_missing_values_are_never_low_risk(self):
        self.assertEqual(app.classify_risk(float("nan"), 88), app.HIGH_RISK)
        self.assertEqual(app.classify_risk(88, float("nan")), app.HIGH_RISK)


class ApplyFiltersTests(unittest.TestCase):
    """Filters narrow the cohort; 'All' / 0 means 'do not filter'."""

    def setUp(self):
        self.rows = with_risk_level(make_rows())

    def test_course_filter(self):
        view = app.apply_filters(self.rows, "Python", app.ALL, 0, 0)
        self.assertEqual(len(view), 2)
        self.assertEqual(set(view["Course"]), {"Python"})

    def test_risk_filter(self):
        view = app.apply_filters(self.rows, app.ALL, app.HIGH_RISK, 0, 0)
        self.assertEqual(len(view), 2)  # Vuthy and the blank-score row

    def test_minimum_attendance_filter(self):
        view = app.apply_filters(self.rows, app.ALL, app.ALL, 90, 0)
        self.assertEqual(len(view), 1)

    def test_filters_combine(self):
        view = app.apply_filters(self.rows, "Python", app.ALL, 0, 50)
        self.assertEqual(len(view), 2)

    def test_no_filters_returns_everything(self):
        view = app.apply_filters(self.rows, app.ALL, app.ALL, 0, 0)
        self.assertEqual(len(view), len(self.rows))

    def test_missing_measure_is_not_dropped_at_zero(self):
        view = app.apply_filters(self.rows, app.ALL, app.ALL, 0, 0)
        self.assertTrue(pd.isna(view["Score"]).any())

    def test_empty_input_stays_empty(self):
        empty = self.rows.iloc[0:0]
        view = app.apply_filters(empty, "Python", app.HIGH_RISK, 50, 50)
        self.assertTrue(view.empty)

    def test_result_is_a_copy_not_a_view(self):
        view = app.apply_filters(self.rows, app.ALL, app.ALL, 0, 0)
        self.assertIsNot(view, self.rows)
        view.loc[view.index[0], "Score"] = -1
        self.assertNotEqual(self.rows.loc[view.index[0], "Score"], -1)


class CountActiveFiltersTests(unittest.TestCase):
    def test_nothing_active(self):
        self.assertEqual(app.count_active_filters(app.ALL, app.ALL, 0, 0), 0)

    def test_everything_active(self):
        self.assertEqual(
            app.count_active_filters("Python", app.HIGH_RISK, 60, 50), 4
        )

    def test_partial(self):
        self.assertEqual(app.count_active_filters(app.ALL, app.LOW_RISK, 0, 70), 2)


class MetricHelperTests(unittest.TestCase):
    def test_average_of_missing_column_is_zero(self):
        self.assertEqual(app.average_of(app.df, "Not A Column"), 0.0)

    def test_average_of_empty_frame_is_zero(self):
        self.assertEqual(app.average_of(app.df.iloc[0:0], "Score"), 0.0)

    def test_average_ignores_missing_values(self):
        self.assertEqual(app.average_of(make_rows(), "Score"), 75.0)

    def test_count_risk(self):
        self.assertEqual(app.count_risk(app.df, app.HIGH_RISK), 2)

    def test_count_risk_on_empty_frame(self):
        self.assertEqual(app.count_risk(app.df.iloc[0:0], app.HIGH_RISK), 0)

    def test_percent_of_rounds_half_up(self):
        self.assertEqual(app.percent_of(1, 8), 13)  # not 12, not 12.5
        self.assertEqual(app.percent_of(2, 8), 25)

    def test_percent_of_zero_whole_is_zero(self):
        self.assertEqual(app.percent_of(0, 0), 0)


class StudentNameValidationTests(unittest.TestCase):
    """Lab 04 validation: a name of only spaces is not a name."""

    def test_empty_name_is_invalid(self):
        self.assertFalse(app.is_valid_student_name(""))

    def test_whitespace_only_name_is_invalid(self):
        self.assertFalse(app.is_valid_student_name("   "))
        self.assertFalse(app.is_valid_student_name("\t\n"))

    def test_real_name_is_valid(self):
        self.assertTrue(app.is_valid_student_name("Dara"))

    def test_name_is_trimmed(self):
        self.assertEqual(app.clean_student_name("  Student A  "), "Student A")

    def test_missing_name_becomes_an_empty_string(self):
        self.assertEqual(app.clean_student_name(None), "")
        self.assertFalse(app.is_valid_student_name(None))

    def test_nan_name_is_not_treated_as_a_real_name(self):
        # str(float("nan")) is the word "nan", which would pass a bare strip().
        self.assertEqual(app.clean_student_name(float("nan")), "")
        self.assertFalse(app.is_valid_student_name(float("nan")))
        self.assertFalse(app.is_valid_student_name(pd.NA))


class RiskRecordTests(unittest.TestCase):
    """The dictionary one form submission adds to the session history."""

    def test_record_has_the_four_lab_columns_in_order(self):
        record = app.build_risk_record("Student A", 90, 95)
        self.assertEqual(
            list(record), ["Student Name", "Score", "Attendance", "Risk Level"]
        )

    def test_record_trims_the_name(self):
        record = app.build_risk_record("  Student A  ", 90, 95)
        self.assertEqual(record["Student Name"], "Student A")

    def test_record_uses_the_risk_rule(self):
        self.assertEqual(
            app.build_risk_record("A", 90, 95)["Risk Level"], app.LOW_RISK
        )
        self.assertEqual(
            app.build_risk_record("B", 70, 80)["Risk Level"], app.MEDIUM_RISK
        )
        self.assertEqual(
            app.build_risk_record("C", 50, 85)["Risk Level"], app.HIGH_RISK
        )

    def test_low_attendance_alone_can_be_high_risk(self):
        record = app.build_risk_record("D", 80, 55)
        self.assertEqual(record["Risk Level"], app.HIGH_RISK)

    def test_empty_history_frame_still_has_columns(self):
        frame = app.history_frame([])
        self.assertTrue(frame.empty)
        self.assertEqual(
            list(frame.columns), ["Student Name", "Score", "Attendance", "Risk Level"]
        )

    def test_history_frame_keeps_submission_order(self):
        history = [
            app.build_risk_record("Student A", 90, 95),
            app.build_risk_record("Student B", 70, 80),
        ]
        frame = app.history_frame(history)
        self.assertEqual(len(frame), 2)
        self.assertEqual(list(frame["Student Name"]), ["Student A", "Student B"])


class RiskFeedbackTests(unittest.TestCase):
    """Step 25: each level gets its own alert style and supportive sentence."""

    def test_low_risk_is_a_success_message(self):
        kind, headline, advice = app.risk_feedback(app.LOW_RISK)
        self.assertEqual(kind, "success")
        self.assertIn("Low Risk", headline)
        self.assertEqual(advice, "Student appears on track.")

    def test_medium_risk_is_a_warning(self):
        kind, headline, advice = app.risk_feedback(app.MEDIUM_RISK)
        self.assertEqual(kind, "warning")
        self.assertIn("Medium Risk", headline)
        self.assertEqual(advice, "Monitor progress and provide guidance.")

    def test_high_risk_is_an_error(self):
        kind, headline, advice = app.risk_feedback(app.HIGH_RISK)
        self.assertEqual(kind, "error")
        self.assertIn("High Risk", headline)
        self.assertEqual(advice, "Student may need additional support.")

    def test_every_risk_level_has_feedback(self):
        for level in app.RISK_LEVELS:
            kind, headline, advice = app.risk_feedback(level)
            self.assertIn(kind, ("success", "warning", "error"))
            self.assertTrue(headline and advice)


class NiceTicksTests(unittest.TestCase):
    def test_non_positive_axis_gets_a_default(self):
        self.assertEqual(app.nice_ticks(0), [0, 1])
        self.assertEqual(app.nice_ticks(-3), [0, 1])

    def test_small_axis_counts_by_one(self):
        self.assertEqual(app.nice_ticks(5), [0, 1, 2, 3, 4, 5])

    def test_step_is_rounded_up(self):
        self.assertEqual(app.nice_ticks(8), [0, 2, 4, 6, 8])

    def test_axis_reaches_the_maximum(self):
        ticks = app.nice_ticks(12)
        self.assertGreaterEqual(ticks[-1], 12)
        self.assertEqual(ticks[0], 0)


class DatasetTests(unittest.TestCase):
    """Guards the CSV contract the dashboard depends on."""

    def test_expected_columns(self):
        self.assertEqual(
            list(app.df.columns),
            [
                "Student Name",
                "Course",
                "Score",
                "Attendance",
                "Study Hours",
                "Risk Level",
            ],
        )

    def test_every_student_has_a_risk_level(self):
        self.assertTrue(app.df["Risk Level"].isin(app.RISK_LEVELS).all())

    def test_scores_are_in_range(self):
        for column in ("Score", "Attendance"):
            self.assertTrue(app.df[column].between(0, 100).all())


if __name__ == "__main__":
    unittest.main()
