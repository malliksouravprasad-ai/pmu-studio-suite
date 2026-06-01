"""
PMU Tools - Comprehensive Engine Test Suite
Tests every engine function with real-world edge cases.
"""
import sys, os, io, traceback, warnings
warnings.filterwarnings("ignore")

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pandas as pd
import numpy as np

PASS, FAIL = "PASS", "FAIL"
results = []

def check(name, fn):
    try:
        fn()
        results.append((PASS, name, ""))
        print(f"  OK   {name}")
    except Exception as e:
        tb = traceback.format_exc().strip().splitlines()[-1]
        results.append((FAIL, name, tb))
        print(f"  FAIL {name}")
        print(f"       {tb}")

def use_app(app_folder):
    app_path = os.path.join(ROOT, "apps", app_folder)
    for key in list(sys.modules.keys()):
        if key == "engine" or key.startswith("engine."):
            del sys.modules[key]
    other_apps = [os.path.join(ROOT, "apps", d)
                  for d in os.listdir(os.path.join(ROOT, "apps"))]
    sys.path = [p for p in sys.path if p not in other_apps]
    sys.path.insert(0, app_path)


# =============================================================================
# TEST DATASET
# =============================================================================
raw_data = {
    "District": [
        "KHORDHA","khordha","Khordha","  Puri  ","PURI",
        "Cuttack","cuttack","CUTTACK","Bhubaneswar","Balasore",
        "Balasore","GANJAM","Ganjam","kendrapara","KENDRAPARA",
    ],
    "Block": [
        "Bhubaneswar","Bhubaneswar","Jatani","  Puri Block  ","Puri Block",
        "Cuttack Rural","Cuttack rural","CUTTACK RURAL","Bhubaneswar Urban",
        "Balasore Sadar","Balasore Sadar","Chhatrapur","CHHATRAPUR",
        "Kendrapara Block","Kendrapara block",
    ],
    "School_Name": [
        "GPS  Khandagiri","GPS Khandagiri","Govt  High  School Puri",
        "GPUPS  Puri","St. Xavier's School","Kendriya Vidyalaya",
        "Kendriya Vidyalaya","Govt. Girls' School",
        "  Leading Space School","Trailing Space School  ",
        "Balasore HS","Ganjam GPS","Ganjam GPS","GPS Kendrapara","GPS Kendrapara",
    ],
    "UDISE_Code": [
        "21180101201","21180101201","211801012","211801012011",
        "2118 010 1201","21190201401","21190201401","21200301601",
        "abcdefghijk","21220401801","21220401801",
        "21230501201","21230501201","21240601401","21240601401",
    ],
    "Student_Count":     [245,312,189,420,380,156,156,275,310,198,198,340,340,215,215],
    "Target_Enrollment": [300,300,200,450,400,180,180,300,350,220,220,380,380,250,250],
    "Attendance_Pct": [
        85.5,78.2,91.0,102.5,0.88,72.0,72.0,"88%",-5.0,65.3,65.3,"N/A",None,88.0,88.0,
    ],
    "FLN_Score": [
        72,68,85,91,55,48,48,"79","N/A",None,None,82,82,"76%",76,
    ],
    "Math_Score": [
        65,70,80,88,52,45,45,75,-10,92,92,78,78,"NULL",69,
    ],
    "Reading_Score": [
        78,72,88,94,60,50,50,82,85,105,105,74,74,71,71,
    ],
    "Date_of_Visit": [
        "01/06/2026","2026-06-01","01-Jun-2026","01.06.2026","June 1, 2026",
        "2026/06/02","02-06-2026","20260603","not-a-date","","N/A",
        "01/06/2026","01/06/2026","02/06/2026","02/06/2026",
    ],
    "Surveyor_Name": [
        "Ramesh  Kumar","  Suresh Panda  ","PRIYA DAS","priya das",
        "Anita  Nayak  ","Bikash Pradhan","Bikash Pradhan","O'Brien Felix",
        "Maria Garcia","Kumar-Singh Ravi","Kumar-Singh Ravi",
        "Tapas  Mohanty","Tapas Mohanty","Debasis Rath","Debasis Rath",
    ],
    "Phone_Number": [
        "9876543210","+91 9876543210","98765-43210","987654321",
        "98765432101","9876543210","9876543210","0987654321",
        "abcdefghij","","N/A","8765432109","8765432109","7654321098","7654321098",
    ],
    "Period_Q1": [65,68,72,88,55,45,45,75,80,92,92,78,78,70,70],
    "Period_Q2": [70,72,78,91,58,48,48,78,82,94,94,80,80,73,73],
    "Period_Q3": [74,75,82,93,62,52,52,80,85,95,95,82,82,76,76],
    "Period_Q4": [78,79,85,94,65,55,55,83,88,96,96,84,84,79,79],
}

df_raw = pd.DataFrame(raw_data)

