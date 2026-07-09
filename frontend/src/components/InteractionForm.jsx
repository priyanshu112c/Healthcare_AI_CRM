import React, { useState } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { useForm } from 'react-hook-form'
import { selectInteraction, setField, clearAll } from '../redux/interactionSlice'
import { addNotification } from '../redux/uiSlice'
import { api } from '../services/api'
import SentimentSelector from './SentimentSelector'
import FollowUpCard from './FollowUpCard'
import Autocomplete from './Autocomplete'

const interactionTypes = ['Meeting', 'Call', 'Email', 'Conference', 'Follow-up']
const priorities = ['low', 'medium', 'high']

export default function InteractionForm() {
  const dispatch = useDispatch()
  const interaction = useSelector(selectInteraction)
  const [saving, setSaving] = useState(false)
  const { register, handleSubmit, setValue } = useForm({
    values: interaction,
  })

  const onSubmit = async (data) => {
    setSaving(true)
    try {
      await api.saveInteraction(data)
      dispatch(clearAll())
      dispatch(addNotification({
        type: 'success',
        message: 'Interaction saved to database successfully!',
      }))
    } catch (err) {
      dispatch(addNotification({
        type: 'error',
        message: `Failed to save: ${err.message}`,
      }))
    } finally {
      setSaving(false)
    }
  }

  const handleClear = () => {
    dispatch(clearAll())
    dispatch(addNotification({
      type: 'info',
      message: 'Form cleared.',
    }))
  }

  const handleFieldChange = (field) => (e) => {
    dispatch(setField({ field, value: e.target.value }))
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-xl font-semibold text-gray-900">Interaction Details</h2>
        <span className="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded-full">
          AI-Controlled Form
        </span>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="crm-card space-y-5">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="crm-label">HCP Name</label>
            <Autocomplete
              value={interaction.hcp_name}
              onChange={(val) => dispatch(setField({ field: 'hcp_name', value: val }))}
            />
          </div>

          <div>
            <label className="crm-label">Interaction Type</label>
            <select
              className="crm-input"
              value={interaction.interaction_type}
              onChange={handleFieldChange('interaction_type')}
            >
              <option value="">Select type...</option>
              {interactionTypes.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>

          <div className="sm:col-span-2 grid grid-cols-2 gap-2">
            <div>
              <label className="crm-label">Date</label>
              <input
                type="date"
                className="crm-input"
                value={interaction.date}
                onChange={handleFieldChange('date')}
              />
            </div>
            <div>
              <label className="crm-label">Time</label>
              <input
                type="time"
                className="crm-input"
                value={interaction.time}
                onChange={handleFieldChange('time')}
              />
            </div>
          </div>

          <div className="sm:col-span-2">
            <label className="crm-label">Attendees</label>
            <input
              type="text"
              className="crm-input"
              placeholder="e.g. Dr. Smith, Nurse Jane"
              value={interaction.attendees?.join(', ') || ''}
              onChange={(e) => dispatch(setField({
                field: 'attendees',
                value: e.target.value.split(',').map(s => s.trim()).filter(Boolean),
              }))}
            />
          </div>

          <div className="sm:col-span-2">
            <label className="crm-label">Topics Discussed</label>
            <textarea
              className="crm-input min-h-[80px] resize-y"
              placeholder="What was discussed during the interaction?"
              value={interaction.topics}
              onChange={handleFieldChange('topics')}
            />
          </div>

          <div>
            <label className="crm-label">Materials Shared</label>
            <input
              type="text"
              className="crm-input"
              placeholder="e.g. Brochure, Clinical Paper"
              value={interaction.materials?.join(', ') || ''}
              onChange={(e) => dispatch(setField({
                field: 'materials',
                value: e.target.value.split(',').map(s => s.trim()).filter(Boolean),
              }))}
            />
          </div>

          <div>
            <label className="crm-label">Samples Distributed</label>
            <input
              type="text"
              className="crm-input"
              placeholder="e.g. Product X 10mg x 30"
              value={interaction.samples?.join(', ') || ''}
              onChange={(e) => dispatch(setField({
                field: 'samples',
                value: e.target.value.split(',').map(s => s.trim()).filter(Boolean),
              }))}
            />
          </div>

          <div>
            <SentimentSelector
              value={interaction.sentiment}
              onChange={(val) => dispatch(setField({ field: 'sentiment', value: val }))}
            />
          </div>

          <div>
            <label className="crm-label">Priority</label>
            <select
              className="crm-input"
              value={interaction.priority}
              onChange={handleFieldChange('priority')}
            >
              {priorities.map((p) => (
                <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>
              ))}
            </select>
          </div>

          <div className="sm:col-span-2">
            <label className="crm-label">Outcomes</label>
            <textarea
              className="crm-input min-h-[60px] resize-y"
              placeholder="Key outcomes of the interaction"
              value={interaction.outcomes}
              onChange={handleFieldChange('outcomes')}
            />
          </div>

          <div className="sm:col-span-2">
            <FollowUpCard
              action={interaction.follow_up_action}
              nextMeeting={interaction.next_meeting}
              onActionChange={(val) => dispatch(setField({ field: 'follow_up_action', value: val }))}
              onNextMeetingChange={(val) => dispatch(setField({ field: 'next_meeting', value: val }))}
            />
          </div>
        </div>

        <div className="border-t border-gray-100 pt-4 flex items-center justify-between">
          <div>
            <button type="button" className="crm-btn-secondary mr-2" onClick={handleClear}>
              Clear
            </button>
          </div>
          <button type="submit" className="crm-btn-primary" disabled={saving}>
            {saving ? 'Saving...' : 'Save Interaction'}
          </button>
        </div>
      </form>
    </div>
  )
}
