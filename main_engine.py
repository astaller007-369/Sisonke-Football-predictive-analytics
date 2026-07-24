import os
import sys
import json
import math
import numpy as np
import pandas as pd

# --- COMPREHENSIVE MULTI-TIER LEAGUE BASELINE GOALS MATRIX ---
COMPETITION_MATRIX = {
    "uefa champions league": {
        "tier_1": "Champions League", "baseline_goals": 2.98,
        "cups": ["Group Stage", "Play-Offs"]
    },
    "south africa": {
        "tier_1": "Betway Premiership", "baseline_goals": 2.02, 
        "cups": ["Nedbank Cup", "MTN8", "Carling Knockout"]
    },
    "england": {
        "tier_1": "Premier League", "baseline_goals": 2.84, 
        "tier_2": "Championship", "tier_2_baseline_goals": 2.68, 
        "cups": ["FA Cup", "EFL Cup"]
    },
    "spain": {
        "tier_1": "La Liga", "baseline_goals": 2.55, 
        "tier_2": "Segunda División", "tier_2_baseline_goals": 2.42, 
        "cups": ["Copa del Rey", "Supercopa de España"]
    },
    "france": {
        "tier_1": "Ligue 1", "baseline_goals": 2.60, 
        "tier_2": "Ligue 2", "tier_2_baseline_goals": 2.38, 
        "cups": ["Coupe de France", "Trophée des Champions"]
    },
    "germany": {
        "tier_1": "Bundesliga", "baseline_goals": 3.18, 
        "tier_2": "2. Bundesliga", "tier_2_baseline_goals": 3.02, 
        "cups": ["DFB-Pokal", "DFL-Supercup"]
    },
    "italy": {
        "tier_1": "Serie A", "baseline_goals": 2.58, 
        "tier_2": "Serie B", "tier_2_baseline_goals": 2.46, 
        "cups": ["Coppa Italia", "Supercoppa Italiana"]
    },
    "argentina": {
        "tier_1": "Liga Profesional", "baseline_goals": 2.11, 
        "tier_2": "Primera Nacional", "tier_2_baseline_goals": 2.05, 
        "cups": ["Copa Argentina", "Copa de la Liga"]
    },
    "austria": {
        "tier_1": "Austrian Football Bundesliga", "baseline_goals": 2.90, 
        "tier_2": "2. Liga", "tier_2_baseline_goals": 2.82, 
        "cups": ["Austrian Cup"]
    },
    "belgium": {
        "tier_1": "Belgian Pro League", "baseline_goals": 2.85, 
        "tier_2": "Challenger Pro League", "tier_2_baseline_goals": 2.78, 
        "cups": ["Belgian Cup", "Belgian Super Cup"]
    },
    "brazil": {
        "tier_1": "Campeonato Brasileiro Série A", "baseline_goals": 2.40, 
        "tier_2": "Campeonato Brasileiro Série B", "tier_2_baseline_goals": 2.26, 
        "cups": ["Copa do Brasil"]
    },
    "china": {
        "tier_1": "Chinese Super League", "baseline_goals": 2.65, 
        "tier_2": "China League One", "tier_2_baseline_goals": 2.48, 
        "cups": ["Chinese FA Cup", "Chinese FA Super Cup"]
    },
    "croatia": {
        "tier_1": "Croatian Football League", "baseline_goals": 2.60, 
        "tier_2": "First Football League (1. NL)", "tier_2_baseline_goals": 2.52, 
        "cups": ["Croatian Football Cup"]
    },
    "denmark": {
        "tier_1": "Danish Superliga", "baseline_goals": 2.75, 
        "tier_2": "Danish 1st Division", "tier_2_baseline_goals": 2.94, 
        "cups": ["Danish Cup"]
    },
    "finland": {
        "tier_1": "Veikkausliiga", "baseline_goals": 2.68, 
        "tier_2": "Ykkösliiga", "tier_2_baseline_goals": 2.88, 
        "cups": ["Suomen Cup", "Finnish League Cup"]
    },
    "iceland": {
        "tier_1": "Best deild karla", "baseline_goals": 3.20, 
        "tier_2": "1. deild karla (Lengjudeildin)", "tier_2_baseline_goals": 3.42, 
        "cups": ["Icelandic Cup", "Icelandic League Cup"]
    },
    "netherlands": {
        "tier_1": "Eredivisie", "baseline_goals": 3.10, 
        "tier_2": "Eerste Divisie", "tier_2_baseline_goals": 3.01, 
        "cups": ["KNVB Cup", "Johan Cruyff Shield"]
    },
    "norway": {
        "tier_1": "Eliteserien", "baseline_goals": 3.02, 
        "tier_2": "1. divisjon (OBOS-ligaen)", "tier_2_baseline_goals": 3.14, 
        "cups": ["Norwegian Football Cup"]
    },
    "poland": {
        "tier_1": "Ekstraklasa", "baseline_goals": 2.62, 
        "tier_2": "I Liga", "tier_2_baseline_goals": 2.55, 
        "cups": ["Polish Cup", "Polish SuperCup"]
    },
    "portugal": {
        "tier_1": "Primeira Liga", "baseline_goals": 2.70, 
        "tier_2": "Liga Portugal 2", "tier_2_baseline_goals": 2.51, 
        "cups": ["Taça de Portugal", "Taça da Liga"]
    },
    "scotland": {
        "tier_1": "Scottish Premiership", "baseline_goals": 2.78, 
        "tier_2": "Scottish Championship", "tier_2_baseline_goals": 2.84, 
        "cups": ["Scottish Cup", "Scottish League Cup"]
    },
    "switzerland": {
        "tier_1": "Swiss Super League", "baseline_goals": 2.95, 
        "tier_2": "Swiss Challenge League", "tier_2_baseline_goals": 2.81, 
        "cups": ["Swiss Cup"]
    },
    "usa": {
        "tier_1": "Major League Soccer", "baseline_goals": 2.92, 
        "cups": ["MLS Cup Playoffs"]
    },
    "usa_usl_championship": {
        "tier_1": "USL Championship", "baseline_goals": 2.74, 
        "cups": ["US Open Cup"]
    }
}