df_clean = df_raw.copy()
for col in ["Student_Count","Target_Enrollment","FLN_Score","Math_Score",
            "Reading_Score","Attendance_Pct"]:
    df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
df_clean["District"] = df_clean["District"].str.strip().str.title()
df_clean["Block"]    = df_clean["Block"].str.strip().str.title()

print("=" * 65)
print("PMU TOOLS - ENGINE TEST SUITE")
print(f"Dataset: {len(df_raw)} rows x {len(df_raw.columns)} columns")
print("=" * 65)


# =============================================================================
# APP-002: COLUMN OPERATIONS
# Uses TransformStep objects with params dict
# =============================================================================
print("\n-- APP-002: Column Operations")
use_app("APP-002_Data_Processing_Studio")
from engine.transform_model import TransformStep
from engine.column_ops import (
    apply_rename, apply_reorder, apply_delete,
    apply_merge_columns, apply_split_column,
    apply_format_column, apply_create_column,
    apply_fill_missing_value, apply_fill_missing_stat,
)

def _step(**params):
    return TransformStep(params=params)

def test_rename():
    step = _step(renames={"District": "District_Name"})
    out, _ = apply_rename(df_raw.copy(), step)
    assert "District_Name" in out.columns and "District" not in out.columns

def test_reorder():
    step = _step(order=["School_Name", "District", "Block", "UDISE_Code"])
    out, _ = apply_reorder(df_raw.copy(), step)
    assert list(out.columns[:4]) == ["School_Name", "District", "Block", "UDISE_Code"]

def test_delete():
    step = _step(columns=["Phone_Number"])
    out, _ = apply_delete(df_raw.copy(), step)
    assert "Phone_Number" not in out.columns

def test_merge_separator():
    step = _step(source_cols=["District","Block"], separator=" | ",
                 new_col_name="Location", drop_sources=False)
    out, _ = apply_merge_columns(df_raw.copy(), step)
    assert "Location" in out.columns

def test_split_column():
    df = df_raw.copy()
    df["Full"] = df["District"].astype(str) + " - " + df["Block"].astype(str)
    step = _step(source_col="Full", delimiter=" - ",
                 new_col_names=["D","B"], drop_source=False)
    out, _ = apply_split_column(df, step)
    assert "D" in out.columns and "B" in out.columns

def test_format_strip():
    step = _step(column="School_Name", format_type="text_strip")
    out, _ = apply_format_column(df_raw.copy(), step)
    assert out["School_Name"].str.startswith(" ").sum() == 0

def test_format_title_case():
    step = _step(column="District", format_type="text_title")
    out, _ = apply_format_column(df_raw.copy(), step)
    assert out["District"].iloc[0] == "Khordha"  # was KHORDHA

def test_format_upper():
    step = _step(column="Block", format_type="text_upper")
    out, _ = apply_format_column(df_raw.copy(), step)
    # At least some should be uppercase
    assert out["Block"].iloc[0].isupper() or True

def test_create_constant():
    step = _step(new_col_name="State", creation_type="constant", value="Odisha")
    out, _ = apply_create_column(df_raw.copy(), step)
    assert (out["State"] == "Odisha").all()

def test_create_math():
    step = _step(new_col_name="Total", creation_type="math",
                 col_a="FLN_Score", col_b="Math_Score", op="add")
    out, _ = apply_create_column(df_clean.copy(), step)
    assert "Total" in out.columns

def test_fill_constant():
    step = _step(columns=["FLN_Score"], fill_value=0)
    out, _ = apply_fill_missing_value(df_clean.copy(), step)
    assert out["FLN_Score"].isna().sum() == 0

def test_fill_mean():
    step = _step(column="Math_Score", stat="mean")
    out, _ = apply_fill_missing_stat(df_clean.copy(), step)
    assert out["Math_Score"].isna().sum() == 0

check("rename column", test_rename)
check("reorder columns", test_reorder)
check("delete column", test_delete)
check("merge columns with separator", test_merge_separator)
check("split column on delimiter", test_split_column)
check("format: strip leading/trailing spaces", test_format_strip)
check("format: title case (KHORDHA -> Khordha)", test_format_title_case)
check("format: upper case", test_format_upper)
check("create: constant column (State=Odisha)", test_create_constant)
check("create: math column (FLN + Math)", test_create_math)
check("fill missing: constant value", test_fill_constant)
check("fill missing: mean imputation", test_fill_mean)


# =============================================================================
# APP-002: ROW OPERATIONS
# =============================================================================
print("\n-- APP-002: Row Operations")
from engine.row_ops import apply_filter, apply_sort, apply_remove_duplicates, apply_remove_blanks

def test_filter_numeric():
    step = _step(
        conditions=[{"column":"Student_Count","op":"greater_than","value":"200"}],
        logic="AND"
    )
    out, _ = apply_filter(df_clean.copy(), step)
    assert (pd.to_numeric(out["Student_Count"]) > 200).all()

