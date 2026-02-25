# 🏁 Getting Started: Running the DVS Project

Follow these steps to set up the environment, run the Python engine on a sample dataset, and visualize the results in VS Code.

## Step 1: Python Environment Setup
1.  Open your terminal and navigate to the `python-engine` directory:
    ```bash
    cd python-engine
    ```
2.  Create a virtual environment:
    ```bash
    python3 -m venv venv
    ```
3.  Activate the environment:
    ```bash
    source venv/bin/activate
    ```
4.  Install the required dependencies:
    ```bash
    pip install pandas
    ```

## Step 2: Running the Sample Test
1.  Execute the public test script which downloads the **SMS Spam Collection** dataset and creates two versions:
    ```bash
    python3 run_public_test.py
    ```
    - **Expected Output:** You will see the hashes for "Version A (Raw)" and "Version B (Cleaned)".
2.  Verify the history is tracked in the CLI:
    ```bash
    python3 core.py --history
    ```

## Step 3: Setting Up the VS Code Extension
1.  Navigate back to the root directory (one level up):
    ```bash
    cd ..
    ```
2.  Install Node.js dependencies:
    ```bash
    npm install
    ```
3.  Compile the extension:
    ```bash
    npm run compile
    ```

## Step 4: Visualizing the GitLens-style UI
1.  Press **`F5`** in VS Code. This opens a new window called the **[Extension Development Host]**.
2.  In that new window, click on the **DVS icon** (History icon) in the Activity Bar (the far-left sidebar).
3.  You will see the **Dataset History** with the versions you created in Step 2.
4.  Click on any version to open the **DVS Dashboard** and see the Timeline and Metric Trends!
