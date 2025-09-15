/**
 * Simplified integration tests for PreviewModal component
 * Focus on essential sanitization functionality
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import React from 'react';
import PreviewModal from './PreviewModal';

// Mock the useAuth hook
vi.mock('../AuthContext', () => ({
  useAuth: () => ({
    token: 'mock-token',
    user: null,
    loading: false,
  }),
}));

// Mock KaTeX
vi.mock('katex/contrib/auto-render', () => ({
  default: vi.fn(),
}));

// Mock fetch globally
global.fetch = vi.fn();

describe('PreviewModal Sanitization Tests', () => {
  const defaultProps = {
    taskId: 'test-task-123',
    onClose: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    (global.fetch as any).mockClear();
  });

  it('should render and sanitize dangerous content', async () => {
    const maliciousPages = [
      '<p>Safe content</p><script>alert("xss")</script>',
    ];
    
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ pages: maliciousPages }),
    });

    render(<PreviewModal {...defaultProps} />);

    await waitFor(() => {
      expect(screen.getByText('Safe content')).toBeInTheDocument();
    });

    // Ensure dangerous content is not present in the DOM
    const previewBody = document.querySelector('.preview-body');
    expect(previewBody?.innerHTML).not.toContain('<script');
    expect(previewBody?.innerHTML).not.toContain('alert');
    expect(previewBody?.innerHTML).toContain('<p>Safe content</p>');
  });

  it('should preserve mathematical content', async () => {
    const mathPages = [
      `<div class="katex-display">
        <math xmlns="http://www.w3.org/1998/Math/MathML">
          <mrow>
            <mi>E</mi>
            <mo>=</mo>
            <mi>m</mi>
            <msup><mi>c</mi><mn>2</mn></msup>
          </mrow>
        </math>
      </div>`,
    ];
    
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ pages: mathPages }),
    });

    render(<PreviewModal {...defaultProps} />);

    await waitFor(() => {
      const previewBody = document.querySelector('.preview-body');
      expect(previewBody?.innerHTML).toContain('math');
      expect(previewBody?.innerHTML).toContain('mrow');
      expect(previewBody?.innerHTML).toContain('msup');
      expect(previewBody?.innerHTML).toContain('katex-display');
    });
  });

  it('should remove dangerous CSS injection', async () => {
    const cssInjectionPages = [
      '<div style="background:url(javascript:alert(\'xss\'))">Content</div>',
    ];
    
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ pages: cssInjectionPages }),
    });

    render(<PreviewModal {...defaultProps} />);

    await waitFor(() => {
      const previewBody = document.querySelector('.preview-body');
      // Should either remove the dangerous style or sanitize it
      expect(previewBody?.innerHTML).not.toContain('javascript:');
      expect(previewBody?.innerHTML).not.toContain('alert');
    });
  });

  it('should handle empty or invalid response', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ pages: [] }),
    });

    render(<PreviewModal {...defaultProps} />);

    // Should show loading state when no pages
    expect(screen.getByText('Cargando...')).toBeInTheDocument();
  });

  it('should call fetch with correct parameters', async () => {
    const mockPages = ['<p>Test content</p>'];
    
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ pages: mockPages }),
    });

    render(<PreviewModal {...defaultProps} />);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/preview/test-task-123',
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: 'Bearer mock-token'
          })
        })
      );
    });
  });
});