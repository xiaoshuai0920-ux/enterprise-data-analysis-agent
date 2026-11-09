import type { VisualizationSpec } from '../types/analysis'
import { ChartRenderer } from './ChartRenderer'
import { TableRenderer } from './TableRenderer'

export function VisualizationPanel({ spec }: { spec?: VisualizationSpec }) {
  if (!spec) {
    return (
      <div className="empty-state">
        <div className="empty-icon">◫</div>
        <h3>等待数据分析</h3>
        <p>试试：“帮我看一下今年各区域销售额，用柱状图展示”</p>
      </div>
    )
  }

  return (
    <section className="visual-card">
      <div className="visual-header">
        <div>
          <h2>{spec.title}</h2>
          {spec.subtitle && <p>{spec.subtitle}</p>}
        </div>
        <span className="chart-tag">{spec.type.toUpperCase()}</span>
      </div>

      {spec.type === 'table' ? (
        <TableRenderer spec={spec} />
      ) : spec.type === 'metric' ? (
        <div className="metric-grid">
          {spec.metrics.map((metric) => (
            <div className="metric-card" key={metric.label}>
              <span>{metric.label}</span>
              <strong>{metric.value}{metric.unit || ''}</strong>
            </div>
          ))}
        </div>
      ) : (
        <ChartRenderer spec={spec} />
      )}
    </section>
  )
}
