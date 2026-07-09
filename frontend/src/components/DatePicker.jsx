import React from 'react'

export default function DatePicker({ value, onChange, label = 'Date' }) {
  return (
    <div>
      <label className="crm-label">{label}</label>
      <input
        type="date"
        className="crm-input"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  )
}
