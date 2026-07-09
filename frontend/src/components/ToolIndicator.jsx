import React from 'react'
import { useSelector } from 'react-redux'
import { selectAgent } from '../redux/agentSlice'

const toolColors = {
  log_interaction: 'bg-blue-100 text-blue-700 border-blue-200',
  edit_interaction: 'bg-amber-100 text-amber-700 border-amber-200',
  clear_fields: 'bg-red-100 text-red-700 border-red-200',
  suggest_follow_up: 'bg-purple-100 text-purple-700 border-purple-200',
  interaction_summary: 'bg-green-100 text-green-700 border-green-200',
  search_hcp: 'bg-cyan-100 text-cyan-700 border-cyan-200',
  missing_field_detection: 'bg-orange-100 text-orange-700 border-orange-200',
  generate_email: 'bg-indigo-100 text-indigo-700 border-indigo-200',
  generate_next_steps: 'bg-teal-100 text-teal-700 border-teal-200',
  compliance_check: 'bg-rose-100 text-rose-700 border-rose-200',
}

export default function ToolIndicator() {
  const { currentTool, isProcessing } = useSelector(selectAgent)

  if (!currentTool && !isProcessing) return null

  return (
    <div className="mb-2">
      {isProcessing && (
        <div className="flex items-center gap-2 text-xs text-gray-400 mb-1">
          <svg className="animate-spin h-3 w-3" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          Processing...
        </div>
      )}
      {currentTool && (
        <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md border text-xs font-medium ${
          toolColors[currentTool] || 'bg-gray-100 text-gray-700 border-gray-200'
        }`}>
          <span className="w-1.5 h-1.5 rounded-full bg-current" />
          {currentTool.replace(/_/g, ' ')}
        </div>
      )}
    </div>
  )
}
