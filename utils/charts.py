import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def auto_chart(columns: list, rows: list):
    if not rows or len(columns) < 2:
        return None
    
    df = pd.DataFrame(rows, columns=columns)
    
    # Find numeric and text columns
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    text_cols = df.select_dtypes(exclude=['number']).columns.tolist()
    
    if not numeric_cols:
        return None
    
    x_col = text_cols[0] if text_cols else columns[0]
    y_col = numeric_cols[0]
    
    # Limit to 20 rows for chart clarity
    df = df.head(20)
    
    # Choose chart type based on data
    if len(df) <= 8:
        fig = px.bar(
            df, x=x_col, y=y_col,
            title=f"{y_col} by {x_col}",
            color=y_col,
            color_continuous_scale="Blues",
            template="plotly_white"
        )
    else:
        fig = px.line(
            df, x=x_col, y=y_col,
            title=f"{y_col} by {x_col}",
            markers=True,
            template="plotly_white"
        )
    
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(size=12),
    )
    return fig