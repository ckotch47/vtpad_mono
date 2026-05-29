#!/usr/bin/env node
import fs from 'node:fs'
import path from 'node:path'
import { chromium } from 'playwright'

const BASE_URL = process.env.BASE_URL || 'http://localhost:5173'
const LOGIN = process.env.LOGIN || 'test@test.ts'
const PASSWORD = process.env.PASSWORD || 'QxGtS2bVK0KHlLYj'
const SPACE_ID = process.env.SPACE_ID || '7c14114e-d2a8-42f4-ab40-5d6ac7a5d1b4'
const OUT_DIR = path.resolve('playwright-ui-regression')

fs.mkdirSync(OUT_DIR, { recursive: true })

const results = []

function addResult(name, ok, details = '') {
  results.push({ name, ok, details })
}

async function take(page, name) {
  await page.screenshot({ path: path.join(OUT_DIR, `${name}.png`), fullPage: true })
}

async function safeGoto(page, url, attempts = 3) {
  let lastErr = null
  for (let i = 0; i < attempts; i++) {
    try {
      await page.goto(url, { waitUntil: 'domcontentloaded' })
      return
    } catch (err) {
      lastErr = err
      await page.waitForTimeout(350)
    }
  }
  throw lastErr
}

async function expectVisible(page, selector, name) {
  const ok = await page.locator(selector).first().isVisible().catch(() => false)
  addResult(name, ok, ok ? 'visible' : `missing: ${selector}`)
  return ok
}