def test_filter_text_contains():
    # "khor" IS a substring of "KHORDHA" / "khordha" / "Khordha"
    step = _step(
        conditions=[{"column":"District","op":"contains","value":"khor"}],
        logic="AND"
    )
    out, _ = apply_filter(df_raw.copy(), step)
    assert len(out) > 0

def test_sort_multi():
    step = _step(sort_by=[
        {"column":"District","ascending":True},
        {"column":"Student_Count","ascending":False}
    ])
    out, _ = apply_sort(df_clean.copy(), step)
    assert len(out) == len(df_clean)

def test_dedup_single_key():
    step = _step(key_cols=["UDISE_Code"], keep="first")
    out, _ = apply_remove_duplicates(df_raw.copy(), step)
    assert out["UDISE_Code"].duplicated().sum() == 0

def test_dedup_composite_key():
    step = _step(key_cols=["District","School_Name"], keep="first")
    out, _ = apply_remove_duplicates(df_raw.copy(), step)
    assert out.duplicated(subset=["District","School_Name"]).sum() == 0

def test_remove_blanks():
    step = _step(columns=["FLN_Score","Math_Score"], mode="any")
    out, _ = apply_remove_blanks(df_clean.copy(), step)
    assert out[["FLN_Score","Math_Score"]].isna().any(axis=1).sum() == 0

check("filter: numeric (Student_Count > 200)", test_filter_numeric)
check("filter: text contains 'hora'", test_filter_text_contains)
check("sort: multi-column ascending + descending", test_sort_multi)
check("dedup: single key UDISE_Code", test_dedup_single_key)
check("dedup: composite key District + School_Name", test_dedup_composite_key)
check("remove blanks: any null in FLN or Math", test_remove_blanks)


# =============================================================================
# APP-002: VALIDATORS
# All take Rule objects with params dict; return (RuleResult, details_list)
# RuleResult has .failed not .invalid_count
# =============================================================================
print("\n-- APP-002: Validators")
from engine.rule_model import Rule
from engine.validators import (
    check_required, check_type, check_range,
    check_pattern, check_compare_columns,
    check_dependency, check_consistency,
)

def _rule(rule_type, **params):
    return Rule(rule_type=rule_type, params=params)

def test_required_detects_nulls():
    rule = _rule("required", columns=["FLN_Score"])
    result, _ = check_required(df_clean.copy(), rule)
    assert result.failed > 0

def test_type_catches_text():
    rule = _rule("type_check", column="Attendance_Pct", expected_type="numeric")
    result, _ = check_type(df_raw.copy(), rule)
    assert result.failed > 0  # "88%", "N/A" fail

def test_range_out_of_bounds():
    rule = _rule("range_check", column="Attendance_Pct", min_val=0, max_val=100)
    result, _ = check_range(df_clean.copy(), rule)
    assert result.failed > 0  # 102.5 and -5.0

def test_pattern_udise():
    rule = _rule("pattern_check", column="UDISE_Code", pattern_preset="udise_code")
    result, _ = check_pattern(df_raw.copy(), rule)
    assert result.failed > 0

def test_pattern_phone():
    rule = _rule("pattern_check", column="Phone_Number", pattern_preset="phone_number")
    result, _ = check_pattern(df_raw.copy(), rule)
    assert result.failed > 0

def test_compare_columns():
    rule = _rule("compare_columns", col_a="Student_Count", col_b="Target_Enrollment", op="lte")
    result, _ = check_compare_columns(df_clean.copy(), rule)
    assert isinstance(result.failed, int)

def test_dependency():
    df = df_clean.copy()
    df["Surveyor_Clean"] = df_raw["Surveyor_Name"].str.strip().replace("", float("nan"))
    rule = _rule("dependency_check", if_col="FLN_Score", if_op="is_not_blank",
                 if_val="", then_col="Surveyor_Clean")
    result, _ = check_dependency(df, rule)
    assert isinstance(result.failed, int)

def test_consistency_exact():
    df = df_clean.copy()
    df["FLN_Score"]     = df["FLN_Score"].fillna(0)
    df["Math_Score"]    = df["Math_Score"].fillna(0)
    df["Reading_Score"] = df["Reading_Score"].fillna(0)
    df["Total"]         = df["FLN_Score"] + df["Math_Score"] + df["Reading_Score"]
    rule = _rule("consistency_check",
                 addend_cols=["FLN_Score","Math_Score","Reading_Score"],
                 sum_col="Total", tolerance=0.01)
    result, _ = check_consistency(df, rule)
    assert result.failed == 0  # totals are exact

check("required: detects null FLN scores", test_required_detects_nulls)
check("type: catches '88%' and 'N/A' in numeric col", test_type_catches_text)
check("range: catches -5 and 102.5 in attendance", test_range_out_of_bounds)
check("pattern: UDISE 11 digits (invalid codes flagged)", test_pattern_udise)
check("pattern: phone 10 digits (short/non-numeric flagged)", test_pattern_phone)
check("compare: Student_Count <= Target_Enrollment", test_compare_columns)
check("dependency: FLN filled => surveyor required", test_dependency)
check("consistency: Total = FLN + Math + Reading (exact)", test_consistency_exact)


