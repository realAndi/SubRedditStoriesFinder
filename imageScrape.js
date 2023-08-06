const playwright = require('playwright');
const path = require('path');

(async () => {
  const browser = await playwright.chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  const htmlFilePath = process.argv[2]; // Get the 'post.html' file path from command line arguments
  await page.goto(`file://${htmlFilePath}`);

  const element = await page.$('.post-container'); // Select the element

  // Wait for a specific amount of time before taking the screenshot
  // The value is in milliseconds, so 3000 means 3 seconds
  await page.waitForTimeout(3000);

  // Create the screenshot file path
  const screenshotFilePath = path.join(path.dirname(htmlFilePath), 'title_card.png');
  
  await element.screenshot({ path: screenshotFilePath }); // Take the screenshot

  console.log(`Screenshot taken!!`); // Log the action to the console
  
  await browser.close();
})();
