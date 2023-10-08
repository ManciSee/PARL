const puppeteer = require('puppeteer');
const fs = require('fs');
import { Browser } from 'puppeteer';

const url = 'https://www.youtube.com/watch?v=OOtxXPaQvoM';

const main = async () => {
    const browser: Browser = await puppeteer.launch({ headless: false, executablePath: '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser' });
    const page = await browser.newPage();
  await page.goto(url);

  await page.waitForSelector('.ytp-caption-segment');


  const captureAndSaveWord = async () => {
    const data = await page.$eval(
      '.ytp-caption-window-container .caption-window .captions-text .caption-visual-line .ytp-caption-segment',
      (el) => (el as HTMLElement).innerText
    );
    console.log(data);

    
    fs.appendFile('transcript.json', JSON.stringify(data) + '\n', (err: any) => {
      if (err) throw err;
      console.log('ok');
    });

    setTimeout(captureAndSaveWord, 3000);
  };

  captureAndSaveWord();
};

main();
