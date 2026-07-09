import { createSlice } from '@reduxjs/toolkit'

const initialState = {
  hcp_name: '',
  interaction_type: '',
  date: '',
  time: '',
  attendees: [],
  topics: '',
  materials: [],
  samples: [],
  sentiment: '',
  outcomes: '',
  follow_up_action: '',
  next_meeting: '',
  priority: 'medium',
  history: [],
  historyIndex: -1,
}

const interactionSlice = createSlice({
  name: 'interaction',
  initialState,
  reducers: {
    setField: (state, action) => {
      const { field, value } = action.payload
      state[field] = value
    },
    setMultipleFields: (state, action) => {
      const fields = action.payload
      Object.entries(fields).forEach(([key, value]) => {
        if (value !== undefined && value !== null && key in state) {
          state[key] = value
        }
      })
    },
    clearFields: (state, action) => {
      const fieldsToClear = action.payload
      fieldsToClear.forEach((field) => {
        if (field in state) {
          state[field] = Array.isArray(state[field]) ? [] : ''
        }
      })
    },
    clearAll: () => initialState,
    pushHistory: (state) => {
      const snapshot = {}
      Object.keys(initialState).forEach((key) => {
        if (key !== 'history' && key !== 'historyIndex') {
          snapshot[key] = state[key]
        }
      })
      state.history = state.history.slice(0, state.historyIndex + 1)
      state.history.push(snapshot)
      if (state.history.length > 50) {
        state.history.shift()
      }
      state.historyIndex = state.history.length - 1
    },
    undo: (state) => {
      if (state.historyIndex > 0) {
        state.historyIndex -= 1
        const snapshot = state.history[state.historyIndex]
        Object.keys(snapshot).forEach((key) => {
          state[key] = snapshot[key]
        })
      }
    },
    redo: (state) => {
      if (state.historyIndex < state.history.length - 1) {
        state.historyIndex += 1
        const snapshot = state.history[state.historyIndex]
        Object.keys(snapshot).forEach((key) => {
          state[key] = snapshot[key]
        })
      }
    },
  },
})

export const {
  setField,
  setMultipleFields,
  clearFields,
  clearAll,
  pushHistory,
  undo,
  redo,
} = interactionSlice.actions

export const selectInteraction = (state) => state.interaction

export default interactionSlice.reducer
