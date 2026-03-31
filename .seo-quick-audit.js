const { chromium } = require('/root/.openclaw/workspace/node_modules/playwright');

(async () => {
  const browser = await chromium.launch({ args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  const page = await browser.newPage();
  page.setDefaultTimeout(8000);
  
  const urls = [
    ['首页', 'https://www.sgvps.cn'],
    ['关于', 'https://www.sgvps.cn/about.html'],
    ['联系', 'https://www.sgvps.cn/contact.html'],
    ['产品', 'https://www.sgvps.cn/service.html'],
    ['新闻', 'https://www.sgvps.cn/news.html'],
  ];
  
  for (const [name, url] of urls) {
    try {
      await page.goto(url, { waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(1000);
      const title = await page.title();
      const h1 = await page.$eval('h1', el => el.textContent.trim()).catch(() => '-');
      const imgs = await page.$$eval('img', els => els.length);
      const noAlt = await page.$$eval('img', els => els.filter(e => !e.alt).length);
      process.stdout.write(`✅ ${name}: "${title}" H1:${h1} | 图:${imgs} 无Alt:${noAlt}\n`);
    } catch(e) {
      process.stdout.write(`❌ ${name}: ${e.message.substring(0,60)}\n`);
    }
  }
  
  await browser.close();
  process.stdout.write('Done\n');
})().catch(e => { console.error('Fatal:', e.message); process.exit(1); });
