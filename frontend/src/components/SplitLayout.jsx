import React, { useState } from 'react'

export default function SplitLayout({ leftPanel, rightPanel }) {
  const [tab, setTab] = useState('form')

  return (
    <div className="flex flex-col lg:flex-row h-full w-full overflow-hidden bg-gray-50">
      <div className="hidden lg:flex w-[70%] min-w-0 overflow-y-auto border-r border-gray-200">
        <div className="h-full p-4 xl:p-6 w-full">
          {leftPanel}
        </div>
      </div>
      <div className="hidden lg:flex w-[30%] min-w-0 flex-col bg-white">
        {rightPanel}
      </div>

      <div className="flex lg:hidden flex-col h-full w-full">
        <div className="flex border-b border-gray-200 bg-white shrink-0">
          <button
            className={`flex-1 px-4 py-3 text-sm font-medium text-center transition-colors ${
              tab === 'form'
                ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50/50'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setTab('form')}
          >
            Interaction Form
          </button>
          <button
            className={`flex-1 px-4 py-3 text-sm font-medium text-center transition-colors ${
              tab === 'chat'
                ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50/50'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setTab('chat')}
          >
            AI Assistant
          </button>
        </div>
        <div className="flex-1 overflow-y-auto">
          {tab === 'form' ? (
            <div className="p-4">{leftPanel}</div>
          ) : (
            <div className="h-full flex flex-col">{rightPanel}</div>
          )}
        </div>
      </div>
    </div>
  )
}
