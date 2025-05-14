// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from "vscode";
import * as path from "path";
import * as fs from "fs";
import { ApiService } from "./api";

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {
  console.log("Extension activation started...");

  // API 서비스 초기화
  const apiService = new ApiService("http://localhost:3000"); // API 서버 URL을 적절히 수정하세요

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
        async (message) => {
          console.log("Received message from webview:", message);
          switch (message.type) {
            case "sendMessage":
              console.log("Processing message:", message.text);
              try {
                // API 호출
                const response = await apiService.search(message.text);
                console.log("API response:", response);

                // 웹뷰로 응답 전송
                if (chatPanel) {
                  if (response.status === "ok") {
                    // 결과를 문자열로 변환
                    const resultsText = response.results
                      .map((result) => JSON.stringify(result, null, 2))
                      .join("\n\n");

                    chatPanel.webview.postMessage({
                      type: "addMessage",
                      text: `검색 결과:\n\`\`\`\n${resultsText}\n\`\`\``,
                      isUser: false,
                    });
                  } else {
                    chatPanel.webview.postMessage({
                      type: "addMessage",
                      text: "죄송합니다. 검색 중 오류가 발생했습니다.",
                      isUser: false,
                    });
                  }
                }
              } catch (error) {
                console.error("Error processing message:", error);
                if (chatPanel) {
                  chatPanel.webview.postMessage({
                    type: "addMessage",
                    text: "죄송합니다. 요청을 처리하는 중 오류가 발생했습니다.",
                    isUser: false,
                  });
                }
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