TEAM_NAME_NORMALIZATION_MAP = {
    "manchester united": "man utd", "manchester city": "man city",
    "tottenham hotspur": "tottenham", "wolverhampton wanderers": "wolves",
    "brighton and hove albion": "brighton", "west ham united": "west ham",
    "real madrid castilla": "real madrid b", "bayern munchen": "bayern munich",
    "internazionale": "inter", "clube atletico mineiro": "atletico mineiro"
}

def normalize_team_name(name_str):
    if not name_str or pd.isna(name_str): return ""
    cleaned = str(name_str).lower().strip()
    return TEAM_NAME_NORMALIZATION_MAP.get(cleaned, cleaned)

SQUAD_TURNOVER_MATRIX = {
    "stable": {"att_modifier": 1.00, "def_modifier": 1.00},
    "promoted": {"att_modifier": 0.88, "def_modifier": 1.15},
    "relegated": {"att_modifier": 1.12, "def_modifier": 0.90}
}

def calculate_time_decay_weight(days_ago, half_life_days=45, freeze_decay=False):
    if freeze_decay: return 1.0
    return math.exp(-0.69314718056 * (max(0, days_ago) / max(1, half_life_days)))

def calculate_rest_multiplier(days_rest):
    if days_rest <= 2: return 0.88
    elif days_rest == 3: return 0.94
    elif days_rest >= 4 and days_rest <= 6: return 1.00
    elif days_rest >= 7 and days_rest <= 10: return 1.04
    else: return 0.97
