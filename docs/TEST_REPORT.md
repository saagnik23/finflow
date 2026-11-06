# SpendStory Test & Quality Assurance Report

## 1. Test Suite Summary

Executed test command: `pytest -v`

```
============================= test session starts ==============================
platform darwin -- Python 3.13.5, pytest-9.2.0, pluggy-1.7.0 -- .venv/bin/python3
cachedir: .pytest_cache
rootdir: /Users/saagnikdey/financecia2/SpendStory
plugins: anyio-4.16.0
collected 32 items

tests/test_analytics.py::test_independent_demo_totals_verification PASSED [  3%]
tests/test_analytics.py::test_transfer_exclusion PASSED                  [  6%]
tests/test_analytics.py::test_budget_comparisons_and_suggestions PASSED  [  9%]
tests/test_analytics.py::test_format_inr PASSED                          [ 12%]
tests/test_analytics.py::test_sanitize_and_safe_csv_export PASSED        [ 15%]
tests/test_analytics.py::test_budget_no_target_and_zero_target PASSED    [ 18%]
tests/test_analytics.py::test_deficit_summary_and_trend_edge_cases PASSED [ 21%]
tests/test_categorizer.py::test_categorizer_fit_and_classes PASSED       [ 25%]
tests/test_categorizer.py::test_categorizer_known_predictions PASSED     [ 28%]
tests/test_categorizer.py::test_categorizer_abstains_on_unknown_vocabulary PASSED [ 31%]
tests/test_categorizer.py::test_categorizer_empty_description PASSED     [ 34%]
tests/test_categorizer.py::test_pipeline_isolation_from_holdout PASSED   [ 37%]
tests/test_storage.py::test_add_and_get_transaction PASSED               [ 40%]
tests/test_storage.py::test_idempotent_import_skips_identical_payload PASSED [ 43%]
tests/test_storage.py::test_import_detects_conflicting_id_payload PASSED [ 46%]
tests/test_storage.py::test_budget_persistence PASSED                    [ 50%]
tests/test_storage.py::test_load_demo_data_idempotency PASSED            [ 53%]
tests/test_transactions.py::test_parse_amount_to_paise_valid PASSED      [ 56%]
tests/test_transactions.py::test_parse_amount_to_paise_invalid PASSED    [ 59%]
tests/test_transactions.py::test_validate_date PASSED                    [ 62%]
tests/test_transactions.py::test_validate_transaction_row_income_and_transfer PASSED [ 65%]
tests/test_transactions.py::test_validate_transaction_row_expense PASSED [ 68%]
tests/test_transactions.py::test_parse_transactions_csv_valid PASSED     [ 71%]
tests/test_transactions.py::test_parse_transactions_csv_atomic_on_duplicate_id PASSED [ 75%]
tests/test_transactions.py::test_parse_transactions_csv_atomic_on_invalid_amount PASSED [ 78%]
tests/test_transactions.py::test_parse_transactions_csv_invalid_header PASSED [ 81%]
tests/test_transactions.py::test_compute_fingerprint PASSED              [ 84%]
tests/test_ui_smoke.py::test_app_startup_and_render PASSED               [ 87%]
tests/test_ui_smoke.py::test_app_navigation_and_views PASSED             [ 90%]
tests/test_ui_smoke.py::test_drilldown_and_filtering PASSED              [ 93%]
tests/test_ui_smoke.py::test_overview_budget_shortcut_and_slider_save PASSED [ 96%]
tests/test_ui_smoke.py::test_hosted_demo_seeds_and_isolates_each_session PASSED [100%]

============================== 32 passed in 2.26s ==============================
```

---

## 2. Machine Learning Holdout Evaluation

Executed command: `python scripts/evaluate_model.py`

