// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from "vscode";
import * as path from "path";
import * as fs from "fs";

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {
  console.log("Extension activation started...");

  // 가장 기본적인 메시지 표시
  vscode.window.showInformationMessage("Extension activated!");

  // 웹뷰 패널 생성
  let chatPanel: vscode.WebviewPanel | undefined;

  // 채팅 열기 명령어 등록
  let openChatCommand = vscode.commands.registerCommand(
    "mx-llm-helper.openChat",
    () => {
      console.log("Opening chat panel...");

      if (chatPanel) {
        console.log("Chat panel already exists, revealing...");
        chatPanel.reveal();
        return;
      }

      // 웹뷰 패널 생성
      console.log("Creating new chat panel...");
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
      console.log("Loading HTML from:", htmlPath);
      const htmlContent = fs.readFileSync(htmlPath, "utf-8");
      chatPanel.webview.html = htmlContent;

      // 패널이 닫힐 때 처리
      chatPanel.onDidDispose(
        () => {
          console.log("Chat panel disposed");
          chatPanel = undefined;
        },
        null,
        context.subscriptions
      );

      // 웹뷰로부터 메시지 수신
      chatPanel.webview.onDidReceiveMessage(
        (message) => {
          console.log("Received message from webview:", message);
          switch (message.type) {
            case "sendMessage":
              console.log("Processing message:", message.text);
              // 여기에 실제 API 호출 로직을 추가할 수 있습니다

              // 웹뷰로 응답 전송
              if (chatPanel) {
                chatPanel.webview.postMessage({
                  type: "addMessage",
                  text: `Received your message: ${message.text}`,
                  isUser: false,
                });
              }
              break;
          }
        },
        undefined,
        context.subscriptions
      );
    }
  );

  context.subscriptions.push(openChatCommand);
  console.log("Extension activation completed");
}

// This method is called when your extension is deactivated
export function deactivate() {
  console.log("Extension is deactivating...");
}
