import { createSignal, onMount } from 'solid-js'
import { For } from 'solid-js'
import { api } from '../api/client'
import type { Shed } from '../types'

const empty = { name: '', location: '', notes: '' }

export default function Sheds() {
  const [rows, setRows] = createSignal<Shed[]>([])
  const [form, setForm] = createSignal({ ...empty })
  const [error, setError] = createSignal('')

  async function load() {
    const data = await api<Shed[]>('/api/sheds')
    setRows(data)
  }

  onMount(() => {
    load().catch((e) => setError(e.message))
  })

  async function onSubmit(e: Event) {
    e.preventDefault()
    setError('')
    try {
      await api('/api/sheds', {
        method: 'POST',
        body: JSON.stringify(form()),
      })
      setForm({ ...empty })
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : '保存失败')
    }
  }

  async function remove(id: number) {
    if (!confirm('确认删除该菇房？')) return
    try {
      await api(`/api/sheds/${id}`, { method: 'DELETE' })
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : '删除失败')
    }
  }

  return (
    <div>
      <header class="page-header">
        <h1>菇房</h1>
        <p class="muted">登记场区位置与备注</p>
      </header>
      {error() && <div class="error">{error()}</div>}

      <form class="panel form-grid" onSubmit={onSubmit}>
        <label>
          名称
          <input
            value={form().name}
            onInput={(e) => setForm({ ...form(), name: e.currentTarget.value })}
            required
          />
        </label>
        <label>
          位置
          <input
            value={form().location}
            onInput={(e) => setForm({ ...form(), location: e.currentTarget.value })}
            required
          />
        </label>
        <label class="span-2">
          备注
          <input
            value={form().notes ?? ''}
            onInput={(e) => setForm({ ...form(), notes: e.currentTarget.value })}
          />
        </label>
        <button type="submit" class="btn primary">
          新增菇房
        </button>
      </form>

      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>名称</th>
              <th>位置</th>
              <th>备注</th>
              <th />
            </tr>
          </thead>
          <tbody>
            <For each={rows()}>
              {(r) => (
                <tr>
                  <td>{r.id}</td>
                  <td>{r.name}</td>
                  <td>{r.location}</td>
                  <td>{r.notes || '—'}</td>
                  <td>
                    <button type="button" class="btn ghost" onClick={() => remove(r.id)}>
                      删除
                    </button>
                  </td>
                </tr>
              )}
            </For>
          </tbody>
        </table>
      </div>
    </div>
  )
}
