import React, { useEffect } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { selectUi, removeNotification } from '../redux/uiSlice'

const typeStyles = {
  success: 'bg-green-50 border-green-200 text-green-800',
  error: 'bg-red-50 border-red-200 text-red-800',
  info: 'bg-blue-50 border-blue-200 text-blue-800',
  warning: 'bg-amber-50 border-amber-200 text-amber-800',
}

const typeIcons = {
  success: '✓',
  error: '✕',
  info: 'ℹ',
  warning: '⚠',
}

export default function Notification() {
  const { notifications } = useSelector(selectUi)
  const dispatch = useDispatch()

  useEffect(() => {
    if (notifications.length > 0) {
      const timer = setTimeout(() => {
        dispatch(removeNotification(notifications[0].id))
      }, 4000)
      return () => clearTimeout(timer)
    }
  }, [notifications, dispatch])

  if (notifications.length === 0) return null

  return (
    <div className="fixed top-4 right-2 sm:right-4 z-50 space-y-2 max-w-[calc(100vw-16px)] sm:max-w-sm">
      {notifications.map((n) => (
        <div
          key={n.id}
          className={`flex items-start gap-2 px-4 py-3 rounded-lg border shadow-lg text-sm ${typeStyles[n.type]}`}
        >
          <span className="font-bold">{typeIcons[n.type]}</span>
          <p className="flex-1">{n.message}</p>
          <button
            className="text-current opacity-60 hover:opacity-100"
            onClick={() => dispatch(removeNotification(n.id))}
          >
            ✕
          </button>
        </div>
      ))}
    </div>
  )
}
