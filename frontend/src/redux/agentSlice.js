import { createSlice } from '@reduxjs/toolkit'

const initialState = {
  currentTool: null,
  toolHistory: [],
  isProcessing: false,
  lastToolResult: null,
}

const agentSlice = createSlice({
  name: 'agent',
  initialState,
  reducers: {
    setTool: (state, action) => {
      state.currentTool = action.payload
    },
    addToolHistory: (state, action) => {
      state.toolHistory.push({
        tool: action.payload.tool,
        args: action.payload.args,
        result: action.payload.result,
        timestamp: new Date().toISOString(),
      })
    },
    setProcessing: (state, action) => {
      state.isProcessing = action.payload
    },
    setLastToolResult: (state, action) => {
      state.lastToolResult = action.payload
    },
    clearAgent: () => initialState,
  },
})

export const {
  setTool,
  addToolHistory,
  setProcessing,
  setLastToolResult,
  clearAgent,
} = agentSlice.actions

export const selectAgent = (state) => state.agent

export default agentSlice.reducer
