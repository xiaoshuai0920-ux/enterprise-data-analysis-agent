from app.services.planner import build_plan

def test_bar_plan():
    plan = build_plan("帮我看一下今年各区域销售额，用柱状图展示")
    assert plan.metric == "sales_amount"
    assert plan.dimensions == ["region"]
    assert plan.visualization == "bar"
    assert plan.time_range == "2026"

def test_table_plan():
    plan = build_plan("把本月各产品毛利率做成表格")
    assert plan.metric == "gross_margin"
    assert plan.dimensions == ["product"]
    assert plan.visualization == "table"
