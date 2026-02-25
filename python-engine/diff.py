import os
import json
import argparse
from typing import Any, Dict

COMMITS_DIR = ".dvs/commits"

def load_commit(version_hash: str) -> Dict[str, Any]:
    with open(os.path.join(COMMITS_DIR, f"{version_hash}.json"), 'r') as f:
        return json.load(f)

def generate_diff(hash_a: str, hash_b: str) -> Dict[str, Any]:
    """Highlights differences in settings, data size, and metrics."""
    commit_a = load_commit(hash_a)
    commit_b = load_commit(hash_b)
    
    diff_report: Dict[str, Any] = {
        "versions": {"old": hash_a, "new": hash_b},
        "data_diff": {
            "row_count_change": int(commit_b["row_count"]) - int(commit_a["row_count"])
        },
        "config_diff": {},
        "metric_diff": {},
        "explanation": "" 
    }
    
    # Compare configs
    all_keys = set(commit_a["config"].keys()).union(commit_b["config"].keys())
    for k in all_keys:
        val_a = commit_a["config"].get(k)
        val_b = commit_b["config"].get(k)
        if val_a != val_b:
            diff_report["config_diff"][k] = {"from": val_a, "to": val_b}
            
    # Compare metrics
    metrics_a = commit_a.get("metrics", {})
    metrics_b = commit_b.get("metrics", {})
    all_metrics = set(metrics_a.keys()).union(metrics_b.keys())
    
    for m in all_metrics:
        val_a = metrics_a.get(m, 0)
        val_b = metrics_b.get(m, 0)
        if val_a != val_b:
            diff_report["metric_diff"][m] = {
                "old": val_a, 
                "new": val_b,
                "change": float(val_b) - float(val_a) if isinstance(val_a, (int, float)) else None
            }

    # Generate explanations
    explanations = []
    row_diff = diff_report["data_diff"]["row_count_change"]
    if row_diff != 0:
        reason = "preprocessing" if diff_report["config_diff"] else "raw data changes"
        explanations.append(f"Dataset size changed by {row_diff} rows due to {reason}.")
    
    if diff_report["config_diff"].get("deduplicate") == {"from": False, "to": True}:
        explanations.append("Deduplication was enabled, likely reducing row count.")
        
    if "vocab_size" in diff_report["metric_diff"]:
        v_diff = diff_report["metric_diff"]["vocab_size"]["change"]
        if v_diff is not None:
            explanations.append(f"Vocabulary size {'increased' if v_diff > 0 else 'decreased'} by {abs(v_diff)} tokens.")

    diff_report["explanation"] = " ".join(explanations) if explanations else "No significant changes detected."

    return diff_report

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--v1", required=True)
    parser.add_argument("--v2", required=True)
    args = parser.parse_args()
    
    print(json.dumps(generate_diff(args.v1, args.v2), indent=2))