def parse_live_team_averages(df, team, current_ts, half_life_days=45, status_override="stable", freeze_decay=False):
    fallbacks = {
        "games_played": 0, "goals_scored": 1.0, "goals_conceded": 1.0,
        "sot": 3.5, "big_chances": 1.2, "box_threat": 12.0, "through_passes": 2.0,
        "final_entries": 35.0, "interceptions": 11.0, "recoveries": 45.0, "saves": 3.0,
        "ground_duels": 0.50, "aerial_duels": 0.50, "tackles": 0.50, "dribbles": 0.50,
        "pass_f3": 0.70, "att_strength_goals": 1.0, "def_resistance": 1.0
    }
    
    if df.empty: return fallbacks
    norm_target = normalize_team_name(team)
    t_df = df[(df["home_team"].apply(normalize_team_name) == norm_target) | 
              (df["away_team"].apply(normalize_team_name) == norm_target)].copy()
    if t_df.empty: return fallbacks
        
    t_df["match_timestamp"] = pd.to_datetime(t_df["match_timestamp"])
    t_df = t_df[t_df["match_timestamp"] < pd.to_datetime(current_ts)]
    if t_df.empty: return fallbacks

    t_df = t_df.sort_values(by="match_timestamp", ascending=False).head(20)
    total_weight = 0.0
    agg_stats = {k: 0.0 for k in fallbacks.keys() if k not in ["games_played", "att_strength_goals", "def_resistance"]}
    
    for _, row in t_df.iterrows():
        days_ago = (pd.to_datetime(current_ts) - row["match_timestamp"]).days
        weight = calculate_time_decay_weight(days_ago, half_life_days, freeze_decay)
        total_weight += weight
        
        is_home = normalize_team_name(row["home_team"]) == norm_target
        gf = float(row["home_goals"]) if is_home else float(row["away_goals"])
        ga = float(row["away_goals"]) if is_home else float(row["home_goals"])
        sot = float(row["home_sot"]) if is_home else float(row["away_sot"])
        bc = float(row["home_big_chances"]) if is_home else float(row["away_big_chances"])
        bt = float(row["home_box_touches"]) if is_home else float(row["away_box_touches"])
        tp = float(row["home_through_passes"]) if is_home else float(row["away_through_passes"])
        f3_ent = float(row["home_final_third_entries"]) if is_home else float(row["away_final_third_entries"])
        inter = float(row["home_interceptions"]) if is_home else float(row["away_interceptions"])
        rec = float(row["home_recoveries"]) if is_home else float(row["away_recoveries"])
        sv = float(row["home_saves"]) if is_home else float(row["away_saves"])
        
        g_duel = float(row["home_ground_duels_won_pct"]) if is_home else float(row["away_ground_duels_won_pct"])
        a_duel = float(row["home_aerial_duels_won_pct"]) if is_home else float(row["away_aerial_duels_won_pct"])
        d_won = float(row["home_dribbles_won_pct"]) if is_home else float(row["away_dribbles_won_pct"])
        t_won = float(row["home_tackles_won_pct"]) if is_home else float(row["away_tackles_won_pct"])
        p_f3 = float(row["home_passes_final_third_pct"]) if is_home else float(row["away_passes_final_third_pct"])
        
        if math.isnan(gf): gf = 1.0
        if math.isnan(ga): ga = 1.0
        if math.isnan(sot): sot = 3.5
        if math.isnan(bc): bc = 1.2
        if math.isnan(bt): bt = 12.0
        if math.isnan(tp): tp = 2.0
        if math.isnan(f3_ent): f3_ent = 35.0
        if math.isnan(inter): inter = 11.0
        if math.isnan(rec): rec = 45.0
        if math.isnan(sv): sv = 3.0
        if math.isnan(g_duel): g_duel = 0.50
        if math.isnan(a_duel): a_duel = 0.50
        if math.isnan(d_won): d_won = 0.50
        if math.isnan(t_won): t_won = 0.50
        if math.isnan(p_f3): p_f3 = 0.70

        agg_stats["goals_scored"] += gf * weight
        agg_stats["goals_conceded"] += ga * weight
        agg_stats["sot"] += sot * weight
        agg_stats["big_chances"] += bc * weight
        agg_stats["box_threat"] += bt * weight
        agg_stats["through_passes"] += tp * weight
        agg_stats["final_entries"] += f3_ent * weight
        agg_stats["interceptions"] += inter * weight
        agg_stats["recoveries"] += rec * weight
        agg_stats["saves"] += sv * weight
        agg_stats["ground_duels"] += g_duel * weight
        agg_stats["aerial_duels"] += a_duel * weight
        agg_stats["dribbles"] += d_won * weight
        agg_stats["tackles"] += t_won * weight
        agg_stats["pass_f3"] += p_f3 * weight

    div = max(0.0001, total_weight)
    output_profile = {"games_played": len(t_df)}
    for k in agg_stats.keys():
        output_profile[k] = agg_stats[k] / div

    output_profile["att_strength_goals"] = round(max(0.2, output_profile["goals_scored"]), 2)
    output_profile["def_resistance"] = round(max(0.2, output_profile["goals_conceded"]), 2)
    return output_profile

def calculate_league_baselines(df, current_ts):
    df_copy = df.copy()
    df_copy["match_timestamp"] = pd.to_datetime(df_copy["match_timestamp"])
    historical = df_copy[df_copy["match_timestamp"] < pd.to_datetime(current_ts)].dropna(subset=["home_goals", "away_goals"])
    
    if historical.empty:
        return {"avg_home_goals": 1.45, "avg_away_goals": 1.15, "baseline_goals": 2.60}
        
    avg_h = historical["home_goals"].mean()
    avg_a = historical["away_goals"].mean()
    return {
        "avg_home_goals": max(0.4, avg_h),
        "avg_away_goals": max(0.4, avg_a),
        "baseline_goals": max(0.8, avg_h + avg_a)
    }
