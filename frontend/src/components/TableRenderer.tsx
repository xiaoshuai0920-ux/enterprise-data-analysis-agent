import type { VisualizationSpec } from '../types/analysis'

function formatValue(value: unknown, type: string) {
  if (value === null || value === undefined) return '-'
  if (typeof value !== 'number') return String(value)

  if (type === 'currency') {
    return `¥${value.toLocaleString('zh-CN', { maximumFractionDigits: 2 })}`
  }
  if (type === 'percent') {
    return `${value.toFixed(2)}%`
  }
  return value.toLocaleString('zh-CN')
}

export function TableRenderer({ spec }: { spec: VisualizationSpec }) {
  return (
    <div className="table-wrap">
      <table className="data-table">
        <thead>
          <tr>
            {spec.columns.map((column) => (
              <th key={column.field}>{column.title}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {spec.data.map((row, index) => (
            <tr key={index}>
              {spec.columns.map((column) => (
                <td key={column.field}>
                  {formatValue(row[column.field], column.data_type)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
