import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { vi } from 'vitest'
import { ItemCard } from '../components/ItemCard'
import type { Item } from '../services/types'
import { ItemsPage } from './ItemsPage'
import { MyItemsPage } from './MyItemsPage'
import { ReportItemPage } from './ReportItemPage'

const base: Item = {
  id: 1, title: 'Public Laptop', type: 'LOST', category: 'Electronics', brand: null, color: null,
  description: null, location: 'Central Library', date: '2026-09-29', time: null, image_url: null,
  private_details: null, status: 'ACTIVE', approval_status: 'APPROVED', visibility: 'PUBLIC',
  reported_by: 1, reporter_name: 'A', created_at: '', updated_at: '',
}
const publicItem = base
const privateItem: Item = { ...base, id: 2, title: 'Gold Chain', visibility: 'PRIVATE' }

const mocks = vi.hoisted(() => ({
  listItems: vi.fn(),
  getMyItems: vi.fn(),
}))
vi.mock('../services/itemService', () => ({
  listItems: mocks.listItems,
  getMyItems: mocks.getMyItems,
  getMeta: vi.fn().mockResolvedValue({ categories: ['Electronics'], locations: ['Central Library'] }),
  deleteItem: vi.fn(),
  createItem: vi.fn(),
  uploadImage: vi.fn(),
}))

const wrap = (ui: React.ReactElement) => render(<MemoryRouter>{ui}</MemoryRouter>)

describe.each([['LOST'], ['FOUND']] as const)('%s report form', (type) => {
  test('has a Visibility selector defaulting to Public, with help text', async () => {
    wrap(<ReportItemPage type={type} />)
    expect(await screen.findByText('Visibility')).toBeInTheDocument()
    expect(screen.getByRole('radio', { name: 'Public' })).toBeChecked()
    expect(screen.getByRole('radio', { name: 'Private / Sensitive' })).not.toBeChecked()
    expect(screen.getByText(/not shown in public listings or search/i)).toBeInTheDocument()
  })
})

test('can switch the report to Private / Sensitive', async () => {
  wrap(<ReportItemPage type="LOST" />)
  await userEvent.click(await screen.findByRole('radio', { name: 'Private / Sensitive' }))
  expect(screen.getByRole('radio', { name: 'Private / Sensitive' })).toBeChecked()
  expect(screen.getByRole('radio', { name: 'Public' })).not.toBeChecked()
})

test('PRIVATE badge only on private items', () => {
  wrap(<><ItemCard item={publicItem} /><ItemCard item={privateItem} /></>)
  const cards = screen.getAllByRole('article')
  expect(within(cards[0]).queryByText(/PRIVATE/)).not.toBeInTheDocument()
  expect(within(cards[1]).getByText('🔒 PRIVATE')).toBeInTheDocument()
})

test('My Items shows the owner their private item with the badge', async () => {
  mocks.getMyItems.mockResolvedValue([publicItem, privateItem])
  wrap(<MyItemsPage />)
  expect(await screen.findByText('Gold Chain')).toBeInTheDocument()
  expect(screen.getByText('Public Laptop')).toBeInTheDocument()
  expect(screen.getAllByText('🔒 PRIVATE')).toHaveLength(1)
})

test('public listing shows exactly what the API returns and never asks for private items', async () => {
  // The backend is the authority: a public/anonymous response contains no private items.
  mocks.listItems.mockResolvedValue({ total: 1, items: [publicItem] })
  wrap(<ItemsPage />)
  expect(await screen.findByText('Public Laptop')).toBeInTheDocument()
  expect(screen.queryByText('Gold Chain')).not.toBeInTheDocument()
  expect(screen.queryByText(/PRIVATE/)).not.toBeInTheDocument()
  expect(mocks.listItems.mock.calls[0][0]).not.toHaveProperty('visibility', 'PRIVATE')
})