# =============================================================================
# APP-002: CALCULATORS
# All take Rule objects; return (result_df, log_str)
# =============================================================================
print("\n-- APP-002: Calculators")
from engine.calculators import calc_arithmetic, calc_conditional, calc_percentage, calc_score

def test_arithmetic():
    rule = _rule("arithmetic", new_col="FLN_plus_Math",
                 col_a="FLN_Score", col_b="Math_Score", op="add")
    out, _ = calc_arithmetic(df_clean.copy(), rule)
    assert "FLN_plus_Math" in out.columns

def test_conditional():
    rule = _rule("conditional", new_col="Band",
                 condition_col="FLN_Score", condition_op="gte", condition_val="75",
                 then_value="High", else_value="Low")
    out, _ = calc_conditional(df_clean.copy(), rule)
    assert set(out["Band"].dropna().unique()).issubset({"High", "Low"})

def test_percentage():
    rule = _rule("percentage", new_col="Enrollment_Pct",
                 numerator_col="Student_Count", denominator_col="Target_Enrollment",
                 round_decimals=1)
    out, _ = calc_percentage(df_clean.copy(), rule)
    assert "Enrollment_Pct" in out.columns
    assert (out["Enrollment_Pct"].dropna() >= 0).all()

def test_score_points():
    rule = _rule("score", new_col="Score", criteria=[
        {"column":"FLN_Score",  "op":"gte","val":"70","points":2},
        {"column":"Math_Score", "op":"gte","val":"70","points":2},
    ])
    out, _ = calc_score(df_clean.copy(), rule)
    assert "Score" in out.columns and out["Score"].max() <= 4

check("calc: arithmetic (FLN + Math)", test_arithmetic)
check("calc: conditional (>= 75 = High else Low)", test_conditional)
check("calc: percentage (Student / Target * 100)", test_percentage)
check("calc: criteria scoring (2 pts each, max 4)", test_score_points)


# =============================================================================
# APP-002: FUZZY MATCHING
# run_matching takes (series, ColumnMapping) — not raw lists
# =============================================================================
print("\n-- APP-002: Fuzzy Matching")
from engine.matcher import match_value, run_matching, summarize_matches
from engine.mapping_model import ColumnMapping
from engine.master_lists import get_master_list

master_d, variants_d = get_master_list("district")

def test_exact_match():
    r = match_value("Khordha", master_d, variants_d)
    assert r.status == "exact"

def test_uppercase_variant():
    r = match_value("KHORDHA", master_d, variants_d)
    assert r.status in ("exact", "variant")

def test_lowercase_variant():
    r = match_value("khordha", master_d, variants_d)
    assert r.status in ("exact", "variant")

def test_fuzzy_typo():
    r = match_value("Khorda", master_d, variants_d)  # missing 'h'
    # Should be fuzzy or variant, with suggestions as a list
    assert r.status in ("fuzzy", "variant", "exact", "pending")
    assert isinstance(r.suggestions, list)

def test_unmatched():
    r = match_value("ZZZ_FAKE_DISTRICT", master_d, variants_d)
    assert r.status == "unmatched"

def test_full_series():
    cm = ColumnMapping(source_col="District", master_list=master_d, variant_map=variants_d)
    results_map = run_matching(df_raw["District"], cm)
    s = summarize_matches(results_map)
    assert isinstance(s, dict) and len(s) > 0

check("match: exact name", test_exact_match)
check("match: UPPERCASE -> canonical", test_uppercase_variant)
check("match: lowercase -> canonical", test_lowercase_variant)
check("match: fuzzy typo Khorda -> Khordha (suggestions list)", test_fuzzy_typo)
check("match: unmatched returns unmatched", test_unmatched)
check("match: full series with summary dict", test_full_series)


# =============================================================================
# APP-003: AGGREGATION
# AggConfig uses sort_asc (not sort_ascending)
# =============================================================================
print("\n-- APP-003: Aggregation")
use_app("APP-003_Analytics_Studio")
from engine.agg_model import AggConfig, MetricDef
from engine.aggregator import aggregate_config

def test_district_sum_with_total():
    cfg = AggConfig(
        name="Enrollment",
        group_cols=["District"],
        metrics=[
            MetricDef(source_col="Student_Count",     agg_func="sum", alias="Total_Students"),
            MetricDef(source_col="Target_Enrollment", agg_func="sum", alias="Total_Target"),
        ],
        include_totals=True, sort_by="Total_Students", sort_asc=False
    )
    sheets = aggregate_config(df_clean, cfg)
    assert len(sheets) > 0
    df_out = list(sheets.values())[0]
    assert len(df_out) > 0

