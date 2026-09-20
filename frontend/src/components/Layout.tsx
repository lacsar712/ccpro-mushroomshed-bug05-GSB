import { A, useNavigate } from '@solidjs/router'
import { For, type ParentProps } from 'solid-js'
import { clearToken } from '../api/client'

const links = [
  { href: '/', label: '看板', end: true },
  { href: '/sheds', label: '菇房' },
  { href: '/rooms', label: '出菇室' },
  { href: '/climate-logs', label: '环境记录' },
  { href: '/flush-harvests', label: '采收记录' },
]

export default function Layout(props: ParentProps) {
  const navigate = useNavigate()

  return (
    <div class="shell">
      <aside class="sidebar">
        <div class="brand">
          <div class="brand-mark" />
          <div>
            <div class="brand-title">MushroomShed</div>
            <div class="brand-sub">菇房出菇台账</div>
          </div>
        </div>
        <nav class="nav">
          <For each={links}>
            {(l) => (
              <A href={l.href} end={l.end} class="nav-link" activeClass="active">
                {l.label}
              </A>
            )}
          </For>
        </nav>
        <button
          type="button"
          class="logout-btn"
          onClick={() => {
            clearToken()
            navigate('/login')
          }}
        >
          退出登录
        </button>
      </aside>
      <main class="main">{props.children}</main>
    </div>
  )
}
