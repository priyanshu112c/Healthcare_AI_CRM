import React, { useRef, useEffect } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { selectChat, clearChat } from '../redux/chatSlice'
import { addNotification } from '../redux/uiSlice'
import ChatBubble from './ChatBubble'
import MessageInput from './MessageInput'
import ToolIndicator from './ToolIndicator'
import Loader from './Loader'

export default function ChatWindow() {
  const dispatch = useDispatch()
  const { messages, isLoading, isStreaming } = useSelector(selectChat)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isStreaming])

  return (
    <div className="flex flex-col h-full">
      <div className="border-b border-gray-100 px-4 py-3 bg-white">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-500" />
          <h3 className="font-medium text-gray-900 text-sm">AI Assistant</h3>
          <button
            className="ml-auto text-xs text-gray-400 hover:text-red-600 transition-colors"
            onClick={() => {
              dispatch(clearChat())
              dispatch(addNotification({ type: 'info', message: 'Chat cleared.' }))
            }}
            title="Clear chat"
          >
            Clear
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-3 sm:px-4 py-4 space-y-3 bg-gray-50/50">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full text-gray-400 text-sm">
            <div className="text-center">
              <p className="text-lg mb-1">👋</p>
              <p>Describe your interaction with an HCP</p>
              <p className="text-xs mt-1">e.g. "Today I met Dr. Smith and discussed Product X"</p>
            </div>
          </div>
        )}
        {messages.map((msg, idx) => (
          <ChatBubble key={idx} message={msg} />
        ))}
        {isStreaming && (
          <div className="flex items-center gap-2 text-gray-400 text-sm py-2">
            <Loader size="sm" />
            <span className="typing-animation">AI is thinking</span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="border-t border-gray-100 px-4 py-3 bg-white">
        <ToolIndicator />
        <MessageInput />
      </div>
    </div>
  )
}
