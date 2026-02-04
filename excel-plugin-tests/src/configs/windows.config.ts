export const windowsCaps: WebdriverIO.Capabilities = {
  platformName: 'Windows',
  'appium:automationName': 'Windows',
  'appium:app': process.env.WIN_EXCEL_PATH
    || 'C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE',
  'appium:createSessionTimeout': 30000,
  'appium:newCommandTimeout': 60,
};
