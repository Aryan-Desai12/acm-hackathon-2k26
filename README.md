# DVS: Dataset Versioning System

DVS is a VS Code extension designed to bring familiar Git-like version control to text datasets. It allows data scientists to track preprocessing experiments, visualize dataset evolution, and monitor metric trends directly within their IDE.

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
