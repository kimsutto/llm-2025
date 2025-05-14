// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from "vscode";
import * as path from "path";
import * as fs from "fs";

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {
  // 가장 기본적인 메시지 표시
  vscode.window.showInformationMessage("Extension activated!");

  // 웹뷰 패널 생성
  let chatPanel: vscode.WebviewPanel | undefined;

  // 채팅 열기 명령어 등록
  let openChatCommand = vscode.commands.registerCommand(
    "mx-llm-helper.openChat",
    () => {
      if (chatPanel) {
        chatPanel.reveal();
        return;
      }

      // 웹뷰 패널 생성
      chatPanel = vscode.window.createWebviewPanel(
        "mx-llm-helper.chatView",
        "LLM Chat",
        vscode.ViewColumn.Two,
        {
          enableScripts: true,
          retainContextWhenHidden: true,
        }
      );

      // HTML 내용 설정
      const htmlPath = path.join(context.extensionPath, "src", "chat.html");
      const htmlContent = fs.readFileSync(htmlPath, "utf-8");
      chatPanel.webview.html = htmlContent;

      // 패널이 닫힐 때 처리
      chatPanel.onDidDispose(
        () => {
          chatPanel = undefined;
        },
        null,
        context.subscriptions
      );

      // 웹뷰로부터 메시지 수신
      chatPanel.webview.onDidReceiveMessage(
        (message) => {
          switch (message.type) {
            case "sendMessage":
              // 여기에 실제 API 호출 로직을 추가할 수 있습니다
              console.log("Received message:", message.text);
              break;
          }
        },
        undefined,
        context.subscriptions
      );
    }
  );

  context.subscriptions.push(openChatCommand);
}

// This method is called when your extension is deactivated
export function deactivate() {
  console.log("Extension is deactivating...");
}
