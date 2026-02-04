# Excel Plugin Cross-Platform Test Automation Plan

## TypeScript/Node.js + Appium

---

## 1. Current Situation

| Platform        | Technology   | Host OS       | Excel Version        |
|-----------------|-------------|---------------|----------------------|
| Windows Desktop | COM/VSTO C# | Windows 10/11 | Excel Desktop (Win)  |
| Mac Desktop     | JS/TS       | macOS         | Excel Desktop (Mac)  |
| Office 365 Web  | JS/TS       | Any           | Excel Online (Browser)|

**Constraint:** One person writes all tests, so everything must stay in **one language: TypeScript**.

---

## 2. Architecture Overview

```
excel-plugin-tests/
├── src/
│   ├── pages/                  # Page Object Models (shared abstraction)
│   │   ├── base.page.ts        # Abstract base page with common interface
│   │   ├── ribbon.page.ts      # Ribbon/toolbar interactions
│   │   ├── taskpane.page.ts    # Task pane interactions
│   │   └── dialog.page.ts      # Dialog/modal interactions
│   ├── helpers/
│   │   ├── driver.factory.ts   # Creates correct driver per platform
│   │   ├── excel.helpers.ts    # Excel-specific utilities (open workbook, etc.)
│   │   ├── wait.helpers.ts     # Custom wait/retry logic
│   │   └── data.helpers.ts     # Test data generation
│   ├── configs/
│   │   ├── windows.config.ts   # Appium caps for Windows Desktop
│   │   ├── mac.config.ts       # Appium caps for Mac Desktop
│   │   └── web.config.ts       # WebDriver/Appium caps for browser
│   └── fixtures/
│       ├── test-workbooks/     # .xlsx files for test scenarios
│       └── expected-results/   # Expected output snapshots
├── tests/
│   ├── shared/                 # Tests that run on ALL platforms
│   │   ├── plugin-load.spec.ts
│   │   ├── taskpane.spec.ts
│   │   └── basic-operations.spec.ts
│   ├── windows/                # Windows-only tests (COM/VSTO specific)
│   │   └── ribbon-com.spec.ts
│   ├── mac/                    # Mac-only tests
│   │   └── mac-specific.spec.ts
│   └── web/                    # Office 365 web-only tests
│       └── browser-specific.spec.ts
├── docs/
│   └── PLAN.md                 # This file
├── package.json
├── tsconfig.json
├── wdio.conf.ts                # Base WebdriverIO config
├── wdio.windows.conf.ts        # Windows overrides
├── wdio.mac.conf.ts            # Mac overrides
├── wdio.web.conf.ts            # Web/browser overrides
└── .env.example                # Environment variables template
```

---

## 3. Technology Stack

| Component           | Tool                        | Rationale                                                       |
|---------------------|-----------------------------|-----------------------------------------------------------------|
| Language            | **TypeScript**              | Single language requirement; shared with Mac/Web plugin codebases |
| Test Runner         | **WebdriverIO (wdio)**      | First-class TypeScript support, Appium integration, multi-driver |
| Windows Automation  | **Appium + WinAppDriver**   | Automates Win32/WPF/UWP — handles COM/VSTO Excel + plugin UI    |
| Mac Automation      | **Appium + Mac2Driver**     | Automates native macOS apps via XCTest under the hood            |
| Web Automation      | **WebdriverIO + Selenium**  | Standard browser automation for Office 365 Online                |
| Assertions          | **expect-webdriverio**      | Built into wdio, async-native matchers                           |
| Reporting           | **Allure Reporter**         | Unified HTML reports with screenshots, cross-platform view       |
| CI/CD               | **GitHub Actions**          | Matrix strategy for parallel platform runs                       |

---

## 4. Platform-Specific Driver Setup

### 4.1 Windows Desktop (COM/VSTO Plugin)

**Driver:** Appium + `appium-windows-driver` (WinAppDriver)

**Prerequisites:**
- Windows 10/11 machine (physical or VM)
- WinAppDriver installed (`winappdriver.exe`)
- Appium Server 2.x with `appium-windows-driver`
- Excel Desktop installed with the COM/VSTO plugin registered

**Desired Capabilities:**
```typescript
// configs/windows.config.ts
export const windowsCaps = {
  platformName: 'Windows',
  'appium:automationName': 'Windows',
  'appium:app': 'C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE',
  'appium:appArguments': '/e "C:\\test-data\\test-workbook.xlsx"',
  'appium:createSessionTimeout': 30000,
  'appium:newCommandTimeout': 60,
};
```

