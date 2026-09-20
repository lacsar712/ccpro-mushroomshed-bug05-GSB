import { Navigate, Route } from '@solidjs/router'
import { Show, type ParentProps, type JSX } from 'solid-js'
import { getToken } from './api/client'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Sheds from './pages/Sheds'
import Rooms from './pages/Rooms'
import ClimateLogs from './pages/ClimateLogs'
import FlushHarvests from './pages/FlushHarvests'

function AuthedLayout(props: ParentProps): JSX.Element {
  return (
    <Show when={getToken()} fallback={<Navigate href="/login" />}>
      <Layout>{props.children}</Layout>
    </Show>
  )
}

export default function App() {
  return (
    <>
      <Route path="/login" component={Login} />
      <Route path="/" component={AuthedLayout}>
        <Route path="/" component={Dashboard} />
        <Route path="/sheds" component={Sheds} />
        <Route path="/rooms" component={Rooms} />
        <Route path="/climate-logs" component={ClimateLogs} />
        <Route path="/flush-harvests" component={FlushHarvests} />
      </Route>
      <Route path="*404" component={() => <Navigate href="/" />} />
    </>
  )
}
