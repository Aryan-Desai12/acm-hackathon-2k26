import os
import sys

# Ensure we can import the DVS core
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core import commit_dataset

# 1. PATH TO YOUR NEW CSV
# Replace 'public_dataset.csv' with the name of your modified file
csv_path = "public_dataset.csv"
# 2. YOUR PREPROCESSING CONFIG
# This is where you record what cleaning you did to the file
config = {
    "lowercase": True,
    "deduplicate": False,
    "custom_cleaning": "Manual row removal",  # You can add custom notes here!
}
# 3. YOUR ACCURACY METRIC
# If you trained a model on this change, put the score here
accuracy = 0.95
print(f"Committing custom version: {csv_path}...")
new_hash = commit_dataset(
    raw_filepath=csv_path,
    text_col="text",  # Ensure this matches your column name
    config=config,
    user_metrics={"accuracy": accuracy},
)
print(f"\nSUCCESS! New Version Hash: {new_hash}")
print("Now go to VS Code and click the Refresh button to see your change!")
