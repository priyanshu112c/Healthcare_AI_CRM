import { createSlice } from '@reduxjs/toolkit'

const initialState = {
  messages: [],
  sessionId: null,
  isLoading: false,
  isStreaming: false,
  error: null,
}

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    addMessage: (state, action) => {
      state.messages.push(action.payload)
    },
    setLoading: (state, action) => {
      state.isLoading = action.payload
    },
    setStreaming: (state, action) => {
      state.isStreaming = action.payload
    },
    setSessionId: (state, action) => {
      state.sessionId = action.payload
    },
    setError: (state, action) => {
      state.error = action.payload
    },
    clearChat: (state) => {
      state.messages = []
      state.sessionId = null
      state.error = null
    },
  },
})

export const {
  addMessage,
  setLoading,
  setStreaming,
  setSessionId,
  setError,
  clearChat,
} = chatSlice.actions

export const selectChat = (state) => state.chat

export default chatSlice.reducer
