import { createSlice } from '@reduxjs/toolkit'

const initialState = {
  sidebarOpen: true,
  notifications: [],
  activeTab: 'form',
  toolStatus: null,
}

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen
    },
    addNotification: (state, action) => {
      state.notifications.push({
        id: Date.now().toString(),
        type: action.payload.type || 'info',
        message: action.payload.message,
        timestamp: new Date().toISOString(),
      })
    },
    removeNotification: (state, action) => {
      state.notifications = state.notifications.filter(
        (n) => n.id !== action.payload
      )
    },
    clearNotifications: (state) => {
      state.notifications = []
    },
    setToolStatus: (state, action) => {
      state.toolStatus = action.payload
    },
  },
})

export const {
  toggleSidebar,
  addNotification,
  removeNotification,
  clearNotifications,
  setToolStatus,
} = uiSlice.actions

export const selectUi = (state) => state.ui

export default uiSlice.reducer
