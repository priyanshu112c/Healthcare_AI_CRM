import React from 'react'

export default function TimePicker({ value, onChange, label = 'Time' }) {
  return (
    <div>
      <label className="crm-label">{label}</label>
      <input
        type="time"
        className="crm-input"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  )
}
