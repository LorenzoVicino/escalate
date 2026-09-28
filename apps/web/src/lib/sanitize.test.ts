import { looksLikeHtml, sanitizeHtml } from './sanitize'

test('strips script tags and inline event handlers', () => {
  expect(sanitizeHtml('<p>ok</p><script>alert(1)</script>')).toBe('<p>ok</p>')
  expect(sanitizeHtml('<img src=x onerror="alert(1)">')).not.toContain('onerror')
  expect(sanitizeHtml('<div onclick="steal()">hi</div>')).toBe('<div>hi</div>')
})

test('keeps basic formatting and hardens links', () => {
  expect(sanitizeHtml('<p>Hello <strong>world</strong></p>')).toBe('<p>Hello <strong>world</strong></p>')
  const link = sanitizeHtml('<a href="https://example.com">x</a>')
  expect(link).toContain('target="_blank"')
  expect(link).toContain('rel="noopener noreferrer"')
})

test('detects html versus plain text', () => {
  expect(looksLikeHtml('<p>hi</p>')).toBe(true)
  expect(looksLikeHtml('centralina non comunica')).toBe(false)
})