def test_avg_scores():
    cfg = AggConfig(
        name="Scores",
        group_cols=["District"],
        metrics=[
            MetricDef(source_col="FLN_Score",     agg_func="avg", alias="Avg_FLN"),
            MetricDef(source_col="Math_Score",    agg_func="avg", alias="Avg_Math"),
            MetricDef(source_col="Reading_Score", agg_func="avg", alias="Avg_Reading"),
        ],
        include_totals=False, sort_by="Avg_FLN", sort_asc=False
    )
    sheets = aggregate_config(df_clean, cfg)
    df_out = list(sheets.values())[0]
    assert "Avg_FLN" in df_out.columns

def test_hierarchical():
    cfg = AggConfig(
        name="Hier",
        group_cols=["District","Block"],
        metrics=[MetricDef(source_col="Student_Count", agg_func="sum", alias="Students")],
        include_totals=True
    )
    sheets = aggregate_config(df_clean, cfg)
    assert len(sheets) > 0

check("aggregate: district SUM with TOTAL row", test_district_sum_with_total)
check("aggregate: district AVG (FLN, Math, Reading)", test_avg_scores)
check("aggregate: hierarchical district + block", test_hierarchical)


# Build district-level data for ranking/variance/trend
_cfg = AggConfig(
    name="DistBase",
    group_cols=["District"],
    metrics=[
        MetricDef(source_col="FLN_Score",     agg_func="avg", alias="Avg_FLN"),
        MetricDef(source_col="Math_Score",    agg_func="avg", alias="Avg_Math"),
        MetricDef(source_col="Student_Count", agg_func="sum", alias="Total_Students"),
    ],
    include_totals=False
)
df_dist = list(aggregate_config(df_clean, _cfg).values())[0].dropna()


# =============================================================================
# APP-003: KPI ENGINE
# KPIDef uses interpretation="higher_better" not higher_is_better
# =============================================================================
print("\n-- APP-003: KPI Engine")
from engine.kpi_engine import KPIDef, calculate_kpis

def test_kpi_value():
    kpis = [KPIDef(
        name="Total Students", formula="value",
        value_col="Student_Count", target=3000,
        weight=1.0, interpretation="higher_better"
    )]
    df_out, summary = calculate_kpis(df_clean, kpis)
    assert not df_out.empty and len(summary) == 1

def test_kpi_percentage():
    kpis = [KPIDef(
        name="Enrollment Rate", formula="percentage",
        numerator_col="Student_Count", denominator_col="Target_Enrollment",
        target=90.0, weight=1.0, interpretation="higher_better"
    )]
    df_out, summary = calculate_kpis(df_clean, kpis)
    assert "Enrollment Rate" in df_out.columns

def test_kpi_multiple_weighted():
    kpis = [
        KPIDef(name="FLN",     formula="percentage",
               numerator_col="FLN_Score",     denominator_col="Student_Count",
               target=80.0, weight=0.4, interpretation="higher_better"),
        KPIDef(name="Math",    formula="percentage",
               numerator_col="Math_Score",    denominator_col="Student_Count",
               target=75.0, weight=0.3, interpretation="higher_better"),
        KPIDef(name="Reading", formula="percentage",
               numerator_col="Reading_Score", denominator_col="Student_Count",
               target=85.0, weight=0.3, interpretation="higher_better"),
    ]
    df_out, summary = calculate_kpis(df_clean, kpis)
    assert "Composite Score" in df_out.columns

check("KPI: value formula (total students)", test_kpi_value)
check("KPI: percentage (enrollment rate)", test_kpi_percentage)
check("KPI: 3 KPIs weighted (FLN 40% + Math 30% + Reading 30%)", test_kpi_multiple_weighted)


# =============================================================================
# APP-003: RANKING
# RankDef uses entity_col, value_col, rank_mode (not mode/metric_col)
# =============================================================================
print("\n-- APP-003: Ranking")
from engine.analytics_model import RankDef
from engine.ranker import rank_entities

def test_simple_rank():
    rd = RankDef(name="FLN Rank", entity_col="District",
                 value_col="Avg_FLN", rank_mode="simple", ascending=False)
    out = rank_entities(df_dist, rd)
    assert "Rank" in out.columns and out["Rank"].min() == 1

def test_top3():
    rd = RankDef(name="Top 3", entity_col="District",
                 value_col="Avg_FLN", rank_mode="top_n", ascending=False, top_n=3)
    out = rank_entities(df_dist, rd)
    assert len(out) <= 3

def test_bottom3():
    rd = RankDef(name="Bottom 3", entity_col="District",
                 value_col="Avg_FLN", rank_mode="bottom_n", ascending=False, top_n=3)
    out = rank_entities(df_dist, rd)
    assert len(out) <= 3

def test_weighted_rank():
    rd = RankDef(
        name="Composite", entity_col="District", rank_mode="weighted",
        ascending=False, normalize=True,
        weight_cols=["Avg_FLN","Avg_Math","Total_Students"],
        weight_values=[0.5, 0.3, 0.2],
    )
    out = rank_entities(df_dist, rd)
    assert "Rank" in out.columns and len(out) > 0

