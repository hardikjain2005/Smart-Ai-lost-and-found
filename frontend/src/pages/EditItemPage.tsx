import { useNavigate, useParams } from 'react-router-dom'
import { ItemForm } from '../components/ItemForm'
import { ErrorMessage } from '../components/ui/ErrorMessage'
import { Loading } from '../components/ui/Loading'
import { useAsync } from '../hooks/useAsync'
import { getItem, updateItem } from '../services/itemService'
import type { ItemInput } from '../services/types'

export function EditItemPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const item = useAsync(() => getItem(id!), [id])

  if (item.loading) return <Loading />
  if (item.error || !item.data) return <ErrorMessage message={item.error ?? 'Not found'} />
  const i = item.data
  const initial: ItemInput = {
    title: i.title, type: i.type, category: i.category, location: i.location, date: i.date,
    brand: i.brand ?? '', color: i.color ?? '', description: i.description ?? '',
    time: i.time?.slice(0, 5) ?? '', image_url: i.image_url ?? '', private_details: i.private_details ?? '', visibility: i.visibility,
  }
  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <h1 className="text-2xl font-bold">Edit item</h1>
      <ItemForm
        initial={initial}
        submitLabel="Save changes"
        onSubmit={async (input) => {
          await updateItem(i.id, input)
          navigate(`/items/${i.id}`)
        }}
      />
    </div>
  )
}
