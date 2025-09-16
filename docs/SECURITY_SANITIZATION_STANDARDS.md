# 🔒 Security Sanitization Standards - Anclora PDF2EPUB Frontend

## 📋 Overview

This document establishes the security standards for HTML sanitization in the Anclora PDF2EPUB frontend application. All developers must follow these guidelines to prevent XSS attacks and maintain application security.

**Last Updated:** January 15, 2025  
**Status:** ✅ ACTIVE  
**Compliance:** MANDATORY

---

## 🛡️ Security Policy

### ❌ **NEVER USE**
- Raw `dangerouslySetInnerHTML` without sanitization
- `innerHTML`, `outerHTML` directly
- `eval()`, `Function()` constructor
- `setTimeout`/`setInterval` with string parameters
- User input directly in DOM without validation

### ✅ **ALWAYS USE**
- Sanitization utilities from `src/utils/sanitize.ts`
- `createSafeHTML()` wrapper for `dangerouslySetInnerHTML`
- TypeScript types for all sanitization functions
- Comprehensive testing for XSS vectors

---

## 🔧 Implementation Standards

### 1. **Sanitization Utilities Location**
```
src/utils/sanitize.ts - Main sanitization utilities
src/utils/sanitize.test.ts - Comprehensive test suite
```

### 2. **Available Functions**

#### **`sanitizePreviewContent(html: string): string`**
- **Use Case:** PDF preview content with mathematical expressions
- **Security Level:** Medium - allows mathematical markup
- **Configuration:** `PREVIEW_SANITIZE_CONFIG`

```typescript
// ✅ CORRECT
const safeContent = sanitizePreviewContent(rawHtmlFromPDF);
```

#### **`sanitizeUserContent(html: string): string`**
- **Use Case:** User-generated content (comments, descriptions)
- **Security Level:** High - very restrictive
- **Configuration:** `STRICT_SANITIZE_CONFIG`

```typescript
// ✅ CORRECT
const safeUserContent = sanitizeUserContent(userInput);
```

#### **`createSafeHTML(html: string, strict?: boolean): { __html: string }`**
- **Use Case:** Direct use with `dangerouslySetInnerHTML`
- **Security Level:** Configurable (preview or strict)
- **Performance:** Includes performance monitoring

```typescript
// ✅ CORRECT
<div dangerouslySetInnerHTML={createSafeHTML(content)} />

// ✅ CORRECT (strict mode)
<div dangerouslySetInnerHTML={createSafeHTML(userContent, true)} />
```

### 3. **Configuration Details**

#### **Preview Configuration (Medium Security)**
```typescript
ALLOWED_TAGS: [
  // Document structure
  'p', 'div', 'span', 'br', 'hr',
  'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
  'ul', 'ol', 'li',
  'table', 'thead', 'tbody', 'tr', 'td', 'th',
  
  // Text formatting
  'strong', 'em', 'u', 'i', 'b', 'sub', 'sup',
  
  // Images and media
  'img', 'figure', 'figcaption',
  
  // Mathematical expressions (KaTeX/MathJax)
  'math', 'semantics', 'mrow', 'msup', 'msub', 'mfrac', 'msqrt',
  'mroot', 'mtext', 'mn', 'mo', 'mi', 'mspace', 'mover', 'munder',
  'munderover', 'mmultiscripts', 'mtable', 'mtr', 'mtd',
  
  // SVG for diagrams
  'svg', 'g', 'path', 'circle', 'rect', 'line', 'polyline', 'polygon',
  'text', 'tspan', 'defs', 'use',
]
```

#### **Strict Configuration (High Security)**
```typescript
ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'u', 'i', 'b']
ALLOWED_ATTR: ['class']
```

### 4. **CSS Injection Prevention**

The system includes advanced CSS injection protection:

```typescript
// Automatically blocked patterns:
- javascript:
- expression()
- behavior:
- moz-binding:
- @import
- url() with dangerous content
```

---

## 🧪 Testing Requirements

### 1. **Mandatory Test Coverage**
- ✅ Basic XSS payloads (script injection)
- ✅ Event handler injection (onclick, onerror, etc.)
- ✅ CSS injection (javascript: in styles)
- ✅ URL injection (javascript: protocols)
- ✅ Mathematical content preservation
- ✅ SVG content safety
- ✅ Performance with large content

### 2. **Test Locations**
```
src/utils/sanitize.test.ts - Unit tests (38 tests)
src/components/PreviewModal.simple.test.tsx - Integration tests (5 tests)
```

### 3. **Running Tests**
```bash
# Run sanitization tests
npm test -- sanitize.test.ts

# Run integration tests
npm test -- PreviewModal.simple.test.tsx

# Run all tests
npm test
```

---

## 📊 Performance Monitoring

### 1. **Built-in Metrics**
The sanitization system includes performance monitoring:

