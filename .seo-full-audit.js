const { chromium } = require('/root/.openclaw/workspace/node_modules/playwright');

(async () => {
  const browser = await chromium.launch({ args: ['--no-sandbox'] });
  const page = await browser.newPage();
  
  const pages = [
    ['首页', 'https://www.sgvps.cn'],
    ['关于我们', 'https://www.sgvps.cn/about.html'],
    ['联系我们', 'https://www.sgvps.cn/contact.html'],
    ['产品服务', 'https://www.sgvps.cn/service.html'],
    ['新闻公告', 'https://www.sgvps.cn/news.html'],
    ['代理合作', 'https://www.sgvps.cn/agent.html'],
    ['帮助中心', 'https://www.sgvps.cn/help.html'],
  ];
  
  const results = [];
  
  for (const [name, url] of pages) {
    try {
      await page.goto(url, { timeout: 12000, waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(1500);
      const title = await page.title();
      const h1 = await page.$eval('h1', el => el.textContent.trim()).catch(() => '无H1');
      const desc = await page.$eval('meta[name="description"]', el => el.content.substring(0, 60)).catch(() => '无');
      const imgs = await page.$$eval('img', els => els.length);
      const noAlt = await page.$$eval('img', els => els.filter(e => !e.alt || e.alt === '').length);
      results.push({name, title, h1, desc: desc.substring(0, 50), imgs, noAlt});
    } catch(e) {
      results.push({name, url, error: e.message.substring(0, 80)});
    }
  }
  
  console.log(JSON.stringify(results, null, 2));
  await browser.close();
})().catch(e => console.log('Error:', e.message));