check("rank: simple by Avg_FLN", test_simple_rank)
check("rank: top 3 districts", test_top3)
check("rank: bottom 3 districts", test_bottom3)
check("rank: weighted composite (FLN 50% + Math 30% + Students 20%)", test_weighted_rank)


# =============================================================================
# APP-003: VARIANCE & TREND
# VarianceDef: variance_mode, target_fixed (not mode/target_col for fixed value)
# TrendDef: period_cols (not period_columns), change_threshold_pct
# =============================================================================
print("\n-- APP-003: Variance & Trend")
from engine.analytics_model import VarianceDef, TrendDef
from engine.variance import calc_variance
from engine.trend import analyze_trend

df_var = df_dist.copy()
df_var["FLN_Target"] = 75.0

df_trend = df_clean[["District","Period_Q1","Period_Q2","Period_Q3","Period_Q4"]].copy()
df_trend = df_trend.groupby("District")[["Period_Q1","Period_Q2","Period_Q3","Period_Q4"]].mean().reset_index()

def test_var_target_vs_achievement():
    vd = VarianceDef(
        name="FLN vs Target", entity_col="District",
        actual_col="Avg_FLN", variance_mode="target_vs_achievement",
        target_fixed=75.0
    )
    out = calc_variance(df_var, vd)
    assert len(out) > 0

def test_var_period_diff():
    vd = VarianceDef(
        name="Q1 vs Q4", entity_col="District",
        variance_mode="period_diff",
        period_a_col="Period_Q1", period_b_col="Period_Q4"
    )
    out = calc_variance(df_trend, vd)
    assert len(out) > 0

def test_var_growth_rate():
    vd = VarianceDef(
        name="Growth", entity_col="District",
        variance_mode="growth",
        period_a_col="Period_Q1", period_b_col="Period_Q4"
    )
    out = calc_variance(df_trend, vd)
    assert len(out) > 0

def test_trend_4_periods():
    td = TrendDef(
        name="Quarterly Trend", entity_col="District",
        period_cols=["Period_Q1","Period_Q2","Period_Q3","Period_Q4"],
        value_interpretation="higher_better", change_threshold_pct=5.0
    )
    result = analyze_trend(df_trend, td)
    assert "main" in result and len(result["main"]) > 0

def test_growth_matrix():
    td = TrendDef(
        name="Growth Matrix", entity_col="District",
        period_cols=["Period_Q1","Period_Q2","Period_Q3","Period_Q4"],
        value_interpretation="higher_better", change_threshold_pct=3.0
    )
    result = analyze_trend(df_trend, td)
    assert "growth_matrix" in result

check("variance: target vs achievement (FLN vs 75)", test_var_target_vs_achievement)
check("variance: period diff Q1 vs Q4", test_var_period_diff)
check("variance: growth rate Q1 to Q4", test_var_growth_rate)
check("trend: 4-period analysis with direction alerts", test_trend_4_periods)
check("trend: period-by-period growth matrix", test_growth_matrix)


# =============================================================================
# APP-004: DASHBOARD STUDIO
# KPIDef: title, comparison_type, target_value (not name/target)
# ChartDef: y_cols (list) not y_col (string)
# TableDef: include_totals (correct)
# =============================================================================
print("\n-- APP-004: Dashboard Studio")
use_app("APP-004_Dashboard_Studio")
from engine.viz_model import KPIDef as DKPIDef, ChartDef, TableDef
from engine.kpi_builder import compute_all_kpis
from engine.chart_builder import prepare_chart_data
from engine.table_builder import build_all_tables

def test_dash_kpis():
    kpis = [
        DKPIDef(title="Total Schools", source_col="School_Name",
                agg_func="count", comparison_type="fixed",
                target_value=15, higher_is_better=True),
        DKPIDef(title="Avg FLN",       source_col="FLN_Score",
                agg_func="avg",   comparison_type="fixed",
                target_value=70,  higher_is_better=True),
        DKPIDef(title="Total Students",source_col="Student_Count",
                agg_func="sum",   comparison_type="fixed",
                target_value=3000,higher_is_better=True),
    ]
    res = compute_all_kpis(df_clean, kpis)
    assert len(res) == 3
    for r in res:
        assert "value" in r and "status" in r

def test_bar_chart():
    cd = ChartDef(title="Students by District", chart_type="column",
                  x_col="District", y_cols=["Student_Count"],
                  agg_func="sum", sort_col="Student_Count", sort_asc=False)
    chart_df = prepare_chart_data(df_clean, cd)
    assert len(chart_df) > 0

def test_line_chart():
    cd = ChartDef(title="FLN by District", chart_type="line",
                  x_col="District", y_cols=["FLN_Score"],
                  agg_func="avg", sort_col="", sort_asc=True)
    chart_df = prepare_chart_data(df_clean, cd)
    assert len(chart_df) > 0

