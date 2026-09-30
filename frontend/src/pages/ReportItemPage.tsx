import { useNavigate } from 'react-router-dom'
import { ItemForm } from '../components/ItemForm'
import { createItem } from '../services/itemService'
import type { ItemType } from '../services/types'

export function ReportItemPage({ type }: { type: ItemType }) {
  const navigate = useNavigate()
  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <h1 className="text-2xl font-bold">Report {type === 'LOST' ? 'Lost' : 'Found'} Item</h1>
      <ItemForm
        key={type}
        initial={{ type }}
        submitLabel="Submit report"
        onSubmit={async (input) => {
          const item = await createItem(input)
          navigate(`/items/${item.id}`)
        }}
      />
    </div>
  )
}
