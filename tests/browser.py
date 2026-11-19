"""Synthetic showcase test. Run with a local static server on port 8766."""
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
    browser=p.chromium.launch(channel='chrome',headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1100})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.route('**/*',lambda r:r.continue_() if r.request.url.startswith('http://127.0.0.1:8766/') else r.abort())
    page.goto('http://127.0.0.1:8766/');page.wait_for_load_state('networkidle')
    expect(page.locator('#module-title')).to_have_text('Overview')
    page.locator('#workspace').screenshot(path=str(ROOT/'assets/demo-preview.png'))
    page.locator('#start-tour').click()
    page.locator('[name=quantity]').fill('999')
    page.locator('#confirm-dialog').click()
    expect(page.locator('#form-error')).to_contain_text('enough units')
    page.locator('[name=quantity]').fill('2');page.locator('#confirm-dialog').click()
    expect(page.locator('#module-title')).to_have_text('Sales')
    expect(page.locator('tbody tr').first).to_contain_text('SO-1003')
    expect(page.locator('tbody tr').first).to_contain_text('$640.00')
    page.locator('[data-module=inventory]').click()
    expect(page.locator('tbody tr').first).to_contain_text('22 units')
    page.locator('#search-records').fill('no-matching-record')
    expect(page.locator('.empty')).to_be_visible()
    page.locator('[data-module=accounts]').click()
    page.locator('[data-action=payment][data-id=SO-1003]').click();page.locator('#confirm-dialog').click()
    expect(page.locator('tbody tr').first).to_contain_text('Settled')
    page.locator('[data-module=purchasing]').click();page.locator('.toolbar [data-action=purchase]').click()
    page.locator('[name=quantity]').fill('3');page.locator('#confirm-dialog').click()
    page.locator('[data-module=inventory]').click()
    expect(page.locator('tbody tr').first).to_contain_text('25 units')
    page.locator('[data-module=service]').click();page.locator('.toolbar [data-action=service]').click();page.locator('#confirm-dialog').click()
    page.locator('[data-action=complete]').first.click();page.locator('#confirm-dialog').click()
    expect(page.locator('tbody tr').first).to_contain_text('Completed')
    page.locator('#reset-demo').click();page.locator('#confirm-dialog').click()
    expect(page.locator('#module-title')).to_have_text('Overview')
    for width in [390,768,1440]:
        page.set_viewport_size({'width':width,'height':900})
        for module in ['overview','sales','purchasing','inventory','accounts','service']:
            page.locator('[data-module='+module+']').click()
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,module)
        page.locator('[data-module=overview]').click()
        page.screenshot(path='/tmp/dezhanggui-demo-'+str(width)+'.png',full_page=True)
    assert not errors,errors
    browser.close()
print('PASS showcase sale, inventory, settlement, receipt, service, validation, reset, search and responsive layouts')
