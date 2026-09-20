import { createSignal, onMount } from 'solid-js'
import { For } from 'solid-js'
import { api } from '../api/client'
import type { ClimateLog, Room } from '../types'

function toLocalInput(iso?: string) {
  const d = iso ? new Date(iso) : new Date()
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}

const empty = {
  roomId: '',
  recordedAt: toLocalInput(),
  tempC: '',
  humidityPct: '',
  co2Ppm: '',
  notes: '',
}

export default function ClimateLogs() {
  const [rows, setRows] = createSignal<ClimateLog[]>([])
  const [rooms, setRooms] = createSignal<Room[]>([])
  const [form, setForm] = createSignal({ ...empty })
  const [error, setError] = createSignal('')

  async function load() {
    const [logs, roomList] = await Promise.all([
      api<ClimateLog[]>('/api/climate-logs'),
      api<Room[]>('/api/rooms'),
    ])
    setRows(logs)
    setRooms(roomList)
  }

  onMount(() => {
    load().catch((e) => setError(e.message))
  })

  async function onSubmit(e: Event) {
    e.preventDefault()
    setError('')
    try {
      await api('/api/climate-logs', {
        method: 'POST',
        body: JSON.stringify({
          roomId: Number(form().roomId),
          recordedAt: new Date(form().recordedAt).toISOString(),
          tempC: Number(form().tempC),
          humidityPct: Number(form().humidityPct),
          co2Ppm: form().co2Ppm ? Number(form().co2Ppm) : null,
          notes: form().notes || null,
        }),
      })
      setForm({ ...empty, recordedAt: toLocalInput() })
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : '保存失败')
    }
  }

  async function remove(id: number) {
    if (!confirm('确认删除该环境记录？')) return
    try {
      await api(`/api/climate-logs/${id}`, { method: 'DELETE' })
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : '删除失败')
    }
  }

  return (
    <div>
      <header class="page-header">
        <h1>环境记录</h1>
        <p class="muted">温湿度与 CO₂；湿度须 1–100</p>
      </header>
      {error() && <div class="error">{error()}</div>}

      <form class="panel form-grid" onSubmit={onSubmit}>
        <label>
          出菇室
          <select
            value={form().roomId}
            onChange={(e) => setForm({ ...form(), roomId: e.currentTarget.value })}
            required
          >
            <option value="">选择出菇室</option>
            <For each={rooms()}>
              {(r) => (
                <option value={String(r.id)}>
                  {r.roomCode} · {r.species}
                </option>
              )}
            </For>
          </select>
        </label>
        <label>
          记录时间
          <input
            type="datetime-local"
            value={form().recordedAt}
            onInput={(e) => setForm({ ...form(), recordedAt: e.currentTarget.value })}
            required
          />
        </label>
        <label>
          温度 (°C)
          <input
            type="number"
            step="0.1"
            value={form().tempC}
            onInput={(e) => setForm({ ...form(), tempC: e.currentTarget.value })}
            required
          />
        </label>
        <label>
          湿度 (%)
          <input
            type="number"
            min="1"
            max="100"
            value={form().humidityPct}
            onInput={(e) => setForm({ ...form(), humidityPct: e.currentTarget.value })}
            required
          />
        </label>
        <label>
          CO₂ (ppm)
          <input
            type="number"
            step="1"
            value={form().co2Ppm}
            onInput={(e) => setForm({ ...form(), co2Ppm: e.currentTarget.value })}
          />
        </label>
        <label class="span-2">
          备注
          <input
            value={form().notes}
            onInput={(e) => setForm({ ...form(), notes: e.currentTarget.value })}
          />
        </label>
        <button type="submit" class="btn primary">
          新增记录
        </button>
      </form>

      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>室 ID</th>
              <th>时间</th>
              <th>温度</th>
              <th>湿度</th>
              <th>CO₂</th>
              <th>备注</th>
              <th />
            </tr>
          </thead>
          <tbody>
            <For each={rows()}>
              {(r) => (
                <tr>
                  <td>{r.id}</td>
                  <td>{r.roomId}</td>
                  <td>{new Date(r.recordedAt).toLocaleString()}</td>
                  <td>{r.tempC}</td>
                  <td>{r.humidityPct}%</td>
                  <td>{r.co2Ppm ?? '—'}</td>
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
