export const webCaps: WebdriverIO.Capabilities = {
  browserName: process.env.O365_BROWSER || 'chrome',
  'goog:chromeOptions': {
    args: ['--start-maximized', '--disable-notifications'],
  },
};
