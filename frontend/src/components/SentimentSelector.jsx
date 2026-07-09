import React from 'react'

const sentiments = [
  { value: 'Positive', emoji: '😊', color: 'text-green-600', bg: 'bg-green-50 border-green-200', ring: 'ring-green-500' },
  { value: 'Neutral', emoji: '😐', color: 'text-gray-600', bg: 'bg-gray-50 border-gray-200', ring: 'ring-gray-400' },
  { value: 'Negative', emoji: '😢', color: 'text-red-600', bg: 'bg-red-50 border-red-200', ring: 'ring-red-500' },
]

export default function SentimentSelector({ value, onChange }) {
  return (
    <div>
      <label className="crm-label">Observed Sentiment</label>
      <div className="flex flex-col sm:flex-row gap-2 mt-1">
        {sentiments.map((s) => (
          <div key={s.value} className="flex-1 flex items-center gap-1.5">
            <label className="cursor-pointer">
              <input
                type="radio"
                name="sentiment"
                value={s.value}
                checked={value === s.value}
                onChange={() => onChange(s.value)}
                className={`appearance-none w-3.5 h-3.5 rounded-full border-2 shrink-0 ${
                  value === s.value ? `${s.ring} ring-2 border-transparent` : 'border-gray-300'
                }`}
              />
            </label>
            <div
              className={`flex items-center justify-center gap-1 px-3 py-2 rounded-lg border text-sm font-medium transition-all duration-200 flex-1 ${
                value === s.value
                  ? `${s.bg} ${s.color} border-2`
                  : 'border-gray-200 text-gray-500'
              }`}
            >
              <span>{s.emoji}</span>
              <span>{s.value}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
