const puppeteer = require('puppeteer');

const fs = require('fs');
import { Browser } from 'puppeteer';

const url = 'https://www.youtube.com/watch?v=OOtxXPaQvoM';

const main = async () => {
    const browser: Browser = await puppeteer.launch({ headless: false, timeout:0, executablePath: '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser' });
    const page = await browser.newPage();
  await page.goto(url);

  
  // Cookie
  //await page.click("#content > div.body.style-scope.ytd-consent-bump-v2-lightbox > div.eom-buttons.style-scope.ytd-consent-bump-v2-lightbox > div:nth-child(1) > ytd-button-renderer:nth-child(1) > yt-button-shape")
  
  // Ad
   
  await page.waitForSelector('.ytp-caption-segment');
  const button = await page.evaluate('document.querySelector("button.ytp-subtitles-button").getAttribute("aria-pressed")');
  
  
  


  if(button === 'false'){
    await page.click('.ytp-subtitles-button');
  }
  

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

    setTimeout(captureAndSaveWord, 2000);
  };

  captureAndSaveWord();
};

main();
