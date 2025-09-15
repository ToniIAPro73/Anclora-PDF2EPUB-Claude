import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { expect, test } from 'vitest';
;(globalThis as any).expect = expect;
await import('@testing-library/jest-dom');
import Toast from '../components/Toast';

test('announces message and cleans up on close', () => {
  const Wrapper = () => {
    const [show, setShow] = React.useState(true);
    return show ? <Toast message="Hola" onClose={() => setShow(false)} /> : null;
  };

  render(<Wrapper />);
  const toast = screen.getByRole('alert');
  expect(toast).toHaveAttribute('aria-live', 'assertive');
  expect(screen.getByText('Hola')).toBeInTheDocument();
  fireEvent.click(screen.getByLabelText(/close/i));
  expect(screen.queryByText('Hola')).toBeNull();
});
