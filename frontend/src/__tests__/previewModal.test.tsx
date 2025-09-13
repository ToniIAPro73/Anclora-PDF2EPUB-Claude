import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, expect, test } from 'vitest';
;(globalThis as any).expect = expect;
await import('@testing-library/jest-dom');
vi.mock('../AuthContext', () => ({
  useAuth: () => ({ token: 'tok' }),
}));
import PreviewModal from '../components/PreviewModal';
import React from 'react';

test('loads pages and navigates', async () => {
  const fetchMock = vi.fn(() =>
    Promise.resolve({ ok: true, json: () => Promise.resolve({ pages: ['<p>uno</p>', '<p>dos</p>'] }) })
  );
  // @ts-ignore
  global.fetch = fetchMock;
  render(<PreviewModal taskId="1" onClose={() => {}} />);
  await waitFor(() => expect(fetchMock).toHaveBeenCalled());
  expect(screen.getByText('uno')).toBeInTheDocument();
  fireEvent.click(screen.getByText(/siguiente/i));
  await waitFor(() => expect(screen.getByText('dos')).toBeInTheDocument());
});

test('renders math formulas with KaTeX', async () => {
  const fetchMock = vi.fn(() =>
    Promise.resolve({ ok: true, json: () => Promise.resolve({ pages: ['<p>$$x^2$$</p>'] }) })
  );
  // @ts-ignore
  global.fetch = fetchMock;
  render(<PreviewModal taskId="1" onClose={() => {}} />);
  await waitFor(() => expect(fetchMock).toHaveBeenCalled());
  await waitFor(() => expect(document.querySelector('.katex')).not.toBeNull());
});
