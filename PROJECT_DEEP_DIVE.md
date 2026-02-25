# 🧠 PROJECT DEEP DIVE: Dataset Versioning System (DVS)

This document provides a technical explanation of the DVS project, its architecture, and key design decisions. Use this to prepare for college placements and hackathons.

---

## 🚀 1. What is DVS?
Data scientists often experiment with different preprocessing steps (e.g., lowercasing, removing stopwords). Frequently, they lose track of which preprocessing config produced which dataset. **DVS (Dataset Versioning System)** fixes this by treating datasets like code. It provides an immutable, Git-like history for your data.

## 🏗️ 2. High-Level Architecture
DVS consists of two main layers:
1.  **The Engine (Python):** Handles the "heavy lifting"—data manipulation, hashing, and metric calculation using Pandas.
2.  **The UI (TypeScript/VS Code):** Provides a GitLens-style interface to browse history, see timelines, and compare versions visually.

## 🧪 3. Core Logic & Implementation Details

### A. The Hashing Strategy (SHA-256)
*   **Why it's important:** In placements, you might be asked, "How do you ensure data integrity?"
*   **Implementation:** We generate a unique `version_id` by hashing both the **raw bytes** of the source CSV and the **JSON configuration** of the preprocessing steps.
*   **Significance:** This ensures that same data + same steps = same ID. If you change a single character in the data or one boolean in the config, the ID changes. This is called **Content-Addressable Storage**.

### B. Immutable Versioning
*   **Implementation:** Once a version is hashed, the resulting processed data is saved in `.dvs/objects/<hash>.csv`.
*   **Design Decision:** We never overwrite files. Each version is a "snapshot," ensuring that your results are 100% reproducible today, tomorrow, or in a month.

### C. Automated Metrics
*   **Implementation:** For every commit, DVS automatically calculates:
    - **Row Count:** Number of records.
    - **Vocab Size:** Number of unique tokens (words).
    - **Avg Doc Length:** Average length of text entries.
*   **Why implementation?** This allows us to track "Accuracy Changes" or "Data Shape Changes" over time. If a preprocessing step accidentally deletes 50% of your data, you'll see a sharp drop in the "Row Count" chart.

## 🖥️ 4. Visualizing the Evolution (The UI)
We implemented three GitLens-inspired components:
1.  **Sidebar TreeView:** Shows a list of all versions (commits) sorted by timestamp.
2.  **Mermaid.js Timeline:** A graph visualization inside VS Code that shows the lineage (which version came from which parent).
3.  **Chart.js Trends:** Line charts that show how your dataset's metrics (like Row Count) evolved over time.

---

## 🎓 Interview & Hackathon Prep Q&A

**Q: Why use content-addressable storage (hashing) instead of simple incremental IDs?**
*   **A:** Incremental IDs (v1, v2) don't prove what's inside the file. Hashing creates a "digital fingerprint." If the data changes, the ID changes. This allows for deduplication (if two people create the same version, we only store one file) and ensures reproducibility.

**Q: How does the Python engine communicate with the VS Code extension?**
*   **A:** The TypeScript extension uses the `child_process.exec` module to run the Python scripts as CLI commands. The Python engine then outputs JSON to `stdout`, which the extension parses and renders in the Webview.

**Q: What was the biggest challenge in the UI?**
*   **A:** Implementing a dynamic dashboard using Webviews. Since VS Code's Webviews are isolated (like a tab in a browser), we had to ensure they could correctly load external libraries like Mermaid.js and Chart.js from CDNs to render complex graphs and charts.

**Q: How would you scale this for Big Data?**
*   **A:** Currently, we store full CSV snapshots. For Big Data, we would move to a **Parquet** format (columnar storage) for faster I/O and use "Delta Hashing" (storing only the changes between versions) instead of full snapshots to save space.
