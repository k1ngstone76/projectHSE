
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
st.title("Road Accident Data Analysis")




accidents = pd.read_csv("Road Accident Data.csv")

#Replace 'Fetal' with 'Fatal' in the Accident_Severity column
accidents['Accident_Severity'] = accidents['Accident_Severity'].replace('Fetal', 'Fatal')


severity_mapping = {'Slight': 1, 'Serious': 2, 'Fatal': 3}
accidents['Severity_Numeric'] = accidents['Accident_Severity'].map(severity_mapping)

daylight_conditions = ['Daylight', 'Daylight: street light present']
accidents['Day_or_Night'] = accidents['Light_Conditions'].apply(
    lambda x: 'Day' if x in daylight_conditions else 'Night'
)



#We calculate the number of accidents of each severity level
severity_counts = accidents['Accident_Severity'].value_counts()

#create a pie chart
st.write("**let's draw some simple graphs to find some kind of relationship** ")
fig = go.Figure(data=[
    go.Pie(
        labels=severity_counts.index,   # Severity categories (Slight, Serious, Fatal)
        values=severity_counts.values, # Number of accidents for each category
        hole=0.0,                      
        textinfo='label+percent',      
        marker=dict(colors=['rgb(135, 206, 250)', 'rgb(255, 165, 0)', 'rgb(255, 69, 0)']) 
    )
])


fig.update_layout(
    title='Emergency severity distribution',
    template='plotly_white'
)


st.plotly_chart(fig, use_container_width=True)


time_of_day_counts = accidents['Day_or_Night'].value_counts()


fig = go.Figure(data=[
    go.Bar(
        x=time_of_day_counts.index,  # Times of Day (Day, Night)
        y=time_of_day_counts.values, # Number of accidents for each time of day
        marker=dict(color=['skyblue', 'orange'])
    )
])


fig.update_layout(
    title='Number of accidents at different times of the day',
    xaxis_title='Times of Day',
    yaxis_title='Number of accidents',
    template='plotly_white'
)


st.plotly_chart(fig, use_container_width=True)

st.write("We count the number of accidents for each type of vehicle")
vehicle_type_counts = accidents['Vehicle_Type'].value_counts()

fig = go.Figure(data=[
    go.Bar(
        x=vehicle_type_counts.index,  # Types of vehicles
        y=vehicle_type_counts.values, # Number of accidents for each type
        marker=dict(color='lightblue')
    )
])

fig.update_layout(
    title='Number of accidents by vehicle type',
    xaxis_title='Vehicle type',
    yaxis_title='Number of Accident',
    template='plotly_white',
    xaxis_tickangle=-45  
)

st.plotly_chart(fig, use_container_width=True)
st.write("**My hypothesis is that - The number of serious accidents is higher in bad weather condition**")


st.write("Let's check the average number of people who tried in different weather")

casualties_weather = accidents.groupby('Weather_Conditions')['Number_of_Casualties'].mean().sort_values()
# Average number of casualties by weather conditions
fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=casualties_weather.index,
    y=casualties_weather,
    mode='lines+markers',
    line=dict(color='blue', width=2),
    marker=dict(size=8)
))

fig1.update_layout(
    title="Average number of casualties by weather conditions",
    xaxis_title="Weather conditions",
    yaxis_title="Average number of victims",
    xaxis=dict(tickangle=45),
    template='plotly'
)
st.plotly_chart(fig1, use_container_width=True)



#Classification of weather conditions into “good” and “bad” 
good_weather = ["Fine no high winds", "Fine with high winds"]
bad_weather = ["Rain", "Snow", "Fog or mist", "Other", "Strong winds"]

# Adding the category "Weather_Type"
accidents['Weather_Type'] = accidents['Weather_Conditions'].apply(
    lambda x: 'Good' if x in good_weather else 'Bad' if x in bad_weather else 'Unknown'
)

# Filter data for known weather conditions
filtered_data = accidents[accidents['Weather_Type'] != 'Unknown']

# Grouping to analyze the proportion of serious accidents
severity_counts = filtered_data.groupby(['Weather_Type', 'Accident_Severity']).size().unstack(fill_value=0)
severity_proportions = severity_counts.div(severity_counts.sum(axis=1), axis=0)

st.write("**Now let’s check the number of accidents in bad and good weather**")
# Accident severity distribution
fig2 = go.Figure()
for severity in severity_proportions.columns:
    fig2.add_trace(go.Bar(
        x=severity_proportions.index,
        y=severity_proportions[severity],
        name=severity
    ))

fig2.update_layout(
    title="Distribution of accident severity by weather conditions",
    xaxis_title="Type of weather conditions",
    yaxis_title="Percentage of total accidents",
    barmode='stack',
    legend_title="Severity of the accident",
    template='plotly'
)



API_URL = "http://127.0.0.1:8000"  

st.title("Road Accident Management")

# Секция для фильтрации и отображения данных
st.header("Fetch Road Accidents Data")
severity = st.selectbox("Select Severity", ["", "Fatal", "Serious", "Slight"])
day_of_week = st.selectbox("Select Day of the Week", ["", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
limit = st.slider("Number of records to display", min_value=1, max_value=100, value=10)

if st.button("Fetch Data"):
    params = {"limit": limit}
    if severity:
        params["severity"] = severity
    if day_of_week:
        params["day_of_week"] = day_of_week

    response = requests.get(f"{API_URL}/accidents", params=params)
    if response.status_code == 200:
        data = response.json()
        st.write(data)
    else:
        st.error(f"Failed to fetch data: {response.status_code}")

# Секция для добавления новых данных
st.header("Add a New Road Accident Record")

# Форма для добавления новой записи
with st.form("add_accident_form"):
    accident_index = st.text_input("Accident Index (Optional)")
    accident_date = st.date_input("Accident Date")
    location = st.text_input("Local Authority (District)")
    accident_severity = st.selectbox("Accident Severity", ["Fatal", "Serious", "Slight"])
    submit_button = st.form_submit_button("Submit New Record")

    if submit_button:
        new_record = {
            "Accident_Index": accident_index if accident_index else None,
            "date": str(accident_date),
            "location": location,
            "severity": accident_severity
        }

        response = requests.post(f"{API_URL}/accidents", json=new_record)
        if response.status_code == 200:
            st.success("New record added successfully!")
        else:
            st.error(f"Failed to add new record: {response.status_code}")



st.plotly_chart(fig2, use_container_width=True)


st.write("Accident severity distribution:")
st.write(severity_counts)
st.write("\nPercentage distribution of accident severity:")
st.write(severity_proportions)



st.write("### Обработанные данные")
st.write(accidents.head())

