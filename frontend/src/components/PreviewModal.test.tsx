/**
 * Integration tests for PreviewModal component
 * Tests sanitization integration and XSS prevention in React component
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import React from 'react';
import PreviewModal from './PreviewModal';

// Mock the auth context module first
vi.mock('../AuthContext', () => ({
  useAuth: vi.fn(() => ({
    token: 'mock-token',
    user: null,
    loading: false,
  })),
}));

// Get the mocked function
import { useAuth } from '../AuthContext';
const mockUseAuth = vi.mocked(useAuth);

// Mock KaTeX
vi.mock('katex/contrib/auto-render', () => ({
  default: vi.fn(),
}));

// Mock fetch globally
global.fetch = vi.fn();

describe('PreviewModal Integration Tests', () => {
  const defaultProps = {
    taskId: 'test-task-123',
    onClose: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    // Reset fetch mock
    (global.fetch as any).mockClear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should render loading state initially', () => {
    // Mock fetch to never resolve
    (global.fetch as any).mockImplementation(() => new Promise(() => {}));

    render(<PreviewModal {...defaultProps} />);

    expect(screen.getByText('Cargando...')).toBeInTheDocument();
  });

  it('should fetch preview data with correct authorization', async () => {
    const mockPages = ['<p>Page 1 content</p>', '<p>Page 2 content</p>'];
    
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ pages: mockPages }),
    });

    render(
      <MockedAuthProvider>
        <PreviewModal {...defaultProps} />
      </MockedAuthProvider>
    );

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/preview/test-task-123',
        {
          headers: { Authorization: 'Bearer mock-token' },
        }
      );
    });
  });

  it('should sanitize dangerous content in pages', async () => {
    const maliciousPages = [
      '<p>Safe content</p><script>alert("xss")</script>',
      '<div onclick="alert(\'xss\')">Click me</div><p>More content</p>',
    ];
    
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ pages: maliciousPages }),
    });

    render(
      <MockedAuthProvider>
        <PreviewModal {...defaultProps} />
      </MockedAuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Safe content')).toBeInTheDocument();
    });

    // Ensure dangerous content is not present in the DOM
    const previewBody = document.querySelector('.preview-body');
    expect(previewBody?.innerHTML).not.toContain('<script');
    expect(previewBody?.innerHTML).not.toContain('onclick');
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

    render(
      <MockedAuthProvider>
        <PreviewModal {...defaultProps} />
      </MockedAuthProvider>
    );

    await waitFor(() => {
      const previewBody = document.querySelector('.preview-body');
      expect(previewBody?.innerHTML).toContain('math');
      expect(previewBody?.innerHTML).toContain('mrow');
      expect(previewBody?.innerHTML).toContain('msup');
      expect(previewBody?.innerHTML).toContain('katex-display');
    });
  });

  it('should handle navigation between pages', async () => {
    const mockPages = [
      '<p>Page 1</p>',
      '<p>Page 2</p>',
      '<p>Page 3</p>',
    ];
    
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ pages: mockPages }),
    });

    render(
      <MockedAuthProvider>
        <PreviewModal {...defaultProps} />
      </MockedAuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Page 1')).toBeInTheDocument();
      expect(screen.getByText('1 / 3')).toBeInTheDocument();
    });

    // Test next button
    const nextButton = screen.getByText('Siguiente');
    fireEvent.click(nextButton);

    await waitFor(() => {
      expect(screen.getByText('Page 2')).toBeInTheDocument();
      expect(screen.getByText('2 / 3')).toBeInTheDocument();
    });

    // Test previous button
    const prevButton = screen.getByText('Anterior');
    fireEvent.click(prevButton);

    await waitFor(() => {
      expect(screen.getByText('Page 1')).toBeInTheDocument();
      expect(screen.getByText('1 / 3')).toBeInTheDocument();
    });
  });

  it('should disable navigation buttons appropriately', async () => {
    const mockPages = ['<p>Single page</p>'];
    
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ pages: mockPages }),
    });

    render(
      <MockedAuthProvider>
        <PreviewModal {...defaultProps} />
      </MockedAuthProvider>
    );

    await waitFor(() => {
      const prevButton = screen.getByText('Anterior');
      const nextButton = screen.getByText('Siguiente');
      
      expect(prevButton).toBeDisabled();
      expect(nextButton).toBeDisabled();
    });
  });

  it('should call onClose when close button is clicked', () => {
    (global.fetch as any).mockImplementation(() => new Promise(() => {}));

    render(
      <MockedAuthProvider>
        <PreviewModal {...defaultProps} />
      </MockedAuthProvider>
    );

    const closeButton = screen.getByText('Cerrar');
    fireEvent.click(closeButton);

    expect(defaultProps.onClose).toHaveBeenCalledTimes(1);
  });

  it('should handle fetch errors gracefully', async () => {
    (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

    render(
      <MockedAuthProvider>
        <PreviewModal {...defaultProps} />
      </MockedAuthProvider>
    );

    // Should continue showing loading state if fetch fails
    await waitFor(() => {
      expect(screen.getByText('Cargando...')).toBeInTheDocument();
    });
  });

  it('should handle empty pages array', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ pages: [] }),
    });

    render(
      <MockedAuthProvider>
        <PreviewModal {...defaultProps} />
      </MockedAuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Cargando...')).toBeInTheDocument();
    });
  });

  it('should handle malformed response data', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ malformed: 'response' }),
    });

    render(
      <MockedAuthProvider>
        <PreviewModal {...defaultProps} />
      </MockedAuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Cargando...')).toBeInTheDocument();
    });
  });

  describe('XSS Prevention in Component', () => {
    const xssPayloads = [
      '<script>document.body.innerHTML = "HACKED"</script>',
      '<img src="x" onerror="document.body.innerHTML = \'HACKED\'">',
      '<div onclick="document.body.innerHTML = \'HACKED\'">Click</div>',
      '<iframe src="javascript:alert(\'XSS\')"></iframe>',
      '<svg onload="document.body.innerHTML = \'HACKED\'"></svg>',
    ];

    it.each(xssPayloads)('should prevent XSS attack: %s', async (payload) => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ pages: [payload] }),
      });

      render(
        <MockedAuthProvider>
          <PreviewModal {...defaultProps} />
        </MockedAuthProvider>
      );

      await waitFor(() => {
        // Ensure the page has loaded
        expect(document.querySelector('.preview-body')).toBeInTheDocument();
      });

      // Verify that the malicious content didn't execute
      expect(document.body.innerHTML).not.toContain('HACKED');
      
      // Verify dangerous elements are not present
      const previewBody = document.querySelector('.preview-body');
      expect(previewBody?.innerHTML).not.toContain('<script');
      expect(previewBody?.innerHTML).not.toContain('onerror');
      expect(previewBody?.innerHTML).not.toContain('onclick');
      expect(previewBody?.innerHTML).not.toContain('onload');
      expect(previewBody?.innerHTML).not.toContain('<iframe');
    });
  });

  describe('Performance Tests', () => {
    it('should handle large page content efficiently', async () => {
      // Generate large content
      const largeContent = Array(1000)
        .fill('<p>Lorem ipsum dolor sit amet consectetur adipiscing elit.</p>')
        .join('');
      
      const mockPages = [largeContent];
      
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ pages: mockPages }),
      });

      const startTime = performance.now();
      
      render(
        <MockedAuthProvider>
          <PreviewModal {...defaultProps} />
        </MockedAuthProvider>
      );

      await waitFor(() => {
        expect(document.querySelector('.preview-body')).toBeInTheDocument();
      });

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      // Should render large content in reasonable time
      expect(renderTime).toBeLessThan(1000); // Less than 1 second
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA attributes', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ pages: ['<p>Content</p>'] }),
      });

      render(
        <MockedAuthProvider>
          <PreviewModal {...defaultProps} />
        </MockedAuthProvider>
      );

      await waitFor(() => {
        const modal = document.querySelector('[role="dialog"]');
        expect(modal).toBeInTheDocument();
        expect(modal).toHaveAttribute('aria-modal', 'true');
        
        const liveRegion = document.querySelector('[aria-live="assertive"]');
        expect(liveRegion).toBeInTheDocument();
      });
    });

    it('should have proper button states', async () => {
      const mockPages = ['<p>Page 1</p>', '<p>Page 2</p>'];
      
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ pages: mockPages }),
      });

      render(
        <MockedAuthProvider>
          <PreviewModal {...defaultProps} />
        </MockedAuthProvider>
      );

      await waitFor(() => {
        const prevButton = screen.getByText('Anterior');
        const nextButton = screen.getByText('Siguiente');
        
        // First page: previous disabled, next enabled
        expect(prevButton).toBeDisabled();
        expect(nextButton).not.toBeDisabled();
      });
    });
  });
});