import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { ItemCard } from './ItemCard'
import { MatchCard } from './MatchCard'
import { Timeline } from './Timeline'
import type { Item } from '../services/types'

const item: Item = {
  id: 7, title: 'Black Dell Laptop', type: 'FOUND', category: 'Electronics', brand: 'Dell', color: 'Black',
  description: null, location: 'Central Library', date: '2026-09-30', time: null, image_url: null,
  private_details: null, status: 'ACTIVE', approval_status: 'APPROVED', visibility: 'PUBLIC', reported_by: 1,
  reporter_name: 'Diya', created_at: '', updated_at: '',
}

test('ItemCard shows the key fields and links to details', () => {
  render(<MemoryRouter><ItemCard item={item} /></MemoryRouter>)
  expect(screen.getByText('Black Dell Laptop')).toBeInTheDocument()
  expect(screen.getByText('FOUND')).toBeInTheDocument()
  expect(screen.getByText('ACTIVE')).toBeInTheDocument()
  expect(screen.getByText(/Central Library/)).toBeInTheDocument()
  expect(screen.getByRole('link', { name: 'View Details' })).toHaveAttribute('href', '/items/7')
})

test('MatchCard calls it a match score, not a probability', () => {
  render(
    <MemoryRouter>
      <MatchCard match={{ match_score: 91, matching_attributes: ['same brand', 'same color'], explanation: 'Both reports describe a laptop.', item }} />
    </MemoryRouter>,
  )
  expect(screen.getByText('91% MATCH SCORE')).toBeInTheDocument()
  expect(screen.getByText('✓ Same brand')).toBeInTheDocument()
  expect(screen.getByRole('link', { name: 'View Match' })).toHaveAttribute('href', '/items/7')
  expect(screen.queryByText(/probab/i)).not.toBeInTheDocument()
})

test('Timeline renders every step', () => {
  render(<Timeline steps={[{ key: 'a', label: 'Reported', done: true }, { key: 'b', label: 'Item Returned', done: false }]} />)
  expect(screen.getByText('Reported')).toBeInTheDocument()
  expect(screen.getByText('Item Returned')).toBeInTheDocument()
})

test('MatchCard shows the matched item image when it has one', () => {
  render(
    <MemoryRouter>
      <MatchCard match={{ match_score: 90, matching_attributes: [], explanation: 'x', item: { ...item, image_url: '/uploads/demo-laptop.jpg' } }} />
    </MemoryRouter>,
  )
  expect(screen.getByRole('img', { name: 'Black Dell Laptop' })).toHaveAttribute('src', expect.stringContaining('/uploads/demo-laptop.jpg'))
})