def compile_composite_strength_vectors(df, team, current_ts, half_life_days=45, status_override="stable", freeze_decay=False):
    raw_averages = parse_live_team_averages(df, team, current_ts, half_life_days, status_override, freeze_decay)
    baselines = calculate_league_baselines(df, current_ts)
    
    if raw_averages["games_played"] == 0:
        return {"att_strength_goals": 1.0, "def_resistance": 1.0, "games_played": 0, "box_threat": 12.0}
        
    composite_attack_index = (
        (raw_averages["goals_scored"] * 0.35) + 
        (raw_averages["big_chances"] * 0.20) + 
        (raw_averages["sot"] * 0.15) + 
        (raw_averages["box_threat"] * 0.10) + 
        (raw_averages["through_passes"] * 0.10) + 
        (raw_averages["pass_f3"] * 0.10)
    )
    
    composite_defense_index = (
        (raw_averages["goals_conceded"] * 0.40) + 
        ((1.0 - raw_averages["ground_duels"]) * 0.20) + 
        ((1.0 - raw_averages["tackles"]) * 0.15) + 
        ((1.0 - raw_averages["aerial_duels"]) * 0.15) + 
        ((1.0 / max(0.5, raw_averages["saves"])) * 0.10)
    )
    
    normalized_att = composite_attack_index / max(0.1, baselines["avg_home_goals"])
    normalized_def = composite_defense_index / max(0.1, baselines["avg_away_goals"])
    
    turnover_mods = SQUAD_TURNOVER_MATRIX.get(status_override.lower().strip(), {"att_modifier": 1.0, "def_modifier": 1.0})
    final_att = max(0.1, normalized_att * turnover_mods["att_modifier"])
    final_def = max(0.1, normalized_def * turnover_mods["def_modifier"])
    
    return {
        "att_strength_goals": round(final_att, 4),
        "def_resistance": round(final_def, 4),
        "games_played": raw_averages["games_played"],
        "box_threat": round(raw_averages["box_threat"], 2)
    }

def calculate_dixon_coles_tau(x, y, mu, rho, tau_adjustment=1.0):
    if x == 0 and y == 0: return 1.0 - (mu * rho * tau_adjustment)
    elif x == 1 and y == 0: return 1.0 + (mu * tau_adjustment)
    elif x == 0 and y == 1: return 1.0 + (rho * tau_adjustment)
    elif x == 1 and y == 1: return 1.0 - tau_adjustment
    else: return 1.0

def predict_match_probabilities(historical_matches, home_team, away_team, current_timestamp, baseline_goals=2.65, home_rest_days=5, away_rest_days=5, home_status="stable", away_status="stable", max_score=6, vol_dampener=1.0, freeze_decay=False):
    h_vectors = compile_composite_strength_vectors(historical_matches, home_team, current_timestamp, 45, home_status, freeze_decay)
    a_vectors = compile_composite_strength_vectors(historical_matches, away_team, current_timestamp, 45, away_status, freeze_decay)
    baselines = calculate_league_baselines(historical_matches, current_timestamp)
    
    h_rest_mod = calculate_rest_multiplier(home_rest_days)
    a_rest_mod = calculate_rest_multiplier(away_rest_days)
    
    hfa_att = max(1.0, min(1.30, baselines["avg_home_goals"] / max(0.4, baselines["avg_away_goals"])))
    hfa_def = max(0.7, min(1.00, baselines["avg_away_goals"] / max(0.4, baselines["avg_home_goals"])))
    
    lambda_home = h_vectors["att_strength_goals"] * a_vectors["def_resistance"] * baselines["avg_home_goals"] * h_rest_mod * hfa_att
    lambda_away = a_vectors["att_strength_goals"] * h_vectors["def_resistance"] * baselines["avg_away_goals"] * a_rest_mod * hfa_def
    
    lambda_home = max(0.01, lambda_home * vol_dampener)
    lambda_away = max(0.01, lambda_away * vol_dampener)
    
    score_matrix = np.zeros((max_score + 1, max_score + 1))
    prob_home_win, prob_draw, prob_away_win = 0.0, 0.0, 0.0
    rho_correlation = -0.05
    
    for h_g in range(max_score + 1):
        for a_g in range(max_score + 1):
            p_h = (math.pow(lambda_home, h_g) * math.exp(-lambda_home)) / math.factorial(h_g)
            p_a = (math.pow(lambda_away, a_g) * math.exp(-lambda_away)) / math.factorial(a_g)
            cell_probability = p_h * p_a
            
            tau_mod = calculate_dixon_coles_tau(h_g, a_g, lambda_home, lambda_away, rho_correlation)
            final_cell_p = max(0.0, cell_probability * tau_mod)
            
            score_matrix[h_g, a_g] = final_cell_p
            if h_g > a_g: prob_home_win += final_cell_p
            elif a_g > h_g: prob_away_win += final_cell_p
            else: prob_draw += final_cell_p

    m_sum = np.sum(score_matrix)
    if m_sum > 0.0: score_matrix = score_matrix / m_sum
    
    return {
        "market_probabilities": {
            "1 (Home Win)": round(prob_home_win / max(0.001, m_sum), 4),
            "X (Draw)": round(prob_draw / max(0.001, m_sum), 4),
            "2 (Away Win)": round(prob_away_win / max(0.001, m_sum), 4)
        },
        "raw_matrix": score_matrix
    }
