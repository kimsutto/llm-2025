import * as vscode from "vscode";
import { askFile } from "./commands/askFile";

export function activate(context: vscode.ExtensionContext) {
  console.log("mx-llm-helper activated");

  // 기존 helloWorld
  context.subscriptions.push(
    vscode.commands.registerCommand("mx-llm-helper.helloWorld", () => {
      vscode.window.showInformationMessage("Hello World from mx-llm-helper!");
    })
  );

  // 새 askFile
  context.subscriptions.push(
    vscode.commands.registerCommand("mx-llm-helper.askFile", () =>
      askFile(context)
    )
  );
}

export function deactivate() {}
