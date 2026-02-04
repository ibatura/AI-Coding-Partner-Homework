import { TaskPanePage } from '../taskpane.page';

/**
 * Office 365 Web task pane implementation.
 * Handles iframe switching for the Excel Online add-in.
 */
export class WebTaskPanePage extends TaskPanePage {
  private async switchToAddinIframe(): Promise<void> {
    // Switch back to default content first
    await this.driver.switchToFrame(null);
    // TODO: Replace selector with actual add-in iframe title/id
    const frame = await this.driver.$('iframe[title="My Add-in"]');
    await this.driver.switchToFrame(frame);
  }

  private async switchToDefaultContent(): Promise<void> {
    await this.driver.switchToFrame(null);
  }

  async waitForPluginLoaded(): Promise<void> {
    await this.switchToAddinIframe();
    await this.driver
      .$('#taskpane-root')
      .waitForExist({ timeout: 15000 });
  }

  async openTaskPane(): Promise<void> {
    await this.switchToDefaultContent();
    // TODO: Replace with actual ribbon/toolbar button selector in Excel Online
    const insertTab = await this.driver.$('[data-automation-id="ribbon-tab-insert"]');
    await insertTab.click();
    const addinButton = await this.driver.$('[data-automation-id="my-addin-button"]');
    await addinButton.click();
    await this.switchToAddinIframe();
  }

  async closeTaskPane(): Promise<void> {
    await this.switchToDefaultContent();
    const closeButton = await this.driver.$('[data-automation-id="taskpane-close"]');
    await closeButton.click();
  }

  async isTaskPaneVisible(): Promise<boolean> {
    try {
      await this.switchToAddinIframe();
      const root = await this.driver.$('#taskpane-root');
      return root.isDisplayed();
    } catch {
      return false;
    }
  }

  async getTitle(): Promise<string> {
    await this.switchToAddinIframe();
    const title = await this.driver.$('#taskpane-title');
    return title.getText();
  }

  async clickButton(label: string): Promise<void> {
    await this.switchToAddinIframe();
    const button = await this.driver.$(`button=${label}`);
    await button.click();
  }

  async getInputValue(fieldName: string): Promise<string> {
    await this.switchToAddinIframe();
    const input = await this.driver.$(`[name="${fieldName}"]`);
    return input.getValue();
  }

  async setInputValue(fieldName: string, value: string): Promise<void> {
    await this.switchToAddinIframe();
    const input = await this.driver.$(`[name="${fieldName}"]`);
    await input.clearValue();
    await input.setValue(value);
  }
}