def run_rolling_window_backtest(df, baseline_goals, window_days=180, evaluation_step_days=7, vol_dampener=1.0):
    sorted_df = df.sort_values(by="match_timestamp").reset_index(drop=True)
    sorted_df["match_timestamp"] = pd.to_datetime(sorted_df["match_timestamp"])
    
    total_records = len(sorted_df)
    if total_records <= 20: return pd.DataFrame()
    backtest_records = []
    
    for current_idx in range(20, total_records):
        match = sorted_df.iloc[current_idx]
        rolling_training_pool = sorted_df.iloc[max(0, current_idx - 20):current_idx]
        h_team, a_team, match_ts = match["home_team"], match["away_team"], match["match_timestamp"]
        
        norm_h = normalize_team_name(h_team)
        norm_a = normalize_team_name(a_team)
        pool_homes = rolling_training_pool["home_team"].apply(normalize_team_name).values
        pool_aways = rolling_training_pool["away_team"].apply(normalize_team_name).values
        
        if not (norm_h in pool_homes or norm_h in pool_aways) or not (norm_a in pool_homes or norm_a in pool_aways): 
            continue
        
        res = predict_match_probabilities(
            historical_matches=rolling_training_pool, home_team=h_team, away_team=a_team, current_timestamp=match_ts,
            baseline_goals=baseline_goals, home_rest_days=int(match.get("home_rest_days", 5)), away_rest_days=int(match.get("away_rest_days", 5)),
            home_status=str(match.get("home_status", "stable")), away_status=str(match.get("away_status", "stable")), max_score=6, vol_dampener=vol_dampener
        )
        
        hg, ag = int(match["home_goals"]), int(match["away_goals"])
        actual = "1 (Home Win)" if hg > ag else ("2 (Away Win)" if ag > hg else "X (Draw)")
        pred_prob = res["market_probabilities"][actual]
        
        backtest_records.append({
            "match_timestamp": match_ts, "home_team": h_team, "away_team": a_team,
            "home_goals": hg, "away_goals": ag, "actual_outcome": actual,
            "model_probability": pred_prob, "log_loss": round(-math.log(max(1e-15, pred_prob)), 5)
        })
    return pd.DataFrame(backtest_records)

def generate_dynamic_league_table(df):
    historical = df.dropna(subset=["home_goals", "away_goals"])
    if historical.empty:
        return pd.DataFrame(columns=["Club Team", "Played", "Won", "Drawn", "Lost", "Points"])
    teams = pd.concat([historical["home_team"], historical["away_team"]]).unique()
    table_data = {t: {"Played": 0, "Won": 0, "Drawn": 0, "Lost": 0, "Points": 0} for t in teams}
    
    for _, row in historical.iterrows():
        h, a = row["home_team"], row["away_team"]
        hg, ag = int(row["home_goals"]), int(row["away_goals"])
        table_data[h]["Played"] += 1
        table_data[a]["Played"] += 1
        if hg > ag:
            table_data[h]["Won"] += 1
            table_data[h]["Points"] += 3
            table_data[a]["Lost"] += 1
        elif ag > hg:
            table_data[a]["Won"] += 1
            table_data[a]["Points"] += 3
            table_data[h]["Lost"] += 1
        else:
            table_data[h]["Drawn"] += 1
            table_data[h]["Points"] += 1
            table_data[a]["Drawn"] += 1
            table_data[a]["Points"] += 1
            
    compiled_df = pd.DataFrame.from_dict(table_data, orient="index").reset_index()
    compiled_df = compiled_df.rename(columns={"index": "Club Team"})
    return compiled_df.sort_values(by=["Points", "Won"], ascending=False).reset_index(drop=True)
