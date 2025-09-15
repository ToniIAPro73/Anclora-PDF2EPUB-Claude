/**
 * HTML Sanitization Utilities for Anclora PDF2EPUB
 * 
 * This module provides secure HTML sanitization using DOMPurify,
 * specifically configured for rendering PDF preview content with
 * mathematical expressions (KaTeX/MathJax support).
 * 
 * Security: Prevents XSS attacks while preserving mathematical markup
 * Performance: Optimized configuration for preview content
 */

import DOMPurify from 'dompurify';

/**
 * Configuration for DOMPurify optimized for PDF preview content
 * Allows mathematical markup while blocking dangerous elements
 */
const PREVIEW_SANITIZE_CONFIG: DOMPurify.Config = {
  // Allow common HTML elements for document structure
  ALLOWED_TAGS: [
    // Text structure
    'p', 'div', 'span', 'br', 'hr',
    // Headers
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    // Lists
    'ul', 'ol', 'li',
    // Tables
    'table', 'thead', 'tbody', 'tr', 'td', 'th',
    // Text formatting
    'strong', 'em', 'u', 'i', 'b', 'sub', 'sup',
    // Images and media (for diagrams)
    'img', 'figure', 'figcaption',
    // Mathematical expressions (KaTeX generates these)
    'math', 'semantics', 'mrow', 'msup', 'msub', 'mfrac', 'msqrt',
    'mroot', 'mtext', 'mn', 'mo', 'mi', 'mspace', 'mover', 'munder',
    'munderover', 'mmultiscripts', 'mtable', 'mtr', 'mtd',
    // SVG for mathematical diagrams
    'svg', 'g', 'path', 'circle', 'rect', 'line', 'polyline', 'polygon',
    'text', 'tspan', 'defs', 'use',
  ],
  
  // Allow safe attributes
  ALLOWED_ATTR: [
    // General attributes
    'class', 'id', 'style',
    // Image attributes
    'src', 'alt', 'width', 'height',
    // Table attributes
    'colspan', 'rowspan',
    // Mathematical attributes
    'xmlns', 'mathvariant', 'mathsize', 'mathcolor', 'mathbackground',
    'displaystyle', 'scriptlevel',
    // SVG attributes
    'viewBox', 'preserveAspectRatio', 'd', 'fill', 'stroke', 'stroke-width',
    'cx', 'cy', 'r', 'x', 'y', 'x1', 'y1', 'x2', 'y2', 'points',
    'font-size', 'font-family', 'text-anchor',
  ],
  
  // Preserve whitespace for mathematical expressions
  KEEP_CONTENT: true,
  
  // Remove dangerous protocols
  ALLOWED_URI_REGEXP: /^(?:(?:(?:f|ht)tps?|mailto|tel|callto|cid|xmpp|data):|[^a-z]|[a-z+.\-]+(?:[^a-z+.\-:]|$))/i,
  
  // Remove script-like attributes
  FORBID_ATTR: ['onerror', 'onload', 'onclick', 'onmouseover', 'onfocus', 'onblur'],
  
  // Remove dangerous tags completely
  FORBID_TAGS: ['script', 'object', 'embed', 'form', 'input', 'textarea', 'button'],
  
  // Remove data attributes that could be used for XSS
  ALLOW_DATA_ATTR: false,
  
  // Custom hook to sanitize CSS
  HOOKS: {
    uponSanitizeAttribute: function (node, hookEvent) {
      // Remove style attributes that contain javascript: or other dangerous content
      if (hookEvent.attrName === 'style') {
        const attrValue = hookEvent.attrValue || '';
        // More comprehensive check for dangerous CSS
        if (/javascript:|expression\(|@import|url\s*\(\s*['"]*javascript:/i.test(attrValue)) {
          hookEvent.keepAttr = false;
          return;
        }
        // Also check for other CSS injection vectors
        if (/behavior\s*:|moz-binding\s*:|data\s*:\s*text\/html/i.test(attrValue)) {
          hookEvent.keepAttr = false;
          return;
        }
      }
    },
  },
};

/**
 * Strict configuration for user-generated content
 * More restrictive than preview content
 */
const STRICT_SANITIZE_CONFIG: DOMPurify.Config = {
  ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'u', 'i', 'b'],
  ALLOWED_ATTR: ['class'],
  KEEP_CONTENT: true,
  FORBID_ATTR: ['style', 'onclick', 'onerror', 'onload'],
  FORBID_TAGS: ['script', 'iframe', 'object', 'embed', 'form', 'input', 'img', 'div'],
  ALLOW_DATA_ATTR: false,
};

/**
 * Sanitizes HTML content for PDF preview display
 * Optimized for mathematical content and document structure
 * 
 * @param html - Raw HTML content from PDF conversion
 * @returns Sanitized HTML safe for rendering
 */
export function sanitizePreviewContent(html: string): string {
  if (!html || typeof html !== 'string') {
    return '';
  }
  
  try {
    let sanitized = DOMPurify.sanitize(html, PREVIEW_SANITIZE_CONFIG);
    
    // Additional security check for CSS-based XSS that might slip through
    // This is a failsafe in case the HOOKS don't work as expected
    if (/javascript:|expression\(|behavior\s*:|moz-binding\s*:/i.test(sanitized)) {
      // Remove all style attributes as a safety measure
      sanitized = sanitized.replace(/\s+style\s*=\s*["'][^"']*["']/gi, '');
    }
    
    return sanitized;
  } catch (error) {
    console.error('Error sanitizing preview content:', error);
    // Return empty string on error to prevent XSS
    return '';
  }
}

/**
 * Strict sanitization for user-generated content
 * Use for comments, descriptions, or any user input
 * 
 * @param html - User-generated HTML content
 * @returns Strictly sanitized HTML
 */
export function sanitizeUserContent(html: string): string {
  if (!html || typeof html !== 'string') {
    return '';
  }
  
  try {
    return DOMPurify.sanitize(html, STRICT_SANITIZE_CONFIG);
  } catch (error) {
    console.error('Error sanitizing user content:', error);
    return '';
  }
}

/**
 * Creates a sanitized React props object for dangerouslySetInnerHTML
 * This is the recommended way to use sanitized content in React
 * 
 * @param html - HTML content to sanitize
 * @param strict - Whether to use strict sanitization (default: false)
 * @returns Object ready for dangerouslySetInnerHTML prop
 */
export function createSafeHTML(html: string, strict: boolean = false): { __html: string } {
  const sanitizedHTML = strict 
    ? sanitizeUserContent(html)
    : sanitizePreviewContent(html);
    
  return { __html: sanitizedHTML };
}

/**
 * Validates if HTML content appears to contain mathematical expressions
 * Useful for applying different sanitization strategies
 * 
 * @param html - HTML content to check
 * @returns true if content likely contains math expressions
 */
export function containsMathContent(html: string): boolean {
  if (!html) return false;
  
  // Check for KaTeX class names
  const katexPatterns = [
    /class="[^"]*katex[^"]*"/i,
    /class="[^"]*math[^"]*"/i,
  ];
  
  // Check for mathematical elements
  const mathPatterns = [
    /<math[^>]*>/i,
    /\$\$.*\$\$/,
    /\\\(.*\\\)/,
    /<span[^>]*class="[^"]*(?:katex|math)[^"]*"[^>]*>/i,
  ];
  
  return [...katexPatterns, ...mathPatterns].some(pattern => pattern.test(html));
}

/**
 * Performance monitoring for sanitization operations
 * Useful for debugging and optimization
 */
export class SanitizationMetrics {
  private static metrics: Array<{ timestamp: number; duration: number; size: number }> = [];
  
  static measureSanitization<T>(operation: () => T, inputSize: number): T {
    const start = performance.now();
    const result = operation();
    const duration = performance.now() - start;
    
    this.metrics.push({
      timestamp: Date.now(),
      duration,
      size: inputSize,
    });
    
    // Keep only last 100 measurements
    if (this.metrics.length > 100) {
      this.metrics = this.metrics.slice(-100);
    }
    
    return result;
  }
  
  static getAveragePerformance(): { avgDuration: number; totalOperations: number } {
    if (this.metrics.length === 0) {
      return { avgDuration: 0, totalOperations: 0 };
    }
    
    const avgDuration = this.metrics.reduce((sum, m) => sum + m.duration, 0) / this.metrics.length;
    return {
      avgDuration: Math.round(avgDuration * 100) / 100, // Round to 2 decimals
      totalOperations: this.metrics.length,
    };
  }
}

// Default export for convenience
export default {
  sanitizePreviewContent,
  sanitizeUserContent,
  createSafeHTML,
  containsMathContent,
  SanitizationMetrics,
};