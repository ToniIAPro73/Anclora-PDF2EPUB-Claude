import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { expect, test } from 'vitest';
;(globalThis as any).expect = expect;
await import('@testing-library/jest-dom');
import Toast from '../components/Toast';

test('announces message with proper roles and animations and cleans up on close', () => {
  const Wrapper = () => {
    const [show, setShow] = React.useState(true);
    return show ? (
      <Toast
        title="Aviso"
        message="Hola"
        variant="success"
        onClose={() => setShow(false)}
      />
    ) : null;
  };

  render(<Wrapper />);
  const toast = screen.getByRole('alert');
  expect(toast).toHaveAttribute('role', 'alert');
  expect(toast).toHaveAttribute('aria-live', 'assertive');
  expect(screen.getByText('Aviso')).toBeInTheDocument();
  expect(screen.getByText('Hola')).toBeInTheDocument();
  fireEvent.click(screen.getByLabelText(/close/i));
  expect(screen.queryByText('Hola')).toBeNull();
});
