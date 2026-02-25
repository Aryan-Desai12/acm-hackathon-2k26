import * as vscode from "vscode";
import { execFile } from "child_process";
import * as path from "path";
import * as fs from "fs";

/* ============================================================
   ACTIVATE
============================================================ */

export function activate(context: vscode.ExtensionContext) {
  const commitProvider = new DvsCommitProvider();
  vscode.window.registerTreeDataProvider("dvsHistory", commitProvider);

  context.subscriptions.push(
    vscode.commands.registerCommand("dvs.refreshHistory", () =>
      commitProvider.refresh(),
    ),

    // 🔥 FIXED: Inspect reloads fresh commit from engine
    vscode.commands.registerCommand(
      "dvs.inspectCommit",
      async (item: DvsCommitItem) => {
        const workspaceRoot = getWorkspaceRoot();
        if (!workspaceRoot) return;

        const engine = resolveEngine(workspaceRoot);
        if (!engine) return;

        execFile(
          engine.python,
          [engine.core, "--history"],
          { cwd: workspaceRoot },
          (error, stdout) => {
            if (error) return;

            try {
              const history = JSON.parse(stdout);
              history.sort((a: any, b: any) => a.timestamp - b.timestamp);

              const commit = history.find(
                (c: any) => c.version_id === item.commit.version_id,
              );

              showDashboard(commit || null);
            } catch {}
          },
        );
      },
    ),

    vscode.commands.registerCommand("dvs.openDashboard", () => {
      showDashboard(null);
    }),

    vscode.commands.registerCommand("dvs.compareVersions", async () => {
      const workspaceRoot = getWorkspaceRoot();
      if (!workspaceRoot) return;

      const engine = resolveEngine(workspaceRoot);
      if (!engine) {
        vscode.window.showErrorMessage("DVS engine not found.");
        return;
      }

      const hashA = await vscode.window.showInputBox({ prompt: "Hash A" });
      const hashB = await vscode.window.showInputBox({ prompt: "Hash B" });
      if (!hashA || !hashB) return;

      execFile(
        engine.python,
        [engine.diff, "--v1", hashA, "--v2", hashB],
        { cwd: workspaceRoot },
        (error, stdout, stderr) => {
          if (error) {
            vscode.window.showErrorMessage(stderr || error.message);
            return;
          }

          try {
            const diffData = JSON.parse(stdout);
            showDiffWebview(diffData);
          } catch {
            vscode.window.showErrorMessage("Invalid diff JSON.");
          }
        },
      );
    }),
  );
}

/* ============================================================
   HELPERS
============================================================ */

function getWorkspaceRoot(): string | null {
  const folders = vscode.workspace.workspaceFolders;
  if (!folders) {
    vscode.window.showErrorMessage("Open a workspace folder first.");
    return null;
  }
  return folders[0].uri.fsPath;
}

function resolveEngine(workspaceRoot: string) {
  const candidates = [workspaceRoot, path.join(workspaceRoot, "python-engine")];

  for (const root of candidates) {
    const core = path.join(root, "core.py");
    const diff = path.join(root, "diff.py");

    const python =
      process.platform === "win32"
        ? path.join(root, ".venv", "Scripts", "python.exe")
        : path.join(root, ".venv", "bin", "python3");

    if (fs.existsSync(core) && fs.existsSync(diff) && fs.existsSync(python)) {
      return { root, core, diff, python };
    }
  }

  return null;
}

/* ============================================================
   TREE ITEM
============================================================ */

class DvsCommitItem extends vscode.TreeItem {
  constructor(public readonly commit: any) {
    super(
      commit.version_id.substring(0, 7),
      vscode.TreeItemCollapsibleState.None,
    );

    this.description = new Date(commit.timestamp * 1000).toLocaleString();
    this.tooltip = `Hash: ${commit.version_id}\nRows: ${commit.row_count}`;
    this.contextValue = "commit";
    this.iconPath = new vscode.ThemeIcon("git-commit");
  }
}

/* ============================================================
   TREE PROVIDER
============================================================ */

class DvsCommitProvider implements vscode.TreeDataProvider<DvsCommitItem> {
  private _onDidChangeTreeData = new vscode.EventEmitter<void>();
  readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

  refresh() {
    this._onDidChangeTreeData.fire();
  }

  getTreeItem(element: DvsCommitItem): vscode.TreeItem {
    return element;
  }

