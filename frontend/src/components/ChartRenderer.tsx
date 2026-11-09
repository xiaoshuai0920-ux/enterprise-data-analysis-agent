import ReactECharts from 'echarts-for-react'
import type { VisualizationSpec } from '../types/analysis'

interface Props {
  spec: VisualizationSpec
}

function numberFormatter(value: unknown) {
  if (typeof value !== 'number') return value
  if (Math.abs(value) >= 100000000) return `${(value / 100000000).toFixed(2)}亿`
  if (Math.abs(value) >= 10000) return `${(value / 10000).toFixed(1)}万`
  return value.toLocaleString()
}

export function ChartRenderer({ spec }: Props) {
  if (!spec.x_field || !spec.series?.length) return null

  const xField = spec.x_field
  const series = spec.series[0]
  const source = spec.data.map((item) => ({
    category: item[xField],
    value: item[series.field]
  }))

  if (spec.type === 'pie') {
    return (
      <ReactECharts
        style={{ height: 400 }}
        option={{
          tooltip: { trigger: 'item' },
          legend: { bottom: 0 },
          series: [
            {
              name: series.name,
              type: 'pie',
              radius: ['38%', '68%'],
              data: source.map((item) => ({
                name: item.category,
                value: item.value
              }))
            }
          ]
        }}
      />
    )
  }

  const type = spec.type === 'line' ? 'line' : 'bar'

  return (
    <ReactECharts
      style={{ height: 400 }}
      option={{
        tooltip: {
          trigger: 'axis',
          valueFormatter: numberFormatter
        },
        grid: { left: 72, right: 24, top: 36, bottom: 56 },
        xAxis: {
          type: 'category',
          data: source.map((item) => item.category),
          axisLabel: { interval: 0 }
        },
        yAxis: {
          type: 'value',
          axisLabel: { formatter: numberFormatter }
        },
        series: [
          {
            name: series.name,
            type,
            smooth: type === 'line',
            data: source.map((item) => item.value),
            label: {
              show: source.length <= 8,
              position: 'top',
              formatter: ({ value }: { value: unknown }) => numberFormatter(value)
            }
          }
        ]
      }}
    />
  )
}
