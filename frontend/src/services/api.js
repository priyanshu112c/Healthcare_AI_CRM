const API_BASE = '/api/v1'

async function request(method, path, body = null, timeoutMs = 180000) {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), timeoutMs)
  const options = {
    method,
    headers: { 'Content-Type': 'application/json' },
    signal: controller.signal,
  }
  if (body) {
    options.body = JSON.stringify(body)
  }
  try {
    const res = await fetch(`${API_BASE}${path}`, options)
    if (!res.ok) {
      throw new Error(`API error: ${res.status} ${res.statusText}`)
    }
    return res.json()
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new Error('Request timed out after 3 minutes. The AI is taking too long to respond.')
    }
    throw err
  } finally {
    clearTimeout(timeout)
  }
}

export const api = {
  chat: (message, sessionId = null) =>
    request('POST', '/chat', { message, session_id: sessionId }),

  executeTool: (tool, args) =>
    request('POST', '/tool', { tool, args }),

  saveInteraction: (data) => request('POST', '/interaction', data),

  health: () => request('GET', '/health'),

  getSchema: () => request('GET', '/schema'),

  getLangGraph: () => request('GET', '/langgraph'),
}
