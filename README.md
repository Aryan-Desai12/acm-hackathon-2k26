# DVS: Dataset Versioning System

DVS is a powerful VS Code extension designed to bring structured version control to text datasets. It empowers data scientists to seamlessly track preprocessing experiments, visualize dataset lineage, and monitor key metric trends—all within a unified, interactive workspace.

---

## 🛠️ Step-by-Step Local Setup

Follow these instructions to get DVS running on your machine.

### 1. Prerequisites
- **Python 3.8+**
- **Node.js 18+** & **npm**
- **VS Code**

### 2. Python Engine Setup
The engine handles the core versioning logic for your data.
```bash
# Navigate to the engine directory
cd python-engine

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install pandas
```

### 3. Run Sample Data Test
Verify the system by processing a sample dataset (SMS Spam Collection).
```bash
# Still inside python-engine
python3 run_public_test.py
```
*This script automatically downloads the dataset and generates two distinct versions: **Raw** and **Cleaned**.*

### 4. VS Code UI Setup
```bash
# Navigate back to the root directory
cd ..

# Install dependencies
npm install

# Compile the extension
npm run compile
```

---

## 🖥️ Launching the Interactive Workspace

To experience the unique DVS interface:

1.  Open the project folder in **VS Code**.
2.  Press **`F5`** (or go to `Run and Debug` → `Run Extension`).
3.  A new **[Extension Development Host]** window will appear.
4.  In the activity bar of the new window, click the **DVS icon** (History icon).
5.  Explore the **Dataset History** populated with the versions managed in Step 3.
6.  Click on any version hash to launch the **Interactive Dashboard**.

---

## 📦 Project Structure

- `src/`: VS Code extension source code (TypeScript).
- `python-engine/`: Core versioning, hashing, and diffing logic.
- `.dvs/`: Local database for commits and objects (automatically generated).
- `dist/`: Compiled extension code.

---

## 🧪 Verification
You can check the tracked history via CLI anytime:
```bash
cd python-engine
python3 core.py --history
```
