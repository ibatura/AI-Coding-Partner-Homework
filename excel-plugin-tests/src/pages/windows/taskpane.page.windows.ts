import { TaskPanePage } from '../taskpane.page';

/**
 * Windows Desktop (COM/VSTO) task pane implementation.
 * Uses WinAppDriver AccessibilityId / Name locators.
 */
export class WindowsTaskPanePage extends TaskPanePage {
  async waitForPluginLoaded(): Promise<void> {
    // TODO: Replace with actual VSTO ribbon tab AccessibilityId
    await this.driver.$('~MyPluginRibbonTab').waitForExist({ timeout: 30000 });
  }

  async openTaskPane(): Promise<void> {
    const ribbonButton = await this.driver.$('~ShowTaskPaneButton');
    await ribbonButton.click();
  }

  async closeTaskPane(): Promise<void> {
    const closeButton = await this.driver.$('~TaskPaneCloseButton');
    await closeButton.click();
  }

  async isTaskPaneVisible(): Promise<boolean> {
    const taskPane = await this.driver.$('~TaskPaneContainer');
    return taskPane.isDisplayed();
  }

  async getTitle(): Promise<string> {
    const titleElement = await this.driver.$('~TaskPaneTitle');
    return titleElement.getText();
  }

  async clickButton(label: string): Promise<void> {
    const button = await this.driver.$(`[Name="${label}"]`);
    await button.click();
  }

  async getInputValue(fieldName: string): Promise<string> {
    const input = await this.driver.$(`~${fieldName}`);
    return input.getText();
  }

  async setInputValue(fieldName: string, value: string): Promise<void> {
    const input = await this.driver.$(`~${fieldName}`);
    await input.clearValue();
    await input.setValue(value);
  }
}
