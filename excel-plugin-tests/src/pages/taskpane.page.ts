import { BasePage } from './base.page';

/**
 * Abstract task pane page object.
 * Platform implementations handle locator differences.
 */
export abstract class TaskPanePage extends BasePage {
  abstract getTitle(): Promise<string>;
  abstract clickButton(label: string): Promise<void>;
  abstract getInputValue(fieldName: string): Promise<string>;
  abstract setInputValue(fieldName: string, value: string): Promise<void>;
}
