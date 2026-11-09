import type { AnalysisState, QueryPlan, VisualizationSpec } from '../types/analysis'

type Listener = (patch: Partial<AnalysisState>) => void

export async function streamAnalysis(question: string, onEvent: Listener) {
  const response = await fetch('/api/v1/analysis/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-user-id': 'u_demo',
      'x-username': 'dawei',
      'x-user-role': 'regional_manager'
    },
    body: JSON.stringify({ question })
  })

  if (!response.ok || !response.body) {
    throw new Error(`请求失败: ${response.status}`)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  let eventName = 'message'

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const chunks = buffer.split('\n\n')
    buffer = chunks.pop() || ''

    for (const chunk of chunks) {
      const lines = chunk.split('\n')
      let dataLine = ''

      for (const line of lines) {
        if (line.startsWith('event:')) eventName = line.slice(6).trim()
        if (line.startsWith('data:')) dataLine += line.slice(5).trim()
      }

      if (!dataLine) continue
      const data = JSON.parse(dataLine)

      if (eventName === 'status') {
        onEvent({ status: data.message })
      } else if (eventName === 'plan') {
        onEvent({ plan: data as QueryPlan, status: '查询计划已生成' })
      } else if (eventName === 'data') {
        onEvent({ sql: data.sql, status: '数据查询完成' })
      } else if (eventName === 'visualization') {
        onEvent({ visualization: data as VisualizationSpec, status: '可视化已生成' })
      } else if (eventName === 'insight') {
        onEvent({ insight: data.content, status: '分析结论已生成' })
      } else if (eventName === 'done') {
        onEvent({ traceId: data.trace_id, loading: false, status: '完成' })
      } else if (eventName === 'error') {
        onEvent({ error: data.message, loading: false, status: '失败' })
      }
    }
  }
}
