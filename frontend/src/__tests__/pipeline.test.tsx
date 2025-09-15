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
    const fetchMock = vi.fn()
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ pipelines: [{ id: 'demo', quality: '', estimated_time: 0 }] })
    })
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ task_id: '1' })
    })
    // @ts-ignore
    global.fetch = fetchMock

    render(<ConversionPanel file={file} />)

    const pipelineSelect = await screen.findByRole('radio')
    fireEvent.click(pipelineSelect)
    const button = screen.getByRole('button')
    fireEvent.click(button)

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2))
    const body = fetchMock.mock.calls[1][1].body as FormData
    expect(body.get('pipeline_id')).toBe('demo')
  })
})