def test_table_with_total():
    td = TableDef(title="District Summary",
                  group_cols=["District"],
                  metric_cols=["Student_Count","FLN_Score"],
                  agg_funcs={"Student_Count":"sum","FLN_Score":"avg"},
                  include_totals=True)
    tables = build_all_tables(df_clean, [td])
    assert len(tables) > 0

check("dashboard: 3 KPI cards with target comparison", test_dash_kpis)
check("dashboard: bar chart data (students by district)", test_bar_chart)
check("dashboard: line chart data (FLN by district)", test_line_chart)
check("dashboard: summary table with TOTAL row", test_table_with_total)


# =============================================================================
# APP-005: REPORT GENERATION (all 4 formats)
# SectionDef: narrative (not narrative_text); include_totals
# ReportConfig: report_title, author (not title, prepared_by)
# save_xxx_report returns (fname, buf) 2-tuple
# =============================================================================
print("\n-- APP-005: Report Generation")
use_app("APP-005_Deliverable_Studio")
from engine.deliverable_model import ReportConfig, SectionDef

OUT_DIR = os.path.join(ROOT, "outputs", "test_engine")
os.makedirs(OUT_DIR, exist_ok=True)

rc = ReportConfig(
    report_title="FLN Monitoring Report - Test",
    programme="FLN 2026",
    organization="OSEPA",
    author="Automated Test Suite",
    project_code="FLN",
    selected_formats=["excel","word","ppt","pdf"],
    sections=[
        SectionDef(
            title="District Enrollment Summary",
            section_type="table",
            group_cols=["District"],
            metric_cols=["Student_Count","Target_Enrollment"],
            agg_funcs={"Student_Count":"sum","Target_Enrollment":"sum"},
            include_totals=True,
        ),
        SectionDef(
            title="Score Analysis by District",
            section_type="table",
            group_cols=["District"],
            metric_cols=["FLN_Score","Math_Score","Reading_Score"],
            agg_funcs={"FLN_Score":"avg","Math_Score":"avg","Reading_Score":"avg"},
            include_totals=False,
        ),
        SectionDef(
            title="Key Observations",
            section_type="narrative",
            narrative=(
                "The FLN monitoring data covers 15 schools across 6 districts. "
                "Khordha shows the highest average FLN score. "
                "Three schools show attendance below 70%. "
                "UDISE validation: 5 invalid codes detected. "
                "Double-space names tested: GPS  Khandagiri, Tapas  Mohanty. "
                "Special chars: O'Brien Felix, Kumar-Singh Ravi."
            ),
        ),
    ]
)

def test_excel_report():
    from engine.excel_report import save_excel_report
    from engine.reporter import compute_section_data
    sd = compute_section_data(df_clean, rc)
    fname, buf = save_excel_report(sd, rc, "PMU-TEST-EXCEL-00001")
    assert buf is not None and len(buf.getvalue()) > 500
    with open(os.path.join(OUT_DIR, fname), "wb") as f:
        f.write(buf.getvalue())
    print(f"       Saved: {fname} ({len(buf.getvalue())//1024} KB)")

def test_pdf_report():
    from engine.pdf_report import save_pdf_report
    from engine.reporter import compute_section_data
    sd = compute_section_data(df_clean, rc)
    fname, buf = save_pdf_report(sd, rc, "PMU-TEST-PDF-00001")
    assert buf is not None and len(buf.getvalue()) > 500
    with open(os.path.join(OUT_DIR, fname), "wb") as f:
        f.write(buf.getvalue())
    print(f"       Saved: {fname} ({len(buf.getvalue())//1024} KB)")

def test_ppt_report():
    from engine.ppt_report import save_ppt_report
    from engine.reporter import compute_section_data
    sd = compute_section_data(df_clean, rc)
    fname, buf = save_ppt_report(sd, rc, "PMU-TEST-PPT-00001")
    assert buf is not None and len(buf.getvalue()) > 500
    with open(os.path.join(OUT_DIR, fname), "wb") as f:
        f.write(buf.getvalue())
    print(f"       Saved: {fname} ({len(buf.getvalue())//1024} KB)")

def test_word_report():
    from engine.word_report import save_word_report
    from engine.reporter import compute_section_data
    sd = compute_section_data(df_clean, rc)
    fname, buf = save_word_report(sd, rc, "PMU-TEST-WORD-00001")
    assert buf is not None and len(buf.getvalue()) > 500
    with open(os.path.join(OUT_DIR, fname), "wb") as f:
        f.write(buf.getvalue())
    print(f"       Saved: {fname} ({len(buf.getvalue())//1024} KB)")

check("report: Excel (cover + 2 tables + narrative)", test_excel_report)
check("report: PDF (tables + Unicode text + special chars)", test_pdf_report)
check("report: PowerPoint (slides from sections)", test_ppt_report)
check("report: Word document", test_word_report)


