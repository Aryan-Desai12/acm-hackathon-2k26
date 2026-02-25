import os
import json
import hashlib
import time
from typing import Any, Dict
import pandas as pd

DVS_DIR = ".dvs"
OBJECTS_DIR = os.path.join(DVS_DIR, "objects")
COMMITS_DIR = os.path.join(DVS_DIR, "commits")

def init_dvs():
    """Initializes the filesystem storage."""
    os.makedirs(OBJECTS_DIR, exist_ok=True)
    os.makedirs(COMMITS_DIR, exist_ok=True)

def preprocess_data(df: pd.DataFrame, text_col: str, config: dict) -> pd.DataFrame:
    """Applies configurable preprocessing using only Pandas."""
    processed = df.copy()
    
    if config.get("lowercase", False):
        processed[text_col] = processed[text_col].str.lower()
        
    if config.get("deduplicate", False):
        processed = processed.drop_duplicates(subset=[text_col])
        
    if config.get("filter_short", False):
        min_len = config.get("min_length", 3)
        processed = processed[processed[text_col].str.len() >= min_len]

    if config.get("tokenize", False):
        # Minimalist whitespace tokenization
        processed[text_col] = processed[text_col].apply(lambda x: str(x).split() if pd.notnull(x) else [])
        
    return processed

def calculate_metrics(df: pd.DataFrame, text_col: str) -> Dict[str, Any]:
    """Calculates automated metrics for the text dataset."""
    metrics: Dict[str, Any] = {
        "row_count": len(df),
    }
    
    if len(df) == 0:
        metrics.update({"avg_doc_length": 0, "vocab_size": 0})
        return metrics

    # Check if tokenized
    first_val = df[text_col].iloc[0]
    if isinstance(first_val, list):
        all_tokens = [token for sublist in df[text_col] for token in sublist]
        metrics["avg_doc_length"] = float(sum(len(s) for s in df[text_col]) / len(df))
    else:
        all_tokens = [token for text in df[text_col].astype(str) for token in text.split()]
        metrics["avg_doc_length"] = float(df[text_col].astype(str).str.len().mean())

    metrics["vocab_size"] = len(set(all_tokens))
    return metrics

def compute_hash(raw_filepath: str, config: dict) -> str:
    """Computes SHA-256 hash from raw data bytes and config."""
    hasher = hashlib.sha256()
    
    # 1. Hash the deterministic JSON string of the config
    config_str = json.dumps(config, sort_keys=True)
    hasher.update(config_str.encode('utf-8'))
    
    # 2. Hash the raw data bytes
    with open(raw_filepath, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
            
    return hasher.hexdigest()

def commit_dataset(raw_filepath: str, text_col: str, config: dict, user_metrics: dict = None):
    """Creates an immutable version of the dataset."""
    user_metrics = user_metrics or {}
    init_dvs()
    
    # Generate unique version ID
    version_hash = compute_hash(raw_filepath, config)
    
    # Load and Preprocess
    df = pd.read_csv(raw_filepath)
    processed_df = preprocess_data(df, text_col, config)
    
    # Calculate automated metrics
    metrics = calculate_metrics(processed_df, text_col)
    if user_metrics:
        metrics.update(user_metrics)
    
    # Save immutable artifact
    artifact_path = os.path.join(OBJECTS_DIR, f"{version_hash}.csv")
    if not os.path.exists(artifact_path):
        processed_df.to_csv(artifact_path, index=False)
    
    # Save commit metadata
    commit_data: Dict[str, Any] = {
        "version_id": version_hash,
        "parent_id": get_head(),
        "timestamp": float(time.time()),
        "config": config,
        "metrics": metrics,
        "row_count": metrics["row_count"]
    }
    
    with open(os.path.join(COMMITS_DIR, f"{version_hash}.json"), 'w') as f:
        json.dump(commit_data, f, indent=4)
        
    set_head(version_hash)
    return version_hash

def get_head():
    head_path = os.path.join(DVS_DIR, "HEAD")
    return open(head_path).read().strip() if os.path.exists(head_path) else None

def set_head(version_hash):
    with open(os.path.join(DVS_DIR, "HEAD"), 'w') as f:
        f.write(version_hash)

def get_history():
    """Returns a list of all commits sorted by timestamp."""
    init_dvs()
    commits = []
    if not os.path.exists(COMMITS_DIR):
        return []
    for filename in sorted(os.listdir(COMMITS_DIR)):
        if filename.endswith(".json"):
            with open(os.path.join(COMMITS_DIR, filename), 'r') as f:
                commits.append(json.load(f))
    
    # Sort by timestamp (newest first)
    return sorted(commits, key=lambda x: x.get("timestamp", 0), reverse=True)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--history":
        import json as json_lib
        print(json_lib.dumps(get_history(), indent=2))