**Key challenges & solutions:**
- **Plugin ribbon tab detection:** Use `AccessibilityId` or `Name` locators to find custom ribbon buttons added by the VSTO add-in.
- **COM dialog windows:** WinAppDriver can switch between window handles — use `driver.getWindowHandles()` to attach to plugin dialogs.
- **VSTO load timing:** Add explicit waits for the plugin's ribbon tab to appear after Excel starts. The VSTO add-in may take several seconds to initialize.

### 4.2 Mac Desktop (JS/TS Plugin)

**Driver:** Appium + `appium-mac2-driver`

**Prerequisites:**
- macOS machine (physical or VM with Xcode)
- Appium Server 2.x with `appium-mac2-driver`
- Excel for Mac installed with the JS add-in sideloaded

**Desired Capabilities:**
```typescript
// configs/mac.config.ts
export const macCaps = {
  platformName: 'mac',
  'appium:automationName': 'Mac2',
  'appium:bundleId': 'com.microsoft.Excel',
  'appium:arguments': ['--args', '/path/to/test-workbook.xlsx'],
  'appium:showServerLogs': true,
  'appium:newCommandTimeout': 60,
};
```

**Key challenges & solutions:**
- **Accessibility tree:** Use Accessibility Inspector (Xcode) to discover element identifiers. Mac2Driver uses XCTest accessibility queries.
- **Task pane as WebView:** The JS plugin's task pane is rendered in a WebView. Use `driver.getContexts()` to switch between NATIVE_APP and WEBVIEW contexts.
- **Sideloading the add-in:** Automate or script the manifest sideload step before test runs via a `beforeSession` hook.

### 4.3 Office 365 Web (JS/TS Plugin — Browser)

**Driver:** WebdriverIO with standard browser drivers (ChromeDriver / GeckoDriver)

**Prerequisites:**
- Appium or direct Selenium/WebDriver
- Browser installed (Chrome recommended)
- Office 365 account with the add-in installed/sideloaded

**Desired Capabilities:**
```typescript
// configs/web.config.ts
export const webCaps = {
  browserName: 'chrome',
  'goog:chromeOptions': {
    args: ['--start-maximized', '--disable-notifications'],
  },
};
```

**Key challenges & solutions:**
- **Authentication:** Office 365 requires Microsoft login. Options:
  - Use saved browser profile with cached credentials.
  - Automate OAuth login flow as a `before` hook (handle MFA via test account with app password).
  - Use Playwright's `storageState` approach adapted for wdio: save cookies/localStorage after manual login, restore before tests.
- **iframes:** The Excel Online editor and the add-in task pane live in nested iframes. Use `driver.switchToFrame()` to navigate to the correct context.
- **Add-in sideloading in browser:** Script the sideload via the "Insert > Office Add-ins > Upload My Add-in" flow, or use a centrally deployed add-in for the test tenant.

---

## 5. Page Object Model — Cross-Platform Abstraction

The core idea: define an **interface** for each UI component, then implement platform-specific versions.

```typescript
// src/pages/base.page.ts
export abstract class BasePage {
  constructor(protected driver: WebdriverIO.Browser) {}

  abstract waitForPluginLoaded(): Promise<void>;
  abstract openTaskPane(): Promise<void>;
  abstract closeTaskPane(): Promise<void>;
  abstract isTaskPaneVisible(): Promise<boolean>;
}
```

```typescript
// src/pages/taskpane.page.ts
export abstract class TaskPanePage extends BasePage {
  abstract getTitle(): Promise<string>;
  abstract clickButton(label: string): Promise<void>;
  abstract getInputValue(fieldName: string): Promise<string>;
  abstract setInputValue(fieldName: string, value: string): Promise<void>;
}
```

Platform-specific implementations:

```typescript
// src/pages/windows/taskpane.page.windows.ts
export class WindowsTaskPanePage extends TaskPanePage {
  async waitForPluginLoaded(): Promise<void> {
    // WinAppDriver: wait for VSTO ribbon tab by AccessibilityId
    await this.driver.$('~MyPluginRibbonTab').waitForExist({ timeout: 30000 });
  }
  // ...
}
```

```typescript
// src/pages/web/taskpane.page.web.ts
export class WebTaskPanePage extends TaskPanePage {
  async waitForPluginLoaded(): Promise<void> {
    // Switch to add-in iframe, wait for task pane root element
    const frame = await this.driver.$('iframe[title="My Add-in"]');
    await this.driver.switchToFrame(frame);
    await this.driver.$('#taskpane-root').waitForExist({ timeout: 15000 });
  }
  // ...
}
```

A **factory** resolves the correct implementation at runtime:

