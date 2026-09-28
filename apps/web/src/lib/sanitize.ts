import DOMPurify from 'dompurify'

const ALLOWED_TAGS = [
  'p', 'br', 'b', 'i', 'em', 'strong', 'u', 'ul', 'ol', 'li',
  'a', 'blockquote', 'span', 'div', 'h1', 'h2', 'h3', 'h4', 'pre', 'code',
]

let hookInstalled = false

function installHook() {
  if (hookInstalled) return
  DOMPurify.addHook('afterSanitizeAttributes', node => {
    if (node.tagName === 'A' && node.hasAttribute('href')) {
      node.setAttribute('target', '_blank')
      node.setAttribute('rel', 'noopener noreferrer')
    }
  })
  hookInstalled = true
}

/** HubSpot note and email bodies are untrusted HTML authored by customers. */
export function sanitizeHtml(value: string): string {
  installHook()
  return DOMPurify.sanitize(value, {
    ALLOWED_TAGS,
    ALLOWED_ATTR: ['href', 'title', 'target', 'rel'],
    ALLOW_DATA_ATTR: false,
  })
}

export function looksLikeHtml(value: string): boolean {
  return /<[a-z][\s\S]*>/i.test(value)
}
