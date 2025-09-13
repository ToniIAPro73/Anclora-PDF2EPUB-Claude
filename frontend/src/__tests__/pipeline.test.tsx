import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { vi, expect, describe, test } from 'vitest'
;(globalThis as any).expect = expect
await import('@testing-library/jest-dom')
vi.mock('../AuthContext', () => ({
  useAuth: () => ({ token: null, logout: vi.fn() }),
}))
vi.mock('react-router-dom', () => ({
  useNavigate: () => vi.fn(),
}))
import ConversionPanel from '../components/ConversionPanel'
import React from 'react'

describe('pipeline selection', () => {
  test('sends selected pipeline_id with request', async () => {
    const file = new File(['hello'], 'sample.pdf', { type: 'application/pdf' })
    const fetchMock = vi.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve({ task_id: '1' }) }))
    // @ts-ignore
    global.fetch = fetchMock

    render(<ConversionPanel file={file} />)

    const pipelineSelect = screen.queryByLabelText(/pipeline/i)
    if (!pipelineSelect) {
      throw new Error('Pipeline selector not implemented')
    }

    fireEvent.change(pipelineSelect, { target: { value: 'demo' } })
    const button = screen.getByRole('button')
    fireEvent.click(button)

    await waitFor(() => expect(fetchMock).toHaveBeenCalled())
    const body = fetchMock.mock.calls[0][1].body as FormData
    expect(body.get('pipeline_id')).toBe('demo')
  })
})
