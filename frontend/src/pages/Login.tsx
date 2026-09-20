import { createSignal } from 'solid-js'
import { useNavigate } from '@solidjs/router'
import { login, setToken } from '../api/client'

export default function Login() {
  const navigate = useNavigate()
  const [username, setUsername] = createSignal('admin')
  const [password, setPassword] = createSignal('123456')
  const [error, setError] = createSignal('')
  const [loading, setLoading] = createSignal(false)

  async function onSubmit(e: Event) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await login(username(), password())
      setToken(res.access_token)
      navigate('/')
    } catch (err) {
      setError(err instanceof Error ? err.message : '登录失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div class="login-page">
      <div class="login-panel">
        <div class="login-cap" />
        <h1>MushroomShed</h1>
        <p class="muted">菇房出菇 · 环境记录与采收台账</p>
        <form onSubmit={onSubmit} class="form-stack">
          <label>
            用户名
            <input
              value={username()}
              onInput={(e) => setUsername(e.currentTarget.value)}
              required
            />
          </label>
          <label>
            密码
            <input
              type="password"
              value={password()}
              onInput={(e) => setPassword(e.currentTarget.value)}
              required
            />
          </label>
          {error() && <div class="error">{error()}</div>}
          <button type="submit" class="btn primary" disabled={loading()}>
            {loading() ? '登录中…' : '进入台账'}
          </button>
        </form>
        <p class="hint">演示账号：admin / fruiter，密码均为 123456</p>
      </div>
    </div>
  )
}
