const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const outDir = path.resolve(__dirname, 'kanban-test-output');
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir);

  const headlessEnv = (process.env.HEADLESS || 'true').toLowerCase();
  const headless = headlessEnv === 'true' || headlessEnv === '1' || headlessEnv === 'yes';
  const browser = await chromium.launch({ headless });
  const page = await browser.newPage();

  const logs = [];
  page.on('console', msg => logs.push(`${msg.type()}: ${msg.text()}`));
  page.on('pageerror', err => logs.push(`pageerror: ${err.message}`));

  const base = 'http://127.0.0.1:5000';
  await page.goto(base, { waitUntil: 'domcontentloaded' });

  // Helper to test a module by providing a button selector and section selector
  async function testModule(name, btnSelector, sectionSelector) {
    console.log(`\n=== Testing ${name} ===`);
    try {
      // Open Administrativo if not already
      await page.click('[data-page="administrativo"]');
      await page.waitForTimeout(400);

      // Click module access button
      await page.click(btnSelector);
      await page.waitForSelector(sectionSelector, { timeout: 3000 });
      const section = await page.$(sectionSelector);
      if (!section) throw new Error(`Section ${sectionSelector} not found`);

      // Add card: click first .btn-add-card inside section
      const addBtn = await section.$('.btn-add-card');
      if (!addBtn) throw new Error('.btn-add-card not found in section');
      await addBtn.click();

      // Wait modal
      const modal = await page.waitForSelector('.modal-overlay', { timeout: 3000 });
      const titleInput = modal.locator('input[type="text"]').first();
      await titleInput.fill(`${name} - teste automático`);
      const textarea = modal.locator('textarea').first();
      await textarea.fill('Criado automaticamente pelo teste Playwright');
      const select = modal.locator('select').first();
      try { await select.selectOption('priority-medium'); } catch (e) { /* ignore if not present */ }
      // fill second text input if present (responsible)
      const secondText = modal.locator('input[type="text"]').nth(1);
      try { await secondText.fill('Automação'); } catch (e) { /* ignore */ }

      // Save
      await modal.locator('text=Adicionar Card').click();
      await page.waitForTimeout(500);

      // Screenshot after add
      await page.screenshot({ path: path.join(outDir, `${name.replace(/\s+/g,'_')}-after-add.png`) });

      // Move card: drag first card in first column to second column (if exists)
      const firstColumn = section.locator('.kanban-column').first();
      const secondColumn = section.locator('.kanban-column').nth(1);
      const card = firstColumn.locator('.kanban-card').first();
      const target = secondColumn.locator('.kanban-cards').first();
      if (await card.count() > 0 && await target.count() > 0) {
        try {
          await card.dragTo(target);
          await page.waitForTimeout(400);
        } catch (err) {
          logs.push(`drag error (${name}): ${err.message}`);
        }
      }

      // Screenshot after move
      await page.screenshot({ path: path.join(outDir, `${name.replace(/\s+/g,'_')}-after-move.png`) });

      // Delete the moved card: find any .btn-card-delete in section and click first
      const deleteBtn = section.locator('.btn-card-delete').first();
      if (await deleteBtn.count() > 0) {
        await deleteBtn.click();
        // Confirm dialog: accept
        try {
          await page.on('dialog', async dialog => { await dialog.accept(); });
        } catch (e) {}
        await page.waitForTimeout(300);
      }

      // Save localStorage snapshot
      const local = await page.evaluate(() => JSON.stringify(localStorage));
      fs.writeFileSync(path.join(outDir, `${name.replace(/\s+/g,'_')}-localstorage.json`), local);

      // Screenshot final
      await page.screenshot({ path: path.join(outDir, `${name.replace(/\s+/g,'_')}-final.png`) });

      // Back to Administrativo
      await page.click('#btn-back-' + (name.toLowerCase().split(' ')[0]) ).catch(()=>{});
      await page.waitForTimeout(300);

      console.log(`Finished ${name}`);
    } catch (err) {
      console.error(`Error testing ${name}:`, err.message);
      logs.push(`error testing ${name}: ${err.message}`);
    }
  }

  // Modules to test: names and selectors
  const modules = [
    { name: 'Comercial', btn: '.btn-acessar-comercial', section: '#comercial' },
    { name: 'Área Médica', btn: '.btn-acessar-area-medica', section: '#area-medica' },
    { name: 'Financeiro', btn: '.btn-acessar-financeiro', section: '#financeiro' },
    { name: 'Judicial', btn: '.btn-acessar-judicial', section: '#judicial' },
    { name: 'Importação', btn: '.btn-acessar-importacao', section: '#importacao' },
    { name: 'IA', btn: '.btn-acessar-ia', section: '#ia' }
  ];

  // Also test Painel directly (it is the default page)
  try {
    console.log('\n=== Testing Painel ===');
    await page.waitForSelector('#painel');
    const painel = await page.$('#painel');
    const painelFirstAdd = painel.locator('.btn-add-card').first();
    await painelFirstAdd.click();
    const modal = await page.waitForSelector('.modal-overlay', { timeout: 3000 });
    await modal.locator('input[type="text"]').first().fill('Painel - teste automático');
    await modal.locator('textarea').first().fill('Teste automatizado no Painel');
    await modal.locator('text=Adicionar Card').click();
    await page.screenshot({ path: path.join(outDir, `Painel-after-add.png`) });
    // move
    const painelSection = page.locator('#painel');
    const firstCol = painelSection.locator('.kanban-column').first();
    const secondCol = painelSection.locator('.kanban-column').nth(1);
    const card = firstCol.locator('.kanban-card').first();
    if (await card.count() > 0 && await secondCol.count() > 0) {
      try { await card.dragTo(secondCol.locator('.kanban-cards')); } catch(e){ logs.push('painel drag error: '+e.message) }
    }
    await page.screenshot({ path: path.join(outDir, `Painel-after-move.png`) });
    // save localStorage
    fs.writeFileSync(path.join(outDir, `Painel-localstorage.json`), await page.evaluate(() => JSON.stringify(localStorage)));
  } catch (err) {
    logs.push('Painel test error: ' + err.message);
  }

  for (const m of modules) {
    await testModule(m.name, m.btn, m.section);
  }

  // Write logs
  fs.writeFileSync(path.join(outDir, 'console-log.txt'), logs.join('\n'));

  console.log('\nAll done. Outputs saved in:', outDir);
  await browser.close();
})();