```typescript
// Automatic performance tracking
const result = SanitizationMetrics.measureSanitization(
  () => createSafeHTML(content),
  content.length
);

// Get performance statistics
const metrics = SanitizationMetrics.getAveragePerformance();
console.log(`Average duration: ${metrics.avgDuration}ms`);
```

### 2. **Performance Guidelines**
- ✅ Large content (1000+ elements): < 100ms
- ✅ Typical content (< 100 elements): < 10ms
- ✅ Mathematical content: Preserve all valid MathML/KaTeX

---

## 🚨 Security Incident Response

### 1. **If XSS is Discovered**
1. **IMMEDIATE:** Remove affected code from production
2. **ASSESS:** Determine scope and impact
3. **FIX:** Apply sanitization using approved utilities
4. **TEST:** Run full XSS test suite
5. **DEPLOY:** Only after security review

### 2. **Reporting Security Issues**
- **Internal:** Create high-priority ticket with `[SECURITY]` tag
- **Code Review:** Mandatory security review for all sanitization changes
- **Documentation:** Update this document with new threats/mitigations

---

## ✅ Developer Checklist

Before deploying code that handles HTML content:

- [ ] ✅ Uses approved sanitization utilities
- [ ] ✅ Never uses raw `dangerouslySetInnerHTML`
- [ ] ✅ Includes comprehensive tests for XSS vectors
- [ ] ✅ Performance tested with large content
- [ ] ✅ Mathematical content preserved (if applicable)
- [ ] ✅ Code reviewed by security-aware developer
- [ ] ✅ No hardcoded HTML without sanitization

---

## 📚 Code Examples

### ✅ **CORRECT Implementations**

#### **Basic Content Sanitization**
```typescript
import { createSafeHTML } from '../utils/sanitize';

// PDF preview content
const PreviewComponent = ({ content }: { content: string }) => (
  <div dangerouslySetInnerHTML={createSafeHTML(content)} />
);

// User-generated content
const UserComment = ({ comment }: { comment: string }) => (
  <div dangerouslySetInnerHTML={createSafeHTML(comment, true)} />
);
```

#### **Performance-Monitored Sanitization**
```typescript
import { SanitizationMetrics, createSafeHTML } from '../utils/sanitize';

const PerformantComponent = ({ content }: { content: string }) => {
  const safeHTML = SanitizationMetrics.measureSanitization(
    () => createSafeHTML(content),
    content.length
  );
  
  return <div dangerouslySetInnerHTML={safeHTML} />;
};
```

#### **Mathematical Content**
```typescript
import { sanitizePreviewContent, containsMathContent } from '../utils/sanitize';

const MathComponent = ({ mathContent }: { mathContent: string }) => {
  if (!containsMathContent(mathContent)) {
    // Use strict sanitization for non-math content
    return <div dangerouslySetInnerHTML={createSafeHTML(mathContent, true)} />;
  }
  
  // Use preview sanitization for mathematical content
  return <div dangerouslySetInnerHTML={createSafeHTML(mathContent)} />;
};
```

### ❌ **INCORRECT Implementations**

```typescript
// ❌ NEVER DO THIS - Raw HTML without sanitization
const BadComponent = ({ content }: { content: string }) => (
  <div dangerouslySetInnerHTML={{ __html: content }} />
);

// ❌ NEVER DO THIS - Direct innerHTML manipulation
const AlsoBad = ({ content }: { content: string }) => {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (ref.current) {
      ref.current.innerHTML = content; // XSS RISK!
    }
  }, [content]);
  return <div ref={ref} />;
};

// ❌ NEVER DO THIS - Eval or Function constructor
const VeryBad = ({ script }: { script: string }) => {
  useEffect(() => {
    eval(script); // EXTREME XSS RISK!
  }, [script]);
  return null;
};
```

---

## 🔄 Maintenance Schedule

### Monthly Reviews
- [ ] Update XSS test vectors with latest threats
- [ ] Review sanitization performance metrics
- [ ] Update DOMPurify to latest version
- [ ] Scan for new `dangerouslySetInnerHTML` usage

### Quarterly Reviews
- [ ] Full security audit of sanitization utilities
- [ ] Performance benchmarking against large datasets
- [ ] Review and update security documentation
- [ ] Train team on latest XSS prevention techniques

---

## 📖 References

### Security Resources
- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [DOMPurify Documentation](https://github.com/cure53/DOMPurify)
- [React Security Best Practices](https://reactjs.org/docs/dom-elements.html#dangerouslysetinnerhtml)

### Internal Documentation
- [ANALISIS_SEGURIDAD_Y_MEJORAS_2025.md](../ANALISIS_SEGURIDAD_Y_MEJORAS_2025.md)
- [PLAN_MEJORA_FASES_2025.md](../PLAN_MEJORA_FASES_2025.md)

---

**Document Version:** 1.0  
**Approved By:** Security Team  
**Next Review:** April 15, 2025

---

> 🔒 **Security Notice:** This document contains security-critical information. Any modifications must be reviewed by the security team before implementation.