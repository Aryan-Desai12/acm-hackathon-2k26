# DVS: Dataset Versioning System (GitLens-style)

DVS is a VS Code extension designed to bring familiar Git-like version control to text datasets. It allows data scientists to track preprocessing experiments, visualize dataset evolution, and monitor metric trends directly within their IDE.

## 🚀 Features

### 1. Dataset History Sidebar
Navigate your project's data evolution with a dedicated history view:
- **Immutable Commits:** Every dataset version is uniquely hashed based on raw data and configuration.
- **Timeline Browsing:** See a list of all versions with exact timestamps.
- **Context Actions:** Refresh history or inspect any version with a single click.

### 2. Interactive Dashboard
Visualize your data lineage and quality:
- **Version Timeline (Graph):** A visual branching graph showing how versions connect.
- **Metric Trend Charts:** Real-time visualization of `Row Count`, `Vocab Size`, and `Average Doc Length` over time.
- **Deep Comparison:** Side-by-side analysis of preprocessing configs and metric shifts.

### 3. Python-Powered Engine
- **Deterministic Hashing:** SHA-256 guarantees reproducibility.
- **Automated Metrics:** Out-of-the-box tracking of vocabulary and document statistics.
- **Configurable Preprocessing:** Support for lowercasing, deduplication, length filtering, and tokenization.

## 🛠️ Getting Started

### Prerequisites
- Python 3.8+
- Pandas

### Installation
1. Open the project in VS Code.
2. Build the extension: `npm install && npm run compile`.
3. Press `F5` to open the Extension Development Host.

### Verification (Public Dataset)
Run the built-in test suite to see DVS in action with the **SMS Spam Collection** corpus:
```bash
cd python-engine
python3 run_public_test.py
```
This will generate two versions:
1. **Raw:** The original dataset.
2. **Cleaned:** Lowercased and deduplicated.

Open the **DVS Sidebar** in VS Code to see these versions appear instantly!

## 📦 Project Structure
- `src/`: VS Code extension source code (TypeScript).
- `python-engine/`: Core versioning and diffing logic.
- `.dvs/`: Local database for commits and objects (ignored by git).