```
=================================================================
  Student Finance Assistant — ML Categorizer Evaluation
=================================================================
Training samples:  72
Holdout samples:   18
Training classes:  ['Bills', 'Education', 'Entertainment', 'Food', 'Shopping', 'Transport']
-----------------------------------------------------------------

Holdout Classification Report:
               precision    recall  f1-score   support

        Bills       1.00      0.33      0.50         3
    Education       1.00      0.33      0.50         3
Entertainment       0.00      0.00      0.00         3
         Food       1.00      0.67      0.80         3
        Other       0.00      0.00      0.00         0
     Shopping       0.00      0.00      0.00         3
    Transport       1.00      0.33      0.50         3

     accuracy                           0.28        18
    macro avg       0.57      0.24      0.33        18
 weighted avg       0.67      0.28      0.38        18

Overall Accuracy:   0.2778 (27.8%)
Abstentions:        13 / 18 (72.2%)
-----------------------------------------------------------------
Report written to: reports/model_evaluation.json
=================================================================
```

---

## 3. Automated Cursor & Micro-Interaction Audit

Executed command: `python3 scripts/verify_recomposition_cursor.py`

| Interaction Scenario | Expected State | Verified State | Status |
|---|---|---|---|
| **Neutral canvas movement** | Follower displays Arrow (`is-interactive=False`) | `{'exists': True, 'isInteractive': False, 'opacity': '1'}` | PASS |
| **Top nav pill hover** | Follower switches to Hand (`is-interactive=True`) | `{'isInteractive': True}` | PASS |
| **Text input hover** | Follower hidden (`opacity: 0`), native OS I-beam shown | `{'opacity': '0'}` | PASS |
| **Pointer down (press)** | Follower applies scale response (`is-pressed=True`) | `{'isPressed': True}` | PASS |

---

## 4. Objective Visual Acceptance Checklist

- [x] **Desktop primary navigation is no longer a full-height left sidebar:** Replaced by horizontal top-navigation header with segmented pills and utility actions.
- [x] **Main content uses a new page composition:** Centered max-width 1360px workspace with deliberate vertical rhythm.
- [x] **Four equal KPI cards are no longer arranged as the old single row:** Replaced by single Monthly Snapshot Hero.
- [x] **Monthly summary is a distinct hero composition:** Recorded Surplus prominently featured in 38px bold with dynamic status badge, supported inline by Income, Expenses, and Transfers Excluded.
- [x] **Cash flow and category spending use an asymmetric composition:** 62% cash flow movement timeline alongside 38% ranked spending bars.
- [x] **Category spending is not the same oversized purple donut:** Replaced with clean ranked horizontal bars displaying category names, exact amounts, and percentage shares.
- [x] **Budget health and recent activity are arranged in a new row/section:** 50%/50% split with progress tracks and recent transaction ledger entries.
- [x] **Category-review reminder is integrated when relevant:** Contextual attention strip appears when items need human review.
- [x] **Old purple/indigo chart palette is removed:** Sage green (`#83AD96`), muted coral (`#C77F78`), charcoal (`#202126`), and pale lime (`#E4F477`) applied.
- [x] **Typography reflects clean geometric style:** Manrope font family loaded with tabular figures.
- [x] **All pages share the new application shell:** Overview, Transactions, Budgets, Category Review, and Model Evaluation.
- [x] **Cursor artwork matches supplied original artwork exactly:** Zero reinterpretation, exact silhouettes, facial expressions, and shadows preserved.

---

## 5. Functional Acceptance Checklist

- [x] App starts with `./.venv/bin/streamlit run app.py --server.address 127.0.0.1 --server.port 8501`.
- [x] Sample ledger loads via `Try sample data` (218 transactions).
- [x] Overview values are computed from selected month (e.g. November 2026: Income ₹19,300, Expenses ₹14,160, Surplus ₹5,140, Transfers ₹2,750).
- [x] Transfers remain excluded from surplus totals.
- [x] Search input filters transactions and navigates to Transactions view.
- [x] Month selection updates dashboard totals and query params.
- [x] Budget target configuration modal preserves all slider values and updates SQLite.
- [x] Category Review confirm/correct actions update database records atomically.
- [x] CSV export generates valid UTF-8 transaction CSV.
- [x] SQLite persistence verified in both local and hosted demo modes.