```typescript
// src/helpers/driver.factory.ts
export function createTaskPanePage(
  driver: WebdriverIO.Browser,
  platform: 'windows' | 'mac' | 'web'
): TaskPanePage {
  switch (platform) {
    case 'windows': return new WindowsTaskPanePage(driver);
    case 'mac':     return new MacTaskPanePage(driver);
    case 'web':     return new WebTaskPanePage(driver);
  }
}
```

---

## 6. Shared Tests (Write Once, Run Everywhere)

```typescript
// tests/shared/plugin-load.spec.ts
import { createTaskPanePage } from '../../src/helpers/driver.factory';

const platform = process.env.TEST_PLATFORM as 'windows' | 'mac' | 'web';

describe('Plugin Loading', () => {
  let taskPane: TaskPanePage;

  before(async () => {
    taskPane = createTaskPanePage(browser, platform);
  });

  it('should load the plugin without errors', async () => {
    await taskPane.waitForPluginLoaded();
    expect(await taskPane.isTaskPaneVisible()).toBe(true);
  });

  it('should display the correct task pane title', async () => {
    const title = await taskPane.getTitle();
    expect(title).toBe('My Excel Plugin');
  });
});
```

**How it works:** The same `.spec.ts` file runs on all three platforms. The `TEST_PLATFORM` env var selects the correct page object implementation. Platform-specific tests go in `tests/windows/`, `tests/mac/`, or `tests/web/`.

---

## 7. WebdriverIO Configuration

```typescript
// wdio.conf.ts (base)
export const config: WebdriverIO.Config = {
  runner: 'local',
  framework: 'mocha',
  mochaOpts: { timeout: 120000, ui: 'bdd' },
  reporters: [
    'spec',
    ['allure', { outputDir: 'allure-results', disableWebdriverStepsReporting: false }],
  ],
  logLevel: 'info',
  waitforTimeout: 10000,
  connectionRetryTimeout: 120000,
  connectionRetryCount: 3,
  afterTest: async function (test, context, { error }) {
    if (error) {
      await browser.saveScreenshot(`./screenshots/${test.title}.png`);
    }
  },
};
```

```typescript
// wdio.windows.conf.ts
import { config as baseConfig } from './wdio.conf';
import { windowsCaps } from './src/configs/windows.config';

export const config = {
  ...baseConfig,
  capabilities: [windowsCaps],
  specs: ['./tests/shared/**/*.spec.ts', './tests/windows/**/*.spec.ts'],
  services: [['appium', { command: 'appium', args: ['--relaxed-security'] }]],
};
```

```typescript
// wdio.mac.conf.ts
import { config as baseConfig } from './wdio.conf';
import { macCaps } from './src/configs/mac.config';

export const config = {
  ...baseConfig,
  capabilities: [macCaps],
  specs: ['./tests/shared/**/*.spec.ts', './tests/mac/**/*.spec.ts'],
  services: [['appium', { command: 'appium', args: ['--relaxed-security'] }]],
};
```

```typescript
// wdio.web.conf.ts
import { config as baseConfig } from './wdio.conf';
import { webCaps } from './src/configs/web.config';

export const config = {
  ...baseConfig,
  capabilities: [webCaps],
  specs: ['./tests/shared/**/*.spec.ts', './tests/web/**/*.spec.ts'],
  baseUrl: 'https://www.office.com',
};
```

---

## 8. Implementation Phases

### Phase 1: Project Setup & Infrastructure

- [ ] Initialize Node.js project with TypeScript
- [ ] Install dependencies: `webdriverio`, `@wdio/cli`, `@wdio/mocha-framework`, `@wdio/appium-service`, `appium`, `typescript`, `ts-node`, `allure-commandline`
- [ ] Configure `tsconfig.json` for strict mode
- [ ] Create base wdio configs for all three platforms
- [ ] Set up npm scripts: `test:windows`, `test:mac`, `test:web`, `test:all`
- [ ] Create `.env.example` with required environment variables
- [ ] Verify Appium server starts and connects on one platform

### Phase 2: Windows Desktop Tests (COM/VSTO)

- [ ] Set up WinAppDriver on test machine
- [ ] Use Accessibility Insights / inspect.exe to map plugin UI elements
- [ ] Implement `WindowsTaskPanePage` and `WindowsRibbonPage`
- [ ] Write first test: Excel launches, plugin loads, ribbon tab visible
- [ ] Write tests: open task pane, interact with plugin UI, verify results in cells
- [ ] Handle VSTO-specific scenarios: plugin enable/disable, COM error dialogs

### Phase 3: Mac Desktop Tests

- [ ] Set up Appium + Mac2Driver on macOS machine
- [ ] Use Accessibility Inspector to map Excel for Mac UI elements
- [ ] Implement `MacTaskPanePage` — handle WebView context switching
- [ ] Write first test: Excel launches, add-in loads, task pane opens
- [ ] Write tests: interact with add-in task pane, verify Excel data
- [ ] Handle macOS-specific: permissions dialogs, Gatekeeper prompts

