import { AxiosError } from 'axios'
import { toApiError } from './errors'

test('uses the API error envelope message', () => {
  const err = new AxiosError('fail', '400', undefined, undefined, {
    status: 409, statusText: '', headers: {}, config: {} as never,
    data: { error: { code: 'http_error', message: 'Email already exists' } },
  })
  const api = toApiError(err)
  expect(api.message).toBe('Email already exists')
  expect(api.status).toBe(409)
})

test('network failures become a friendly message', () => {
  const api = toApiError(new AxiosError('Network Error'))
  expect(api.code).toBe('network_error')
  expect(api.message).toMatch(/cannot reach the server/i)
})