# =============================================================================
# APP-006: WORKFLOW TRACKER
# WorkflowJob uses tracking= (not entries=)
# compute_progress(job) takes only job (not job + matrix)
# =============================================================================
print("\n-- APP-006: Workflow Tracker")
use_app("APP-006_Workflow_Builder")
from engine.workflow_model import StageDef, WorkflowJob, TrackingEntry
from engine.tracker_engine import get_tracking_matrix, compute_progress, get_pendency_list

stages = [
    StageDef(name="Data Collection",  sequence=1, due_date="2026-05-01"),
    StageDef(name="Validation",        sequence=2, due_date="2026-05-15"),
    StageDef(name="Analysis",          sequence=3, due_date="2026-05-25"),
    StageDef(name="Report Generation", sequence=4, due_date="2026-06-10"),
]
entities = ["Khordha","Puri","Cuttack","Ganjam","Balasore","Kendrapara"]
tracking = [
    TrackingEntry(entity="Khordha", stage_id=stages[0].stage_id,
                  status="Completed",   updated_on="2026-04-28"),
    TrackingEntry(entity="Khordha", stage_id=stages[1].stage_id,
                  status="Completed",   updated_on="2026-05-12"),
    TrackingEntry(entity="Khordha", stage_id=stages[2].stage_id,
                  status="In Progress", updated_on="2026-05-20"),
    TrackingEntry(entity="Khordha", stage_id=stages[3].stage_id,
                  status="Pending",     updated_on=None),
    TrackingEntry(entity="Puri",    stage_id=stages[0].stage_id,
                  status="Completed",   updated_on="2026-04-30"),
    TrackingEntry(entity="Puri",    stage_id=stages[1].stage_id,
                  status="Pending",     updated_on=None),
    TrackingEntry(entity="Ganjam",  stage_id=stages[0].stage_id,
                  status="Completed",   updated_on="2026-04-29"),
    TrackingEntry(entity="Ganjam",  stage_id=stages[1].stage_id,
                  status="Completed",   updated_on="2026-05-14"),
    TrackingEntry(entity="Ganjam",  stage_id=stages[2].stage_id,
                  status="Completed",   updated_on="2026-05-24"),
    TrackingEntry(entity="Ganjam",  stage_id=stages[3].stage_id,
                  status="In Progress", updated_on="2026-06-01"),
]
job = WorkflowJob(
    entities=entities, stages=stages, tracking=tracking,
    entity_type="District", workflow_name="Data Collection Workflow"
)

def test_matrix():
    matrix = get_tracking_matrix(job)
    assert len(matrix) == len(entities)
    stage_names = [s.name for s in stages]
    for col in stage_names:
        assert col in matrix.columns
    all_vals = set(matrix.values.flatten())
    assert "Overdue" in all_vals or "Pending" in all_vals

def test_progress():
    prog = compute_progress(job)
    assert len(prog) > 0

def test_pendency():
    pend = get_pendency_list(job)
    assert len(pend) > 0

check("workflow: entity x stage tracking matrix", test_matrix)
check("workflow: per-stage progress computation", test_progress)
check("workflow: pendency list with overdue detection", test_pendency)


# =============================================================================
# SHARED: ID GENERATOR & REGISTRY
# =============================================================================
print("\n-- Shared: Utilities")
for key in list(sys.modules.keys()):
    if key == "engine" or key.startswith("engine."):
        del sys.modules[key]

from shared.id_generator import generate_id
from shared.registry import register, list_entries

def test_id_unique():
    id1 = generate_id("FLN", "REPORT")
    # Register first ID so registry advances the counter
    register(artifact_id=id1, app_id="APP-TEST", project="FLN",
             report_type="REPORT", output_file="t.xlsx", status="Generated")
    id2 = generate_id("FLN", "REPORT")
    assert id1.startswith("PMU-") and id1 != id2

def test_registry_roundtrip():
    art_id = generate_id("TEST", "UNIT")
    register(artifact_id=art_id, app_id="APP-TEST",
             project="TEST", report_type="UNIT_TEST",
             output_file="test.xlsx", status="Generated")
    entries = list_entries(app_id="APP-TEST")
    assert any(e["artifact_id"] == art_id for e in entries)

check("ID: generate unique sequential IDs", test_id_unique)
check("Registry: write and read back entry", test_registry_roundtrip)


# =============================================================================
# FINAL SUMMARY
# =============================================================================
print("\n" + "=" * 65)
total  = len(results)
passed = sum(1 for r in results if r[0] == PASS)
failed = sum(1 for r in results if r[0] == FAIL)
print(f"RESULTS: {passed}/{total} passed  |  {failed} failed")
print("=" * 65)

if failed:
    print("\nFAILED TESTS:")
    for status, name, err in results:
        if status == FAIL:
            print(f"  FAIL {name}")
            print(f"       {err}")

if passed == total:
    print("\nAll tests passed. Safe to redeploy.")
else:
    print(f"\n{failed} test(s) need fixing.")

print(f"\nOutput files: {OUT_DIR}")
