import { TaskPanePage } from '../pages/taskpane.page';

export type Platform = 'windows' | 'mac' | 'web';

/**
 * Returns the current platform from the TEST_PLATFORM env var.
 */
export function getPlatform(): Platform {
  const platform = process.env.TEST_PLATFORM;
  if (platform !== 'windows' && platform !== 'mac' && platform !== 'web') {
    throw new Error(
      `Invalid TEST_PLATFORM "${platform}". Must be one of: windows, mac, web`
    );
  }
  return platform;
}

/**
 * Factory placeholder — implementations will be registered per platform.
 * Extend this once platform-specific page objects are built.
 */
export async function createTaskPanePage(
  driver: WebdriverIO.Browser,
  platform: Platform
): Promise<TaskPanePage> {
  switch (platform) {
    case 'windows': {
      const { WindowsTaskPanePage } = await import('../pages/windows/taskpane.page.windows');
      return new WindowsTaskPanePage(driver);
    }
    case 'mac': {
      const { MacTaskPanePage } = await import('../pages/mac/taskpane.page.mac');
      return new MacTaskPanePage(driver);
    }
    case 'web': {
      const { WebTaskPanePage } = await import('../pages/web/taskpane.page.web');
      return new WebTaskPanePage(driver);
    }
  }
}
