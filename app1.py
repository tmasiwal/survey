import streamlit as st
import certifi
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import pandas as pd
import plotly.express as px



# Load environment variables
load_dotenv()

# MongoDB connection
mongodb_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongodb_uri, tlsCAFile=certifi.where())
db = client["survay"]

collection = db["users"]

# Streamlit app
st.set_page_config(layout="wide",page_title="Survey",page_icon=":bar_chart:")

st.title(":bar_chart: Political Survey in Jharkhand 2024")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

# Fetch data from MongoDB collection
documents = list(collection.find({}))

# Convert ObjectId values to strings in the _id field
for doc in documents:
    doc['_id'] = str(doc['_id'])

# Create DataFrame from modified documents
df = pd.DataFrame(documents,columns=["Name","Number","Age Group","Gender","Occupation","Constituency","Interested","Additional Comments"])


st.write(df)

col1, col2 = st.columns((2))


st.sidebar.header("Choose your filter: ")
# Create for Constituency
Constituency = st.sidebar.multiselect("Pick your Constituency", df["Constituency"].unique())
if not Constituency:
    df2 = df.copy()
else:
    df2 = df[df["Constituency"].isin(Constituency)]

# Create for Occupation
Occupation = st.sidebar.multiselect("Pick the Occupation", df2["Occupation"].unique())
if not Occupation:
    df3 = df2.copy()
else:
    df3 = df2[df2["Occupation"].isin(Occupation)]

# Create for Age Group"
Age= st.sidebar.multiselect("Pick the Age Group",df3["Age Group"].unique())
if not Age:
    df4=df3.copy()
else:
    df4 = df3[df3["Age Group"].isin(Age)]
# Create for Gender
Gender= st.sidebar.multiselect("Pick the Gender", df4["Gender"].unique())
if not Gender:
    df5=df4.copy()
else:
    df5 = df4[df4["Gender"].isin(Gender)]
# Filter the data based on Constituency, Occupation and Age

if not Constituency and not Occupation and not Age and not Gender:
    filtered_df = df
elif not Occupation and not Age:
    filtered_df = df[df["Constituency"].isin(Constituency)]
elif not Constituency and not Age:
    filtered_df = df[df["Occupation"].isin(Occupation)]
elif Occupation and Age:
    filtered_df = df3[df["Occupation"].isin(Occupation) & df3["Age"].isin(Age)]
elif Constituency and Age:
    filtered_df = df3[df["Constituency"].isin(Constituency) & df3["Age Group"].isin(Age)]
elif Constituency and Occupation:
    filtered_df = df3[df["Constituency"].isin(Constituency) & df3["Occupation"].isin(Occupation)]
elif Age:
    filtered_df = df3[df3["Age Group"].isin(Age)]

else:
    filtered_df = df3[df3["Constituency"].isin(Constituency) & df3["Occupation"].isin(Occupation) & df3["Age Group"].isin(Age)]

if Gender:
    filtered_df = df5


with col1:
    # Group by Constituency and count the number of people in each Constituency
    constituency_counts = filtered_df['Constituency'].value_counts().reset_index()
    constituency_counts.columns = ['Constituency', 'Number of People']

   # Plot the bar chart
    st.subheader("Constituency wise People")
    fig = px.bar(constituency_counts, x="Constituency", y="Number of People", text=constituency_counts['Number of People'],
             template="seaborn",color='Constituency')
    st.plotly_chart(fig, use_container_width=True, height=200)

with col2:
    gender_counts = filtered_df['Gender'].value_counts().reset_index()
    gender_counts.columns = ['Gender', 'Number of People']

    # Plot the pie chart
    st.subheader("Gender wise People")
    fig = px.pie(gender_counts, values="Number of People", names="Gender", hole=0.5)
    fig.update_traces(textinfo='percent+label', textposition='inside', showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Constituency Data"):
        st.write(filtered_df.style.background_gradient(cmap="Blues"))
        csv = filtered_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Constituency_Data.csv", mime = "text/csv",
                            help = 'Click here to download the data as a CSV file')

        

chart1, chart2 = st.columns((2))
with chart1:
    st.subheader('Occupation wise People')
    occupation_counts = filtered_df.groupby('Occupation').size().reset_index(name='Count')

    fig = px.pie(occupation_counts, values='Count', names='Occupation', template='plotly_dark')

    # Update the chart layout
    fig.update_traces(textinfo='percent+label', textposition='inside')

    # Display the chart using Streamlit
    st.plotly_chart(fig, use_container_width=True)

with chart2:
    st.subheader('Interested People in Constituency')
    interested_df = filtered_df[filtered_df['Interested'] == 'Yes']
    constituency_counts = interested_df.groupby('Constituency').size().reset_index(name='Number of People')
    fig = px.bar(constituency_counts, y='Number of People', x='Constituency', text='Number of People',
             template='seaborn',color='Constituency')
    fig.update_traces( textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)


with chart2:
    with st.expander("Constituency Interested Data"):
        st.write(interested_df.style.background_gradient(cmap="Blues"))
        csv = interested_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Interested_Constituency_Data.csv", mime = "text/csv",
                            help = 'Click here to download the data as a CSV file')


with st.expander("View Survey Data"):
    st.write(df.style.background_gradient(cmap="Oranges"))

    # Download orginal DataSet
    csv = df.to_csv(index = False).encode('utf-8')
    st.download_button('Download Data', data = csv, file_name = "Data.csv",mime = "text/csv")