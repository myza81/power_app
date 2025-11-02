import pandas as pd
import plotly.graph_objects as go

# Read CSVs
file_path = '/Users/myijat/Desktop/C37118-241-500JMJG-U5-20251015161200-20251015162959.csv'
df = pd.read_csv(file_path, skiprows=[0], header=0)
timestamp = df['Date']+' '+df['Time (Asia/Singapore)']
df['timestamp'] = pd.to_datetime(timestamp, format="%m/%d/%y %H:%M:%S.%f")



print(df)





# # Create plot
# fig = go.Figure()

# fig.add_trace(go.Scatter(x=df['Time'], y=df['Frequency'], 
#                          name='Sum of Frequency', 
#                          mode='lines+markers', 
#                          line=dict(color='blue')))

# fig.add_trace(go.Scatter(x=df['Time'], y=df['JMAH_U1'], 
#                          name='Sum of JMAH U1', 
#                          mode='lines+markers', 
#                          line=dict(color='red'),
#                          yaxis='y2'))

# fig.add_trace(go.Scatter(x=df['Time'], y=df['JMAH_U2'], 
#                          name='Sum of JMAH U2', 
#                          mode='lines+markers',
#                          line=dict(color='darkblue'),
#                          yaxis='y2'))

# # Add secondary y-axis
# fig.update_layout(
#     xaxis=dict(title='Time'),
#     yaxis=dict(title='Sum of Frequency'),
#     yaxis2=dict(title='Sum of JMAH U1 and U2', overlaying='y', side='right'),
#     template='plotly_white',
#     legend=dict(x=0.01, y=0.99)
# )

# fig.show()
