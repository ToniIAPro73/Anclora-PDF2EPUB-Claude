/**
 * Comprehensive tests for HTML sanitization utilities
 * Tests XSS prevention, mathematical content preservation, and performance
 */

import { describe, it, expect, beforeEach } from 'vitest';
import {
  sanitizePreviewContent,
  sanitizeUserContent,
  createSafeHTML,
  containsMathContent,
  SanitizationMetrics,
} from './sanitize';

describe('HTML Sanitization', () => {
  beforeEach(() => {
    // Reset performance metrics before each test
    SanitizationMetrics['metrics'] = [];
  });

  describe('sanitizePreviewContent', () => {
    it('should preserve safe HTML elements', () => {
      const input = '<div><p>Hello <strong>world</strong></p><h1>Title</h1></div>';
      const result = sanitizePreviewContent(input);
      expect(result).toBe(input);
    });

    it('should remove script tags', () => {
      const input = '<div>Safe content<script>alert("xss")</script></div>';
      const result = sanitizePreviewContent(input);
      expect(result).toBe('<div>Safe content</div>');
      expect(result).not.toContain('script');
      expect(result).not.toContain('alert');
    });

    it('should remove dangerous event handlers', () => {
      const input = '<div onclick="alert(\'xss\')" onload="evil()">Content</div>';
      const result = sanitizePreviewContent(input);
      expect(result).toBe('<div>Content</div>');
      expect(result).not.toContain('onclick');
      expect(result).not.toContain('onload');
    });

    it('should preserve mathematical markup (KaTeX)', () => {
      const input = `
        <span class="katex">
          <math xmlns="http://www.w3.org/1998/Math/MathML">
            <mrow>
              <mi>x</mi>
              <mo>=</mo>
              <mfrac>
                <mrow><mo>−</mo><mi>b</mi></mrow>
                <mrow><mn>2</mn><mi>a</mi></mrow>
              </mfrac>
            </mrow>
          </math>
        </span>
      `;
      const result = sanitizePreviewContent(input);
      expect(result).toContain('math');
      expect(result).toContain('mrow');
      expect(result).toContain('mfrac');
      expect(result).toContain('katex');
    });

    it('should preserve SVG elements for diagrams', () => {
      const input = `
        <svg viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="40" fill="red"/>
          <text x="50" y="50" text-anchor="middle">Text</text>
        </svg>
      `;
      const result = sanitizePreviewContent(input);
      expect(result).toContain('svg');
      expect(result).toContain('circle');
      expect(result).toContain('text');
      expect(result).toContain('viewBox');
    });

    it('should handle empty or invalid input', () => {
      expect(sanitizePreviewContent('')).toBe('');
      expect(sanitizePreviewContent(null as any)).toBe('');
      expect(sanitizePreviewContent(undefined as any)).toBe('');
    });

    it('should remove iframe and embed tags', () => {
      const input = '<div>Content<iframe src="evil.com"></iframe><embed src="bad.swf"></div>';
      const result = sanitizePreviewContent(input);
      expect(result).toBe('<div>Content</div>');
      expect(result).not.toContain('iframe');
      expect(result).not.toContain('embed');
    });

    it('should sanitize dangerous URLs', () => {
      const input = '<img src="javascript:alert(\'xss\')" alt="test">';
      const result = sanitizePreviewContent(input);
      expect(result).not.toContain('javascript:');
    });
  });

  describe('sanitizeUserContent', () => {
    it('should be more restrictive than preview sanitization', () => {
      const input = '<div><img src="test.jpg"><script>alert("xss")</script></div>';
      const userResult = sanitizeUserContent(input);
      const previewResult = sanitizePreviewContent(input);
      
      // User sanitization should remove more elements
      expect(userResult).not.toContain('img');
      expect(userResult).not.toContain('script');
      expect(userResult).not.toContain('div'); // div is also forbidden in strict mode
      expect(userResult).toBe('');
    });

    it('should allow basic text formatting', () => {
      const input = '<p>Hello <strong>world</strong> and <em>universe</em></p>';
      const result = sanitizeUserContent(input);
      expect(result).toBe(input);
    });

    it('should remove style attributes', () => {
      const input = '<p style="color: red;">Styled text</p>';
      const result = sanitizeUserContent(input);
      expect(result).toBe('<p>Styled text</p>');
      expect(result).not.toContain('style');
    });
  });

  describe('createSafeHTML', () => {
    it('should return object compatible with dangerouslySetInnerHTML', () => {
      const input = '<p>Safe content</p>';
      const result = createSafeHTML(input);
      
      expect(result).toHaveProperty('__html');
      expect(result.__html).toBe(input);
    });

    it('should use strict sanitization when requested', () => {
      const input = '<div><img src="test.jpg">Text</div>';
      const normalResult = createSafeHTML(input, false);
      const strictResult = createSafeHTML(input, true);
      
      expect(normalResult.__html).toContain('img');
      expect(strictResult.__html).not.toContain('img');
    });
  });

  describe('containsMathContent', () => {
    it('should detect KaTeX class names', () => {
      const inputs = [
        '<span class="katex">Math</span>',
        '<div class="katex-display">Display math</div>',
        '<span class="math-inline">Inline math</span>',
      ];
      
      inputs.forEach(input => {
        expect(containsMathContent(input)).toBe(true);
      });
    });

    it('should detect MathML elements', () => {
      const input = '<math><mrow><mi>x</mi></mrow></math>';
      expect(containsMathContent(input)).toBe(true);
    });

    it('should detect LaTeX delimiters', () => {
      const inputs = [
        'Text with $$E = mc^2$$ equation',
        'Inline \\(x + y = z\\) math',
      ];
      
      inputs.forEach(input => {
        expect(containsMathContent(input)).toBe(true);
      });
    });

    it('should return false for non-math content', () => {
      const inputs = [
        '<p>Regular text</p>',
        '<div>No math here</div>',
        '',
        null,
      ];
      
      inputs.forEach(input => {
        expect(containsMathContent(input as string)).toBe(false);
      });
    });
  });

  describe('SanitizationMetrics', () => {
    it('should measure sanitization performance', () => {
      const testOperation = () => sanitizePreviewContent('<p>Test content</p>');
      const inputSize = 20;
      
      const result = SanitizationMetrics.measureSanitization(testOperation, inputSize);
      
      expect(result).toBe('<p>Test content</p>');
      
      const metrics = SanitizationMetrics.getAveragePerformance();
      expect(metrics.totalOperations).toBe(1);
      expect(metrics.avgDuration).toBeGreaterThan(0);
    });

    it('should calculate average performance correctly', () => {
      // Perform multiple operations
      for (let i = 0; i < 5; i++) {
        SanitizationMetrics.measureSanitization(
          () => sanitizePreviewContent('<p>Test</p>'),
          10
        );
      }
      
      const metrics = SanitizationMetrics.getAveragePerformance();
      expect(metrics.totalOperations).toBe(5);
      expect(metrics.avgDuration).toBeGreaterThan(0);
    });

    it('should limit stored metrics to 100 entries', () => {
      // Perform 150 operations
      for (let i = 0; i < 150; i++) {
        SanitizationMetrics.measureSanitization(
          () => sanitizePreviewContent('<p>Test</p>'),
          10
        );
      }
      
      const metrics = SanitizationMetrics.getAveragePerformance();
      expect(metrics.totalOperations).toBe(100); // Should be capped at 100
    });
  });

  describe('XSS Attack Vectors', () => {
    const xssPayloads = [
      // Script injection
      '<script>alert("xss")</script>',
      '<script src="//evil.com/xss.js"></script>',
      
      // Event handler injection
      '<img src="x" onerror="alert(\'xss\')">',
      '<body onload="alert(\'xss\')">',
      '<div onclick="alert(\'xss\')">Click me</div>',
      
      // JavaScript URLs
      '<a href="javascript:alert(\'xss\')">Link</a>',
      '<img src="javascript:alert(\'xss\')">',
      
      // Data URLs with JavaScript
      '<iframe src="data:text/html,<script>alert(\'xss\')</script>"></iframe>',
      
      // CSS injection
      '<style>body{background:url("javascript:alert(\'xss\')")}</style>',
      '<div style="background:url(javascript:alert(\'xss\'))">',
      
      // HTML5 injection
      '<input onfocus="alert(\'xss\')" autofocus>',
      '<details ontoggle="alert(\'xss\')" open>',
      
      // SVG injection
      '<svg onload="alert(\'xss\')">',
      '<svg><script>alert("xss")</script></svg>',
      
      // Form injection
      '<form><button formaction="javascript:alert(\'xss\')">',
      
      // Meta refresh
      '<meta http-equiv="refresh" content="0;url=javascript:alert(\'xss\')">',
    ];

    it.each(xssPayloads)('should prevent XSS payload: %s', (payload) => {
      const result = sanitizePreviewContent(payload);
      
      // Ensure no dangerous content remains
      expect(result).not.toContain('alert');
      expect(result).not.toContain('javascript:');
      expect(result).not.toContain('onerror');
      expect(result).not.toContain('onload');
      expect(result).not.toContain('onclick');
      expect(result).not.toContain('<script');
      expect(result).not.toContain('eval(');
    });
  });

  describe('Performance Tests', () => {
    it('should handle large HTML content efficiently', () => {
      // Generate large HTML content
      const largeContent = Array(1000)
        .fill('<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>')
        .join('');
      
      const startTime = performance.now();
      const result = sanitizePreviewContent(largeContent);
      const duration = performance.now() - startTime;
      
      expect(result).toContain('<p>');
      expect(duration).toBeLessThan(100); // Should complete in under 100ms
    });

    it('should handle complex mathematical content', () => {
      const complexMath = `
        <div class="katex-display">
          <math xmlns="http://www.w3.org/1998/Math/MathML">
            <mrow>
              <mi>f</mi>
              <mo stretchy="false">(</mo>
              <mi>x</mi>
              <mo stretchy="false">)</mo>
              <mo>=</mo>
              <munderover>
                <mo>∑</mo>
                <mrow><mi>n</mi><mo>=</mo><mn>0</mn></mrow>
                <mi>∞</mi>
              </munderover>
              <mfrac>
                <mrow>
                  <msup><mi>f</mi><mo stretchy="false">(</mo><mi>n</mi><mo stretchy="false">)</mo></msup>
                  <mo stretchy="false">(</mo><mi>a</mi><mo stretchy="false">)</mo>
                </mrow>
                <mrow><mi>n</mi><mo>!</mo></mrow>
              </mfrac>
              <msup>
                <mrow><mo stretchy="false">(</mo><mi>x</mi><mo>−</mo><mi>a</mi><mo stretchy="false">)</mo></mrow>
                <mi>n</mi>
              </msup>
            </mrow>
          </math>
        </div>
      `;
      
      const result = sanitizePreviewContent(complexMath);
      
      // Should preserve mathematical structure
      expect(result).toContain('math');
      expect(result).toContain('munderover');
      expect(result).toContain('mfrac');
      expect(result).toContain('msup');
      expect(result).toContain('katex-display');
    });
  });
});