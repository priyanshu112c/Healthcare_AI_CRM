import React from 'react'

const statusStyles = {
  success: 'bg-green-100 text-green-700 border-green-200',
  error: 'bg-red-100 text-red-700 border-red-200',
  warning: 'bg-amber-100 text-amber-700 border-amber-200',
  info: 'bg-blue-100 text-blue-700 border-blue-200',
  neutral: 'bg-gray-100 text-gray-600 border-gray-200',
}

export default function StatusBadge({ status = 'neutral', label, icon }) {
  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border ${
        statusStyles[status] || statusStyles.neutral
      }`}
    >
      {icon && <span>{icon}</span>}
      {label || status}
    </span>
  )
}
