import { createTaskPanePage, getPlatform } from '../../src/helpers/driver.factory';
import type { TaskPanePage } from '../../src/pages/taskpane.page';

describe('Plugin Loading', () => {
  let taskPane: TaskPanePage;

  before(async () => {
    const platform = getPlatform();
    taskPane = await createTaskPanePage(browser, platform);
  });

  it('should load the plugin without errors', async () => {
    await taskPane.waitForPluginLoaded();
    expect(await taskPane.isTaskPaneVisible()).toBe(true);
  });

  it('should open and close the task pane', async () => {
    await taskPane.closeTaskPane();
    expect(await taskPane.isTaskPaneVisible()).toBe(false);

    await taskPane.openTaskPane();
    expect(await taskPane.isTaskPaneVisible()).toBe(true);
  });
});
