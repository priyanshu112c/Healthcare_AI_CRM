import React from 'react'
import SplitLayout from '../components/SplitLayout'
import InteractionForm from '../components/InteractionForm'
import ChatWindow from '../components/ChatWindow'

export default function Home() {
  return (
    <div className="h-[calc(100dvh-41px)]">
      <SplitLayout
        leftPanel={<InteractionForm />}
        rightPanel={<ChatWindow />}
      />
    </div>
  )
}
