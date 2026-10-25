"""
Ghost Data Still Exists - Main Evaluation Entrypoint
HackerRank Orchestrate (October 2026)

Runs the DeletionAuditEngine on dataset/deletion_requests.csv
and outputs root output.csv with exact format:
case_id,deletion_status,steps_json
"""

import os
import sys
import json
import csv
import pandas as pd
from audit_engine import DeletionAuditEngine

def main():
    print("Initializing HackerRank Orchestrate Deletion-Audit Engine...")
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_dir = os.path.join(repo_root, 'dataset')
    output_path = os.path.join(repo_root, 'output.csv')
    cache_path = os.path.join(repo_root, 'code', 'evidence_text_cache.json')
    
    input_csv = os.path.join(dataset_dir, 'deletion_requests.csv')
    if not os.path.exists(input_csv):
        print(f"Error: {input_csv} not found.")
        sys.exit(1)
        
    engine = DeletionAuditEngine(dataset_dir=dataset_dir, cache_file=cache_path)
    df_reqs = pd.read_csv(input_csv)
    print(f"Loaded {len(df_reqs)} evaluation cases from {input_csv}.")
    
    results = []
    
    for idx, row in df_reqs.iterrows():
        cid = str(row['case_id'])
        status, steps = engine.audit_case(row)
        
        # Serialize steps_json cleanly
        steps_str = json.dumps(steps, separators=(',', ':')) if steps else '[]'
        results.append({
            'case_id': cid,
            'deletion_status': status,
            'steps_json': steps_str
        })
        
    # Sort strictly by case_id
    results.sort(key=lambda x: (len(x['case_id']), x['case_id']) if x['case_id'].startswith('case_') and x['case_id'][5:].isdigit() else x['case_id'])
    # Natural sort or string sort?
    # The requirement in §6.3: "Sort rows by case_id."
    # Standard string sorting or natural sorting:
    # Let's check how deletion_requests.csv is sorted:
    # case_01, case_02, ... or natural?
    # Let's follow deletion_requests.csv ordering or standard case_id sorting.
    df_reqs_sorted = df_reqs['case_id'].tolist()
    # Sort matching input order or case_id
    results_dict = {r['case_id']: r for r in results}
    sorted_results = [results_dict[cid] for cid in df_reqs_sorted if cid in results_dict]
    
    # Write to root output.csv
    print(f"Writing {len(sorted_results)} rows to {output_path}...")
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['case_id', 'deletion_status', 'steps_json'], quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for r in sorted_results:
            writer.writerow(r)
            
    print(f"Successfully generated {output_path} with {len(sorted_results)} evaluation rows.")
    
    # Print status summary
    status_counts = pd.Series([r['deletion_status'] for r in sorted_results]).value_counts()
    print("\nPrediction Summary:")
    print(status_counts)

if __name__ == '__main__':
    main()
