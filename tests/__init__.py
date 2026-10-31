"""Test package for EduRisk Analytics.

Importing this package silences the two *log* warnings Streamlit prints when
``app.py`` runs outside a real server - which is exactly what the suites do: the
unit tests import the file, and ``test_app_flow`` drives it with ``AppTest``.

* "Thread 'MainThread': missing ScriptRunContext!"
* "Session state does not function when running a script without `streamlit run`"

A level change is not enough: Streamlit calls ``get_logger()`` again on every app
run and resets the logger's level. A filter on the logger survives.

One piece of noise is out of reach here: Streamlit's "to view this app on a
browser, run it with..." banner, which it logs to the root logger and is not
worth changing a global option for.

Run from the repository root:

    python -m unittest discover -s tests -t . -v
"""

import logging

# The loggers that carry the two bare-mode warnings.
NOISY_LOGGERS = (
    "streamlit.runtime.scriptrunner_utils.script_run_context",
    "streamlit.runtime.state.session_state_proxy",
)

# The warning texts, without their formatting (line breaks are added at log time).
BARE_MODE_WARNINGS = ("missing ScriptRunContext", "Session state does not function")


def _hide_bare_mode_warnings(record):
    """Keep every record except the two warnings above."""
    message = record.getMessage()
    return not any(warning in message for warning in BARE_MODE_WARNINGS)


for _name in NOISY_LOGGERS:
    logging.getLogger(_name).addFilter(_hide_bare_mode_warnings)
