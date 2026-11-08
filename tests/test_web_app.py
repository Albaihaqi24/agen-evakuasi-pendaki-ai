from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest


WEB_APP = str(Path(__file__).resolve().parents[1] / "web_app.py")


class WebDashboardTests(unittest.TestCase):
    def test_extreme_dashboard_shows_expected_costs(self):
        app = AppTest.from_file(WEB_APP, default_timeout=30).run()

        self.assertEqual(len(app.exception), 0)
        self.assertEqual([metric.value for metric in app.metric], ["12", "16"])
        self.assertEqual(
            [button.label for button in app.get("download_button")],
            ["Unduh hasil JSON"],
        )

    def test_manual_closures_report_no_available_route(self):
        app = AppTest.from_file(WEB_APP, default_timeout=30).run()
        app.multiselect[0].set_value(["S ↔ A", "S ↔ E", "S ↔ C"]).run()

        self.assertEqual(len(app.exception), 0)
        self.assertIn(
            "Tidak tersedia rute untuk A* maupun BFS pada konfigurasi ini.",
            [warning.value for warning in app.warning],
        )


if __name__ == "__main__":
    unittest.main()
