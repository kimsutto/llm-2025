import * as vscode from "vscode";
import { showChatPanel } from "../chatPanel";

export async function askFile(context: vscode.ExtensionContext) {
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    vscode.window.showErrorMessage("No active editor");
    return;
  }

  const document = editor.document;
  const fileContent = document.getText();
  const fileName = document.fileName;

  showChatPanel(context, `질문할 파일: ${fileName}`, fileContent);
}
