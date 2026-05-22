import DOMPurify from 'dompurify';

export function sanitizeHtml(dirty) {
  if (!dirty) return '';
  return DOMPurify.sanitize(String(dirty), {
    ALLOWED_TAGS: [
      'b', 'i', 'em', 'strong', 'a', 'p', 'br', 'ul', 'ol', 'li',
      'span', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'img', 'table', 'thead', 'tbody', 'tr', 'td', 'th',
      'blockquote', 'pre', 'code', 's', 'strike', 'u',
      'sub', 'sup', 'hr'
    ],
    ALLOWED_ATTR: [
      'href', 'target', 'src', 'alt', 'title', 'class', 'style',
      'width', 'height', 'align', 'valign', 'colspan', 'rowspan'
    ]
  });
}
