import unittest
import numpy as np
import pandas as pd
import datetime
import main_engine as engine

class TestSisonkeProcessEngine(unittest.TestCase):

    def setUp(self):
        """
        Set up a miniature, process-symmetrical dataset 
        to test mathematical execution flow.
        """
        self.test_ts = pd.to_datetime("2026-07-22 12:00:00")
        self.sample_data = pd.DataFrame({
            "league_country": ["scotland", "scotland"],
            "match_timestamp": [pd.to_datetime("2026-07-10"), pd.to_datetime("2026-07-15")],
            "home_team": ["Celtic", "Rangers"],
            "away_team": ["Rangers", "Celtic"],
            "home_goals": [3.0, 1.0],
            "away_goals": [1.0, 2.0],
            "home_sot":, "away_sot":,
            "home_big_chances":, "away_big_chances":,
            "home_box_touches":, "away_box_touches":,
            "home_through_passes":, "away_through_passes":,
            "home_final_third_entries":, "away_final_third_entries":,
            "home_interceptions":, "away_interceptions":,
            "home_recoveries":, "away_recoveries":,
            "home_saves":, "away_saves":,
            "home_ground_duels_won_pct": [0.54, 0.45], "away_ground_duels_won_pct": [0.46, 0.52],
            "home_aerial_duels_won_pct": [0.58, 0.44], "away_aerial_duels_won_pct": [0.42, 0.54],
            "home_tackles_won_pct": [0.72, 0.60], "away_tackles_won_pct": [0.64, 0.65],
            "home_passes_final_third_pct": [0.82, 0.72], "away_passes_final_third_pct": [0.74, 0.76],
            "home_rest_days":, "away_rest_days": [6, 7]
        })

    def test_probability_matrix_normalization(self):
        """VERIFICATION 1: Ensure total matrix probability sums up exactly to 1.0 (100%)"""
        prediction = engine.predict_match_probabilities(
            historical_matches=self.sample_data,
            home_team="Celtic", away_team="Rangers",
            current_timestamp=self.test_ts,
            baseline_goals=2.65, home_rest_days=5, away_rest_days=5
        )
        matrix_sum = np.sum(prediction["raw_matrix"])
        self.assertAlmostEqual(matrix_sum, 1.0, places=4, msg="Poisson matrix failed normalization boundary bounds!")

    def test_rest_days_minimum_floor(self):
        """VERIFICATION 2: Test if severe negative rest days safely apply the 0.88 penalty floor"""
        extreme_penalty = engine.calculate_rest_multiplier(-10)
        self.assertEqual(extreme_penalty, 0.88, "Rest day handler failed to clamp anomalous negative entries.")

    def test_division_by_zero_fallback(self):
        """VERIFICATION 3: Test that empty team data sets safely switch to fallbacks without throwing errors"""
        empty_pool = pd.DataFrame(columns=self.sample_data.columns)
        fallback_stats = engine.parse_live_team_averages(
            df=empty_pool, team="Unknown Team", current_ts=self.test_ts, status_override="stable"
        )
        self.assertEqual(fallback_stats["games_played"], 0, "Fallback tracker failed to catch empty pool index.")
        self.assertEqual(fallback_stats["att_strength_goals"], 1.0, "Attacking index did not safely regress to default.")

    def test_time_decay_freeze(self):
        """VERIFICATION 4: Check if off-season freeze toggle locks time weight strictly at 1.0"""
        frozen_weight = engine.calculate_time_decay_weight(days_ago=365, half_life_days=45, freeze_decay=True)
        self.assertEqual(frozen_weight, 1.0, "Time-decay freeze toggle failed to hold weight constant at 1.0.")

if __name__ == "__main__":
    unittest.main()
