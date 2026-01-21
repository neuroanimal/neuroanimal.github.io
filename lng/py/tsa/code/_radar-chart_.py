import plotly.graph_objects as go
import pandas as pd
# Generate sample data
categories = ['Speed', 'Reliability', 'Comfort', 'Safety', 'Efficiency']
values = [90, 60, 85, 70, 80]
# Create a radar chart
fig = go.Figure()
fig.add_trace(go.Scatterpolar(
    r=values,
    theta=categories,
    fill='toself',
    name='Product A'
))
# Add title
fig.update_layout(title='Radar Chart')
# Show the plot
fig.show()

