import { FormEvent, useState } from 'react'
import { streamAnalysis } from './api/analysis'
import { VisualizationPanel } from './components/VisualizationPanel'
import type { AnalysisState } from './types/analysis'
import './styles/app.css'

const examples = [
  '帮我看一下今年各区域销售额，用柱状图展示',
  '把本月各产品销售额做成表格',
  '最近6个月销售额趋势怎么样？用折线图',
  '今年各区域销售额占比，用饼图展示',
  '华东本月各产品毛利率做成表格'
]

function App() {
  const [question, setQuestion] = useState(examples[0])
  const [state, setState] = useState<AnalysisState>({
    loading: false,
    status: '等待提问'
  })

  const submit = async (event?: FormEvent) => {
    event?.preventDefault()
    if (!question.trim() || state.loading) return

    setState({ loading: true, status: '正在启动 Agent...' })

    try {
      await streamAnalysis(question, (patch) => {
        setState((current) => ({ ...current, ...patch }))
      })
    } catch (error) {
      setState({
        loading: false,
        status: '失败',
        error: error instanceof Error ? error.message : '未知错误'
      })
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <div className="brand">DATA AGENT</div>
          <h1>企业智能数据分析 Agent</h1>
        </div>
        <div className="status-pill">
          <span className={state.loading ? 'dot loading' : 'dot'} />
          {state.status}
        </div>
      </header>

      <main className="workspace">
        <aside className="chat-panel">
          <section className="intro-card">
            <p className="eyebrow">BI Copilot / Data Agent</p>
            <h2>用自然语言完成企业数据分析</h2>
            <p>
              Agent 自动完成指标识别、权限过滤、查询计划、数据查询、
              Visualization DSL 生成和分析结论。
            </p>
          </section>

          <div className="examples">
            {examples.map((item) => (
              <button key={item} onClick={() => setQuestion(item)} className="example-btn">
                {item}
              </button>
            ))}
          </div>

          <form onSubmit={submit} className="query-form">
            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="例如：最近6个月华东销售额趋势怎么样？"
            />
            <button disabled={state.loading} type="submit">
              {state.loading ? '分析中...' : '开始分析'}
            </button>
          </form>

          {state.insight && (
            <section className="insight-card">
              <div className="card-label">Agent 结论</div>
              <p>{state.insight}</p>
            </section>
          )}

          {state.plan && (
            <details className="debug-card">
              <summary>查看执行计划</summary>
              <pre>{JSON.stringify(state.plan, null, 2)}</pre>
            </details>
          )}

          {state.sql && (
            <details className="debug-card">
              <summary>查看受控 SQL</summary>
              <pre>{state.sql}</pre>
            </details>
          )}

          {state.traceId && <div className="trace-id">Trace: {state.traceId}</div>}
          {state.error && <div className="error-box">{state.error}</div>}
        </aside>

        <section className="result-panel">
          <VisualizationPanel spec={state.visualization} />
        </section>
      </main>
    </div>
  )
}

export default App