### Phase 4: Office 365 Web Tests

- [ ] Set up WebdriverIO with ChromeDriver
- [ ] Solve authentication (cookie replay or automated login)
- [ ] Map iframe structure: Excel Online canvas, add-in task pane iframe
- [ ] Implement `WebTaskPanePage` with iframe switching
- [ ] Write first test: navigate to Excel Online, open workbook, load add-in
- [ ] Write tests: full add-in interaction through the browser
- [ ] Handle web-specific: network latency waits, session expiry

### Phase 5: Shared Test Suite & Reporting

- [ ] Identify and extract all common test scenarios into `tests/shared/`
- [ ] Ensure shared tests pass on all three platforms
- [ ] Configure Allure reporting with platform tags
- [ ] Add screenshot-on-failure for all platforms
- [ ] Write test data generators in `src/fixtures/`

### Phase 6: CI/CD Integration

- [ ] GitHub Actions workflow with platform matrix
- [ ] Windows runner for Windows Desktop tests
- [ ] macOS runner for Mac Desktop tests
- [ ] Ubuntu/Chrome runner for Web tests
- [ ] Allure report publishing as GitHub Pages or artifacts
- [ ] Slack/Teams notification on failure

---

## 9. NPM Scripts

```json
{
  "scripts": {
    "test:windows": "cross-env TEST_PLATFORM=windows wdio run wdio.windows.conf.ts",
    "test:mac": "cross-env TEST_PLATFORM=mac wdio run wdio.mac.conf.ts",
    "test:web": "cross-env TEST_PLATFORM=web wdio run wdio.web.conf.ts",
    "test:all": "npm run test:windows && npm run test:mac && npm run test:web",
    "report:generate": "allure generate allure-results --clean -o allure-report",
    "report:open": "allure open allure-report",
    "lint": "eslint src/ tests/ --ext .ts",
    "typecheck": "tsc --noEmit"
  }
}
```

---

## 10. Key Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| WinAppDriver is archived / no longer maintained | Windows tests may break on newer OS | Monitor community forks; consider switching to Appium Windows Driver v2 |
| Mac2Driver accessibility tree is sparse | Hard to locate elements | Supplement with AppleScript via `driver.executeScript('macos: appleScript', ...)` |
| Office 365 frequent UI changes | Web tests become flaky | Use data-testid selectors where possible; keep locators in page objects for single-point updates |
| Microsoft login MFA blocks automation | Web tests can't authenticate | Use test tenant with app passwords or security defaults disabled for test accounts |
| Cross-platform element timing differences | Flaky tests | Use explicit waits in page objects, never hard-coded sleeps; tune per platform |
| Single person maintaining all tests | Bus factor = 1 | Keep code simple, well-documented, and heavily typed; the Page Object pattern limits blast radius of changes |

---

## 11. Environment Variables (.env)

```
# Platform selection
TEST_PLATFORM=windows|mac|web

# Windows
WIN_EXCEL_PATH=C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE
WIN_APPIUM_HOST=127.0.0.1
WIN_APPIUM_PORT=4723

# Mac
MAC_APPIUM_HOST=127.0.0.1
MAC_APPIUM_PORT=4723

# Web / Office 365
O365_BASE_URL=https://www.office.com
O365_USERNAME=test@contoso.com
O365_PASSWORD=<from-secret-manager>
O365_BROWSER=chrome

# Reporting
ALLURE_RESULTS_DIR=allure-results
SCREENSHOT_ON_FAILURE=true
```

---

## 12. Estimated Test Coverage Matrix

| Test Area                  | Windows | Mac | Web | Location              |
|---------------------------|---------|-----|-----|-----------------------|
| Plugin loads successfully  | x       | x   | x   | tests/shared/         |
| Task pane opens/closes     | x       | x   | x   | tests/shared/         |
| Plugin UI interactions     | x       | x   | x   | tests/shared/         |
| Data written to cells      | x       | x   | x   | tests/shared/         |
| Ribbon/toolbar buttons     | x       | x   | x   | tests/shared/         |
| COM-specific dialogs       | x       |     |     | tests/windows/        |
| VSTO enable/disable        | x       |     |     | tests/windows/        |
| macOS permissions          |         | x   |     | tests/mac/            |
| WebView context switching  |         | x   |     | tests/mac/            |
| O365 authentication        |         |     | x   | tests/web/            |
| iframe navigation          |         |     | x   | tests/web/            |
| Session/cookie handling    |         |     | x   | tests/web/            |
