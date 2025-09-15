import { render, screen } from '@testing-library/react';
import { expect, test } from 'vitest';
;(globalThis as any).expect = expect;
await import('@testing-library/jest-dom');
import React from 'react';
import Modal from '../components/Modal';

test('does not render when closed', () => {
  render(<Modal title="Hola" message="Mensaje" type="success" isOpen={false} />);
  expect(screen.queryByText('Hola')).toBeNull();
});

test('renders title and message when open', () => {
  render(<Modal title="Hola" message="Mensaje" type="error" isOpen={true} />);
  expect(screen.getByText('Hola')).toBeInTheDocument();
  expect(screen.getByText('Mensaje')).toBeInTheDocument();
});
