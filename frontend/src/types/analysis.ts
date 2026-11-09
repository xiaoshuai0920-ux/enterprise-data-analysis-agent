export type ChartType = 'bar' | 'line' | 'pie' | 'table' | 'metric'

export interface SeriesSpec {
  name: string
  field: string
  type?: 'bar' | 'line'
}

export interface ColumnSpec {
  title: string
  field: string
  data_type: 'string' | 'number' | 'percent' | 'currency'
}

export interface MetricCard {
  label: string
  value: number | string
  unit?: string
  change?: number
}

export interface VisualizationSpec {
  type: ChartType
  title: string
  subtitle?: string
  x_field?: string
  x_label?: string
  series: SeriesSpec[]
  columns: ColumnSpec[]
  data: Record<string, unknown>[]
  metrics: MetricCard[]
}

export interface QueryPlan {
  metric: string
  dimensions: string[]
  filters: Record<string, unknown>
  time_range: string
  comparison?: string
  visualization: ChartType
  limit: number
}

export interface AnalysisState {
  loading: boolean
  status: string
  plan?: QueryPlan
  visualization?: VisualizationSpec
  insight?: string
  sql?: string
  traceId?: string
  error?: string
}
