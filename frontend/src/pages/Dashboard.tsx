import { createSignal, onMount } from 'solid-js'
import { api } from '../api/client'
import type { DashboardStats } from '../types'

export default function Dashboard() {
  const [stats, setStats] = createSignal<DashboardStats | null>(null)
  const [error, setError] = createSignal('')

  onMount(() => {
    api<DashboardStats>('/api/dashboard/stats')
      .then(setStats)
      .catch((e) => setError(e.message))
  })

  return (
    <div>
      <header class="page-header">
        <h1>运行看板</h1>
        <p class="muted">出菇室状态 · 近 24h 环境 · 近 7 日采收</p>
      </header>
      {error() && <div class="error">{error()}</div>}
      <div class="stat-grid">
        <div class="stat-card">
          <div class="stat-label">菇房总数</div>
          <div class="stat-value">{stats()?.shedTotal ?? '—'}</div>
        </div>
        <div class="stat-card accent">
          <div class="stat-label">出菇中 (fruiting)</div>
          <div class="stat-value">{stats()?.fruitingRoomCount ?? '—'}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">近 24h 环境记录</div>
          <div class="stat-value">{stats()?.climateLast24h ?? '—'}</div>
        </div>
        <div class="stat-card warn">
          <div class="stat-label">近 7 日采收总量 (kg)</div>
          <div class="stat-value">
            {stats() ? stats()!.harvestKgLast7d.toFixed(2) : '—'}
          </div>
        </div>
      </div>
    </div>
  )
}
