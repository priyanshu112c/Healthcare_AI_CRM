import React from 'react'
import { useDispatch } from 'react-redux'
import { undo, redo, clearAll } from '../redux/interactionSlice'
import { clearChat } from '../redux/chatSlice'
import { addNotification } from '../redux/uiSlice'

export default function Toolbar() {
  const dispatch = useDispatch()

  const handleUndo = () => {
    dispatch(undo())
    dispatch(addNotification({ type: 'info', message: 'Undo last change' }))
  }

  const handleRedo = () => {
    dispatch(redo())
    dispatch(addNotification({ type: 'info', message: 'Redo change' }))
  }

  const handleClear = () => {
    dispatch(clearAll())
    dispatch(clearChat())
    dispatch(addNotification({ type: 'info', message: 'Reset all' }))
  }

  return (
    <div className="flex items-center gap-1.5 px-4 py-2 border-b border-gray-100 bg-white">
      <button
        className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-500 transition-colors"
        onClick={handleUndo}
        title="Undo"
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
        </svg>
      </button>
      <button
        className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-500 transition-colors"
        onClick={handleRedo}
        title="Redo"
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 10H11a8 8 0 00-8 8v2m18-10l-6 6m6-6l-6-6" />
        </svg>
      </button>
      <div className="w-px h-5 bg-gray-200 mx-1" />
      <button
        className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-500 transition-colors"
        onClick={handleClear}
        title="Reset"
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
        </svg>
      </button>
    </div>
  )
}
