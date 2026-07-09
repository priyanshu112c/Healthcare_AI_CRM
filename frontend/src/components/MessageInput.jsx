import React, { useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { addMessage, setLoading, setStreaming, setSessionId, setError } from '../redux/chatSlice'
import { setMultipleFields, pushHistory } from '../redux/interactionSlice'
import { setTool, setProcessing, setLastToolResult } from '../redux/agentSlice'
import { addNotification } from '../redux/uiSlice'
import { api } from '../services/api'

export default function MessageInput() {
  const [text, setText] = useState('')
  const dispatch = useDispatch()
  const { sessionId, isLoading } = useSelector((s) => s.chat)

  const handleSend = async () => {
    if (!text.trim() || isLoading) return

    const userMsg = {
      role: 'user',
      content: text.trim(),
      timestamp: new Date().toISOString(),
    }
    dispatch(addMessage(userMsg))
    dispatch(setLoading(true))
    dispatch(setStreaming(true))
    dispatch(setProcessing(true))

    const currentText = text
    setText('')

    try {
      const result = await api.chat(currentText, sessionId)

      if (!sessionId) {
        dispatch(setSessionId(result.session_id))
      }

      if (result.tool_called) {
        dispatch(setTool(result.tool_called))
        dispatch(setLastToolResult(result.tool_result))
      }

      if (result.interaction && Object.keys(result.interaction).length > 0) {
        dispatch(pushHistory())
        dispatch(setMultipleFields(result.interaction))
        const toolName = result.tool_called
          ? result.tool_called.replace(/_/g, ' ')
          : ''
        const label = toolName ? toolName.charAt(0).toUpperCase() + toolName.slice(1) : 'AI'
        dispatch(addNotification({
          type: 'success',
          message: `${label} completed! Form updated.`,
        }))
      }

      dispatch(addMessage({
        role: 'assistant',
        content: result.response,
        tool: result.tool_called,
        timestamp: new Date().toISOString(),
      }))
    } catch (err) {
      dispatch(setError(err.message))
      dispatch(addNotification({
        type: 'error',
        message: `Error: ${err.message}`,
      }))
    } finally {
      dispatch(setLoading(false))
      dispatch(setStreaming(false))
      dispatch(setProcessing(false))
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex items-end gap-2">
      <textarea
        className="flex-1 crm-input resize-none min-h-[40px] max-h-[120px] py-2.5"
        placeholder="Describe your interaction... (e.g. 'Today I met Dr. Smith and discussed Product X')"
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        rows={1}
        disabled={isLoading}
      />
      <button
        className={`crm-btn-primary h-[40px] px-4 flex items-center gap-1 ${
          isLoading ? 'opacity-50 cursor-not-allowed' : ''
        }`}
        onClick={handleSend}
        disabled={isLoading}
      >
        {isLoading ? (
          <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
        ) : (
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        )}
      </button>
    </div>
  )
}
