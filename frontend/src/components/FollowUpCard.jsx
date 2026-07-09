import React from 'react'

const ACTION_OPTIONS = ['Meeting', 'Call', 'Email', 'Reminder', 'Follow-up']

function isValidAction(val) {
  return ACTION_OPTIONS.includes(val)
}

function isValidDate(val) {
  return /^\d{4}-\d{2}-\d{2}$/.test(val) && !isNaN(Date.parse(val))
}

export default function FollowUpCard({ action, nextMeeting, onActionChange, onNextMeetingChange }) {
  return (
    <div className="bg-gray-50 rounded-lg border border-gray-200 p-4 space-y-3">
      <h4 className="text-sm font-medium text-gray-700 flex items-center gap-1.5">
        <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        Follow Up Actions
      </h4>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div>
          <label className="text-xs text-gray-500 mb-1 block">Action Type</label>
          {isValidAction(action) ? (
            <select
              className="crm-input text-sm"
              value={action}
              onChange={(e) => onActionChange(e.target.value)}
            >
              <option value="">Select...</option>
              {ACTION_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
          ) : (
            <input
              type="text"
              className="crm-input text-sm"
              placeholder="e.g. Meeting next month"
              value={action}
              onChange={(e) => onActionChange(e.target.value)}
            />
          )}
        </div>
        <div>
          <label className="text-xs text-gray-500 mb-1 block">Next Meeting</label>
          {isValidDate(nextMeeting) ? (
            <input
              type="date"
              className="crm-input text-sm"
              value={nextMeeting}
              onChange={(e) => onNextMeetingChange(e.target.value)}
            />
          ) : (
            <input
              type="text"
              className="crm-input text-sm"
              placeholder="e.g. 2026-08-15 or next month"
              value={nextMeeting}
              onChange={(e) => onNextMeetingChange(e.target.value)}
            />
          )}
        </div>
      </div>
    </div>
  )
}
