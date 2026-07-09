import React, { useState, useCallback } from 'react'

const HCP_SUGGESTIONS = [
  'Dr. Smith',
  'Dr. John Williams',
  'Dr. Sarah Johnson',
  'Dr. Michael Chen',
  'Dr. Emily Brown',
  'Dr. James Wilson',
  'Dr. Lisa Garcia',
  'Dr. Robert Taylor',
  'Dr. Jennifer Martinez',
  'Dr. David Anderson',
]

export default function Autocomplete({ value, onChange }) {
  const [suggestions, setSuggestions] = useState([])
  const [isOpen, setIsOpen] = useState(false)

  const handleChange = useCallback((e) => {
    const val = e.target.value
    onChange(val)
    if (val.length > 0) {
      const filtered = HCP_SUGGESTIONS.filter((s) =>
        s.toLowerCase().includes(val.toLowerCase())
      )
      setSuggestions(filtered)
      setIsOpen(filtered.length > 0)
    } else {
      setSuggestions([])
      setIsOpen(false)
    }
  }, [onChange])

  const handleSelect = (suggestion) => {
    onChange(suggestion)
    setSuggestions([])
    setIsOpen(false)
  }

  return (
    <div className="relative">
      <input
        type="text"
        className="crm-input"
        placeholder="Search HCP by name..."
        value={value}
        onChange={handleChange}
        onFocus={() => {
          if (suggestions.length > 0) setIsOpen(true)
        }}
        onBlur={() => setTimeout(() => setIsOpen(false), 200)}
      />
      {isOpen && (
        <div className="absolute z-10 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg max-h-48 overflow-y-auto">
          {suggestions.map((s, idx) => (
            <button
              key={idx}
              type="button"
              className="w-full text-left px-3 py-2 text-sm hover:bg-blue-50 text-gray-700 transition-colors"
              onMouseDown={() => handleSelect(s)}
            >
              {s}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
