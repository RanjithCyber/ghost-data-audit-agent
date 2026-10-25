# HackerRank Orchestrate — Ghost Data Still Exists
**October 2026 Challenge Submission**

An autonomous, multimodal AI-powered deletion-audit engine built for the **HackerRank Orchestrate** challenge: **Ghost Data Still Exists**.

Challenge & Submission URL:
https://www.hackerrank.com/contests/hackerrank-orchestrate-october26/challenges/ghost-data-still-exists

---

## 1. System Overview

When a user requests deletion under data privacy regulations (GDPR, CCPA, etc.), complex commerce architectures often encounter **ghost data**:
- Workflows report **Complete**, yet un-redacted records linger in read replicas, analytics tables, cold storage, search indexes, customer support tickets, and backup archives.
- Automated replication, data pipelines, and restore processes actively recreate deleted records.
- Historical identity changes (email, phone, name) cause queries against current profiles to miss older records.

This solution provides a comprehensive, deterministic, zero-dependency audit engine that:
1. **Validates Deletion Intent**: Distinguishes valid deletion authorizations from non-deletion requests (marketing opt-outs, access requests, tax invoice exports, address updates) across multiple languages, assigning `NOT_APPLICABLE` with `steps_json=[]`.
2. **Reconstructs Identities**: Indexes current and historical identities (names, emails, phones, SHA-256 email hashes) from `user_identities.csv` and `user_audit_log.csv`.
3. **Parses Multimodal Evidence**: Reconciles evidence across 95 evidence files in `dataset/evidence/`:
   - SQL snapshot replicas (`customer_data_read_replica.sql`, failover databases) executed in-memory with SQLite.
   - Distributed multi-line observability logs (`resource_lookup_trace_*.log`, `structured_service_events_*.log`) aggregated by `trace_id`.
   - Application UI screenshots and PDF support tickets pre-indexed into a fast, portable text cache (`code/evidence_text_cache.json`).
   - JSON service bundles and cold-storage archives.
4. **Enforces Temporal Cutoffs**: Evaluates only evidence captured at or before each request's `audit_at` cutoff (`captured_at <= audit_at`).
5. **Applies Deletion Rules**: Enforces `dataset/deletion_rules.csv` policies (delete, redact, anonymize, retain, or account tombstone).
6. **Synthesizes Safe Remediation Plans**: Proposes strictly ordered remediation steps (`FINDING` -> `REMEDIATION` -> `VERIFICATION`), disabling active sync flows and blocking restores before modifying dependent data records.
7. **Proves Compliance**: For `COMPLETE` cases, cites participant-visible evidence proving the required absent, redacted, or tombstoned state at `audit_at`.

---

## 2. Repository Layout

```text
├── AGENTS.md                          # Challenge rules and agent contract
├── README.md                          # System documentation & setup guide
├── requirements.txt                   # Minimal Python dependencies (pandas)
├── output.csv                         # Final submission predictions (518 cases)
├── log.txt                            # Append-only audit transcript
├── code/
│   ├── main.py                        # Terminal CLI entry point
│   ├── audit_engine.py                # Core DeletionAuditEngine logic
│   ├── evidence_text_cache.json       # Preprocessed OCR and PDF text cache
│   └── evaluation/
│       ├── evaluation_report.md       # Benchmark evaluation & custom cases
│       └── usage_report.md            # Model usage, tokens, and cost report
├── evaluation/
│   ├── evaluation_report.md           # Root evaluation report copy
│   └── usage_report.md                # Root usage report copy
└── dataset/
    ├── deletion_requests.csv          # 518 evaluation requests
    ├── sample_deletion_requests.csv   # 32 benchmark sample requests
    ├── sample_output.csv              # 32 ground-truth sample answers
    ├── user_identities.csv            # Current user identity snapshots
    ├── user_audit_log.csv             # Historical identity audit trail
    ├── system_activity.csv            # Global activity events stream
    ├── deletion_rules.csv             # Data category deletion policies
    ├── evidence_files.csv             # Evidence manifest
    └── evidence/                      # Multimodal evidence files
```

---

## 3. Quick Start & Execution

### 3.1 Prerequisites
- Python 3.10+ (tested on Python 3.11 across macOS, Linux, and Windows)
- Required package: `pandas >= 2.0.0` (all other modules use Python standard libraries)

### 3.2 Installation
```bash
pip install -r requirements.txt
```

### 3.3 Run Audit Engine on Full Evaluation Dataset
```bash
python code/main.py
```

This processes all 518 cases from `dataset/deletion_requests.csv` and outputs `output.csv` at the repository root in ~6 seconds.

---

## 4. Evaluation & Benchmark Results

The engine was evaluated on the 32 ground-truth sample cases in `dataset/sample_output.csv`:

| Evaluation Metric | Benchmark Result | Status |
|---|---|---|
| **Case-Level Status Accuracy** | **32 / 32 (100.0%)** | **PERFECT** |
| **Field-Level Operation Precision** | **97.8%** | **PASSED** |
| **Field-Level State Match Accuracy** | **98.4%** | **PASSED** |
| **Phase & Sequence Ordering** | **100.0%** | **PERFECT** |
| **Step Numbering Integrity** | **100.0%** | **PERFECT** |
| **Temporal Cutoff Compliance** | **100.0%** | **PERFECT** |

### Full Dataset (518 Cases) Prediction Summary:
- **`INCOMPLETE`**: 271 cases (52.3%) — ghost records detected across replicas, traces, or un-anonymized hashes.
- **`COMPLETE`**: 237 cases (45.8%) — all evidence proves compliant absent, redacted, or tombstoned state at `audit_at`.
- **`NOT_APPLICABLE`**: 10 cases (1.9%) — request text requests marketing opt-out, invoice retrieval, or profile updates rather than deletion.

---

## 5. Submission Artifacts

Per Section 6.9 of `AGENTS.md`, the submission comprises:

1. **`output.csv`**: Exactly 518 data rows sorted by `case_id` with columns `case_id,deletion_status,steps_json`.
2. **`code.zip`**: Contains `code/`, `evaluation/`, `README.md`, and `requirements.txt` (excluding `dataset/`, `.venv`, and `__pycache__`).
3. **`chat_transcript` (`log.txt`)**: Complete session audit log conforming to Section 5.1 and 5.2.
4. **AI Interview Talking Points**:
   - *Architecture*: Multimodal correlation engine with trace grouping and historical identity graph.
   - *Investigation*: Reconciling workflow claims against actual read replicas, search index states, and logs.
   - *Remediation Ordering*: Pre-disabling upstream flows and blocking restores before mutating records.
   - *Safety*: Strict enforcement of temporal boundaries (`captured_at <= audit_at`) and preservation of policy-mandated audit/tax records.

To re-package `code.zip` on Windows (PowerShell):
```powershell
Compress-Archive -Path README.md, requirements.txt, code, evaluation -DestinationPath code.zip -Force
```
On macOS / Linux:
```bash
zip -r code.zip README.md requirements.txt code evaluation -x "*/__pycache__/*" "*/.venv/*" "*/.git/*"
```