async function run() {
  const browser = await chromium.launch({ headless: true })
  const page = await browser.newPage({ viewport: { width: 1920, height: 1200 } })
  const networkErrors = []

  page.on('response', (r) => {
    if (r.status() >= 400 && !r.url().includes('favicon')) {
      networkErrors.push(`${r.status()} ${r.url()}`)
    }
  })

  try {
    await safeGoto(page, `${BASE_URL}/auth`)
    await page.fill('input[placeholder="Email address"]', LOGIN)
    await page.fill('input[placeholder="Enter your password"]', PASSWORD)
    await page.click('button:has-text("LOG IN")')
    await page.waitForURL('**/space', { timeout: 15000 })
    addResult('Auth login', true, page.url())
    await take(page, '01-space-home')

    await safeGoto(page, `${BASE_URL}/space/${SPACE_ID}/test-cases?page=1&page_size=25`)
    await page.waitForTimeout(1200)
    const tcRows = await page.locator('tbody tr').count()
    addResult('Test Cases list loads', tcRows > 0, `rows=${tcRows}`)
    await take(page, '02-test-cases-list')

    if (tcRows > 0) {
      const caseLink = await page.locator('a[href*="/test-cases/"]').first().getAttribute('href').catch(() => null)
      if (caseLink) {
        await safeGoto(page, `${BASE_URL}${caseLink}`)
      } else {
        await page.locator('tbody tr td').nth(1).click().catch(() => {})
      }
      await page.waitForTimeout(1400)
      const okDetail = /\/test-cases\/[^/?]+/.test(page.url())
      addResult('Test Case detail opens', okDetail, page.url())
      await expectVisible(page, 'text=Details', 'Test Case detail: Details tab')
      await expectVisible(page, 'text=Run History', 'Test Case detail: Run History tab')
      await expectVisible(page, 'text=Info', 'Test Case detail: Info card')
      await take(page, '03-test-case-detail')
    }

    await safeGoto(page, `${BASE_URL}/space/${SPACE_ID}/test-runs`)
    await page.waitForTimeout(1200)
    const trRows = await page.locator('tbody tr').count()
    addResult('Test Runs list loads', trRows > 0, `rows=${trRows}`)
    await take(page, '04-test-runs-list')

    if (trRows > 0) {
      await page.locator('tbody tr').first().click()
      await page.waitForURL(new RegExp(`/space/${SPACE_ID}/test-runs/[^/?]+`), { timeout: 5000 }).catch(() => {})
      await page.waitForTimeout(300)
      addResult('Test Run detail opens', /\/test-runs\/[^/?]+/.test(page.url()), page.url())
      await take(page, '05-test-run-detail')
    }

    await safeGoto(page, `${BASE_URL}/space/${SPACE_ID}/test-plans`)
    await page.waitForTimeout(1200)
    const tpRows = await page.locator('tbody tr').count()
    addResult('Test Plans list loads', tpRows > 0, `rows=${tpRows}`)
    await take(page, '06-test-plans-list')

    if (tpRows > 0) {
      await page.locator('tbody tr').first().click()
      await page.waitForTimeout(1200)
      addResult('Test Plan detail opens', /\/test-plans\/.+/.test(page.url()), page.url())
      await take(page, '07-test-plan-detail')
    }

    await safeGoto(page, `${BASE_URL}/space/${SPACE_ID}/test-suites`)
    await page.waitForTimeout(1200)
    const tsRows = await page.locator('tbody tr').count()
    addResult('Test Suites list loads', tsRows > 0, `rows=${tsRows}`)
    await take(page, '08-test-suites-list')

    if (tsRows > 0) {
      await page.locator('tbody tr').first().click()
      await page.waitForURL(new RegExp(`/space/${SPACE_ID}/test-suites/[^/?]+`), { timeout: 5000 }).catch(() => {})
      await page.waitForTimeout(300)
      addResult('Test Suite detail opens', /\/test-suites\/[^/?]+/.test(page.url()), page.url())
      await take(page, '09-test-suite-detail')
    }

    await safeGoto(page, `${BASE_URL}/space/${SPACE_ID}/tech-docs`)
    await page.waitForTimeout(1400)
    const docsCount = await page.locator('.tech-doc-list-item').count()
    addResult('Tech Docs tree loads', docsCount > 0, `items=${docsCount}`)
    await take(page, '10-tech-docs')

    if (docsCount > 0) {
      await page.locator('.tech-doc-list-item').first().click()
      await page.waitForTimeout(1000)
      const editVisible =
        await page.locator('button:has(i[class*="mdi-pencil"]), button:has(i[class*="mdi-square-edit-outline"])').first().isVisible().catch(() => false)
      addResult('Tech Doc: Edit action visible', editVisible, editVisible ? 'visible' : 'missing edit icon button')
      await take(page, '11-tech-doc-detail')
    }

    // Basic typography consistency check (no extreme jumps in body text)
    await safeGoto(page, `${BASE_URL}/space/${SPACE_ID}/test-cases`)
    await page.waitForTimeout(1000)
    const sizeStats = await page.evaluate(() => {
      const selectors = ['.v-card-text', '.v-list-item-title', '.v-list-item-subtitle', '.v-btn']
      const samples = []
      for (const sel of selectors) {
        const el = document.querySelector(sel)
        if (!el) continue
        const fontSize = Number.parseFloat(getComputedStyle(el).fontSize)
        if (!Number.isNaN(fontSize)) samples.push({ sel, fontSize })
      }
      return samples
    })
    const bad = sizeStats.filter((s) => s.fontSize < 12 || s.fontSize > 20)
    addResult('Typography sanity check', bad.length === 0, JSON.stringify(sizeStats))

    const uniqErrors = [...new Set(networkErrors)]
    addResult('Network errors', uniqErrors.length === 0, uniqErrors.slice(0, 10).join(' | '))
  } finally {
    await browser.close()
  }
}

await run()

const passed = results.filter((r) => r.ok).length
const failed = results.length - passed

const report = {
  baseUrl: BASE_URL,
  spaceId: SPACE_ID,
  passed,
  failed,
  results,
  generatedAt: new Date().toISOString(),
}

fs.writeFileSync(path.join(OUT_DIR, 'report.json'), JSON.stringify(report, null, 2))

for (const r of results) {
  const mark = r.ok ? 'PASS' : 'FAIL'
  console.log(`${mark} - ${r.name}${r.details ? ` :: ${r.details}` : ''}`)
}
console.log(`\\nSummary: ${passed} passed, ${failed} failed`)

process.exit(failed > 0 ? 1 : 0)