  async getChildren(): Promise<DvsCommitItem[]> {
    const workspaceRoot = getWorkspaceRoot();
    if (!workspaceRoot) return [];

    const engine = resolveEngine(workspaceRoot);
    if (!engine) return [];

    return new Promise((resolve) => {
      execFile(
        engine.python,
        [engine.core, "--history"],
        { cwd: workspaceRoot },
        (error, stdout) => {
          if (error) {
            resolve([]);
            return;
          }

          try {
            const history = JSON.parse(stdout);
            history.sort((a: any, b: any) => a.timestamp - b.timestamp);
            resolve(history.map((c: any) => new DvsCommitItem(c)));
          } catch {
            resolve([]);
          }
        },
      );
    });
  }
}

/* ============================================================
   DASHBOARD
============================================================ */

function showDashboard(selectedCommit: any) {
  const panel = vscode.window.createWebviewPanel(
    "dvsDashboard",
    "DVS Dashboard",
    vscode.ViewColumn.One,
    { enableScripts: true },
  );

  const workspaceRoot = getWorkspaceRoot();
  if (!workspaceRoot) return;

  const engine = resolveEngine(workspaceRoot);
  if (!engine) return;

  execFile(
    engine.python,
    [engine.core, "--history"],
    { cwd: workspaceRoot },
    (error, stdout) => {
      let history: any[] = [];

      if (!error) {
        try {
          history = JSON.parse(stdout);
          history.sort((a: any, b: any) => a.timestamp - b.timestamp);
        } catch {}
      }

      panel.webview.html = getDashboardHtml(history, selectedCommit);
    },
  );
}

/* ============================================================
   DASHBOARD HTML
============================================================ */

function getDashboardHtml(history: any[], selectedCommit: any) {
  let mermaidGraph = "graph LR\n";

  history.forEach((c) => {
    if (c.parent_id) {
      mermaidGraph += `  ${c.parent_id.substring(0, 7)} --> ${c.version_id.substring(0, 7)}\n`;
    } else {
      mermaidGraph += `  ${c.version_id.substring(0, 7)}\n`;
    }
  });

  // Brighter arrows
  mermaidGraph += `linkStyle default stroke:#00eaff,stroke-width:2.5px;\n`;

  return `
<!DOCTYPE html>
<html>
<head>
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
body { font-family: var(--vscode-font-family); padding: 20px; }
.card { padding: 15px; border: 1px solid var(--vscode-widget-border); border-radius: 8px; margin-bottom: 20px; }
</style>
</head>
<body>

<h1>DVS Dashboard</h1>

<div class="card">
<h2>Version Timeline</h2>
<pre class="mermaid">${mermaidGraph}</pre>
</div>

<div class="card">
<h2>Metric Trends</h2>
<canvas id="metricsChart"></canvas>
</div>

${
  selectedCommit
    ? `<div class="card">
<h2>Instance Inspect</h2>
<pre>${JSON.stringify(selectedCommit, null, 2)}</pre>
</div>`
    : ""
}

<script>
mermaid.initialize({ startOnLoad: true });

const history = ${JSON.stringify(history)};
const ctx = document.getElementById('metricsChart').getContext('2d');

new Chart(ctx, {
  type: 'line',
  data: {
    labels: history.map(h => h.version_id.substring(0,7)),
    datasets: [
      {
        label: 'Row Count',
        data: history.map(h => h.row_count ?? 0),
        borderColor: '#4caf50',
        yAxisID: 'yRows',
        fill: false
      },
      {
        label: 'Vocab Size',
        data: history.map(h => h.metrics?.vocab_size ?? 0),
        borderColor: '#2196f3',
        yAxisID: 'yVocab',
        fill: false
      }
    ]
  },
  options: {
    responsive: true,
    interaction: { mode: 'index', intersect: false },
    scales: {
      yRows: {
        type: 'linear',
        position: 'left',
        title: { display: true, text: 'Row Count' }
      },
      yVocab: {
        type: 'linear',
        position: 'right',
        grid: { drawOnChartArea: false },
        title: { display: true, text: 'Vocab Size' }
      }
    }
  }
});
</script>

</body>
</html>
`;
}

/* ============================================================
   DIFF VIEW
============================================================ */

function showDiffWebview(diffData: any) {
  const panel = vscode.window.createWebviewPanel(
    "dvsDiff",
    "Dataset Diff",
    vscode.ViewColumn.One,
    { enableScripts: true },
  );

  panel.webview.html = `
<!DOCTYPE html>
<html>
<body>
<h2>Dataset Version Comparison</h2>
<pre>${JSON.stringify(diffData, null, 2)}</pre>
</body>
</html>
`;
}
