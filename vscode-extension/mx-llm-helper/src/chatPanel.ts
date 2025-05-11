import * as vscode from "vscode";
import * as path from "path";

export function showChatPanel(
  context: vscode.ExtensionContext,
  title: string,
  initialCode: string
) {
  const panel = vscode.window.createWebviewPanel(
    "llmChat",
    "LLM Chat",
    vscode.ViewColumn.Beside,
    {
      enableScripts: true,
      localResourceRoots: [
        vscode.Uri.file(path.join(context.extensionPath, "media")),
      ],
    }
  );

  const webviewPath = vscode.Uri.file(
    path.join(context.extensionPath, "media", "webview.html")
  );

  const html = require("fs").readFileSync(webviewPath.fsPath, "utf8");
  panel.webview.html = html;

  // 초기 메시지 전송
  panel.webview.onDidReceiveMessage(async (message) => {
    if (message.type === "ask") {
      const res = await fetch("http://localhost:8000/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: message.question,
          top_k: 3,
        }),
      });
      const data = await res.json();
      panel.webview.postMessage({ type: "answer", data });
    }
  });

  // 웹뷰에 초기 코드 전송
  panel.webview.postMessage({
    type: "init",
    payload: {
      file: title,
      content: initialCode,
    },
  });
}
