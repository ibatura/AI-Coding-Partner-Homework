/**
 * Abstract base class for cross-platform page objects.
 * Each platform (Windows/Mac/Web) provides its own implementation.
 */
export abstract class BasePage {
  constructor(protected driver: WebdriverIO.Browser) {}

  abstract waitForPluginLoaded(): Promise<void>;
  abstract openTaskPane(): Promise<void>;
  abstract closeTaskPane(): Promise<void>;
  abstract isTaskPaneVisible(): Promise<boolean>;
}
