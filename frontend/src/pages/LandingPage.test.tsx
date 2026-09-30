import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { vi } from 'vitest'
import { LandingPage } from './LandingPage'

vi.mock('../services/healthService', () => ({
  getHealth: vi.fn().mockResolvedValue({ status: 'ok', app: 'CampusFind AI', environment: 'test', database: 'up' }),
}))
vi.mock('../services/itemService', () => ({
  listItems: vi.fn().mockResolvedValue({
    total: 1,
    items: [{
      id: 1, title: 'Black Dell Laptop', type: 'LOST', category: 'Electronics', brand: 'Dell', color: 'Black',
      description: null, location: 'Central Library', date: '2026-09-29', time: null, image_url: null,
      private_details: null, status: 'ACTIVE', approval_status: 'APPROVED', visibility: 'PUBLIC', reported_by: 1,
      reporter_name: 'A', created_at: '', updated_at: '',
    }],
  }),
}))

test('renders hero, CTAs, backend status and recent items', async () => {
  render(<MemoryRouter><LandingPage /></MemoryRouter>)
  expect(screen.getByText(/lost something on campus/i)).toBeInTheDocument()
  expect(screen.getByRole('link', { name: 'Report Lost Item' })).toHaveAttribute('href', '/report/lost')
  expect(screen.getByRole('link', { name: 'Report Found Item' })).toHaveAttribute('href', '/report/found')
  expect(await screen.findByText(/database up/i)).toBeInTheDocument()
  expect(await screen.findByText('Black Dell Laptop')).toBeInTheDocument()
})
