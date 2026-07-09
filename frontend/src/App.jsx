import React from 'react'
import Home from './pages/Home'
import Notification from './components/Notification'
import Toolbar from './components/Toolbar'

export default function App() {
  return (
    <>
      <Notification />
      <Toolbar />
      <Home />
    </>
  )
}
