import { TaskPanePage } from '../taskpane.page';

/**
 * Mac Desktop task pane implementation.
 * Uses Mac2Driver with WebView context switching for the JS add-in.
 */
export class MacTaskPanePage extends TaskPanePage {
  private async switchToWebViewContext(): Promise<void> {
    const contexts = await this.driver.getContexts();
    const webview = contexts.find((ctx: string) =>
      ctx.toLowerCase().includes('webview')
    );
    if (webview) {
      await this.driver.switchContext(webview as string);
    }
  }

  private async switchToNativeContext(): Promise<void> {
    await this.driver.switchContext('NATIVE_APP');
  }

  async waitForPluginLoaded(): Promise<void> {
    // Wait for Excel to finish launching and add-in to load
    // TODO: Replace with actual accessibility identifier
    await this.driver
      .$('~com.microsoft.Excel.addin.taskpane')
      .waitForExist({ timeout: 30000 });
  }

  async openTaskPane(): Promise<void> {
    await this.switchToNativeContext();
    // TODO: Replace with actual menu/ribbon selector for Mac
    const menuItem = await this.driver.$('~ShowTaskPaneMenuItem');
    await menuItem.click();
    await this.switchToWebViewContext();
  }

  async closeTaskPane(): Promise<void> {
    await this.switchToNativeContext();
    const closeButton = await this.driver.$('~TaskPaneCloseButton');
    await closeButton.click();
  }

  async isTaskPaneVisible(): Promise<boolean> {
    try {
      await this.switchToWebViewContext();
      const root = await this.driver.$('#taskpane-root');
      return root.isDisplayed();
    } catch {
      return false;
    }
  }

  async getTitle(): Promise<string> {
    await this.switchToWebViewContext();
    const title = await this.driver.$('#taskpane-title');
    return title.getText();
  }

  async clickButton(label: string): Promise<void> {
    await this.switchToWebViewContext();
    const button = await this.driver.$(`button=${label}`);
    await button.click();
  }

  async getInputValue(fieldName: string): Promise<string> {
    await this.switchToWebViewContext();
    const input = await this.driver.$(`[name="${fieldName}"]`);
    return input.getValue();
  }

  async setInputValue(fieldName: string, value: string): Promise<void> {
    await this.switchToWebViewContext();
    const input = await this.driver.$(`[name="${fieldName}"]`);
    await input.clearValue();
    await input.setValue(value);
  }
}
