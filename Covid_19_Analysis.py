import pandas as pd 
import streamlit as st 
import pandas as pd 
import os
import plotly.figure_factory as ff
import warnings
import plotly.express as px
warnings.filterwarnings('ignore')
st.set_page_config(page_title='THECOVID!!!' , page_icon=":bar_chart:" , layout="wide")
st.title(":bar_chart: COVID-19 DashBoard")
st.markdown("<style>div.block-container{padding-top:2rem;}</style>" , unsafe_allow_html=True)
f1 = st.file_uploader(":file_folder: UPLOAD A FILE" , type=(["csv","xlsx"]))
if f1 is not None :
    filename = f1.name
    st.write(filename)
    df = pd.read_csv(filename)
else:
    df = pd.read_csv("covid_19_clean_complete.csv")
df['Date'] = pd.to_datetime(df['Date'])
col1 , col2 = st.columns((2))
startdate = pd.to_datetime(df['Date']).min()
enddate = pd.to_datetime(df['Date']).max()
with col1:
    date1 = pd.to_datetime(st.date_input("Start Date" , startdate))
with col2:
    date2 = pd.to_datetime(st.date_input("End date" , enddate))
df= df[(df["Date"]>= date1) & (df["Date"] <= date2)].copy()
st.sidebar.header("Choose your filter : ")
region = st.sidebar.multiselect("pick your region" , df["Country/Region"].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Country/Region"].isin(region)]
# Create for Province/State
state = st.sidebar.multiselect("Pick the state" , df2["Province/State"].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["Province/State"].isin(state)]
# Create for WHO region 
who = st.sidebar.multiselect("Choose a WHO Region" , df["WHO Region"].unique())
if not who:
    df4 = df3.copy()
else:
    df4 = df3[df3["WHO Region"].isin(who)]
# Filtering the data based on Region , State and City
if not region and not state and not who:
    filtered_df = df
elif not state and not who:
    filtered_df = df[df["Country/Region"].isin(region)]
elif not region and not who:
    filtered_df  = df[df["Province/State"].isin(state)]
elif state and who:
    filtered_df = df3[df["Province/State"].isin(state) & df["WHO Region"].isin(who)]
elif region and state:
    filtered_df = df3[df["Country/Region"].isin(region) & df["Province/State"].isin(state)]
elif region and who:
    filtered_df = df3[df["Country/Region"].isin(region) & df["WHO Region"].isin(state)]
elif who:
    filtered_df = df3[df3["WHO Region"].isin(who)]
else:
    filtered_df = df3[df3["Country/Region"].isin(region) & df3["Province/State"].isin(state) & df3["WHO Region"].isin(who)]
    
category_df = filtered_df.groupby(by = ['Country/Region'],as_index = False)["Confirmed"].sum()
with col1:
    st.subheader("Region wise Confirmed Patients")
    fig = px.histogram(category_df , x = "Country/Region",y="Confirmed", template="seaborn")
    st.plotly_chart(fig , use_container_width=True , height = 200)
with col2:
    st.subheader("Region wise Deaths")
    fig = px.pie(filtered_df , values = "Deaths" , names="Country/Region" , hole = 0.5)
    fig.update_traces(text = filtered_df["Country/Region"] ,textposition="outside")
    st.plotly_chart(fig , use_container_width=True)
cl1 , cl2 = st.columns(2)
with cl1:
    with st.expander("Region_ViewData"):
        st.write(category_df.style.background_gradient(cmap = "Blues"))
        csv = category_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download_Data" ,data=csv , file_name = "Category.csv" , mime="text/csv",
                           help="Click here to download the data as a CSV file")
with cl2:
    with st.expander("Death_ViewData"):
        region = filtered_df.groupby(by = "Country/Region" , as_index=False)["Deaths"].sum()
        st.write(category_df.style.background_gradient(cmap="Oranges"))
        csv = region.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data",data = csv , file_name="Deaths.csv",mime="text/csv",
                           help="Click here to download the data as a CSV file")
filtered_df["month_year"]= pd.to_datetime(filtered_df["Date"]).dt.to_period("M").sort_values(ascending=True)
st.subheader("Time series Analysis")
linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Active"].sum()).reset_index()
fig2 = px.line(linechart , x ="month_year" , y = "Active" , height=500 , width = 1000,template="gridon")
st.plotly_chart(fig2 , use_container_width=True)
with st.expander("View Data Series in TimeSeries:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data',data=csv,file_name="TimeSeries.csv",mime="text/csv")
# Create a Trees based on Region, Deaths , Active-Patients , Recovered etc.
st.subheader("Hierarchical view of Deaths using TreeMap")
fig3 = px.treemap(filtered_df , path=["Country/Region"],values="Deaths",hover_data=["Deaths"],color="Country/Region")
fig3.update_layout(width=800 , height=650)
st.plotly_chart(fig3 ,use_container_width=True)
chart1 , chart2 = st.columns((2))
with chart1:
    st.subheader("WHO Region wise Recovered")
    fig = px.pie(filtered_df, values="Recovered",names="WHO Region" , template="plotly_dark")
    fig.update_traces(text=filtered_df["WHO Region"],textposition="inside")
    st.plotly_chart(fig , use_container_width=True)
with chart2:
    st.subheader("Country wise Recovered")
    fig = px.pie(filtered_df, values="Recovered",names="Country/Region" , template="plotly_dark")
    fig.update_traces(text=filtered_df["Country/Region"],textposition="inside")
    st.plotly_chart(fig , use_container_width=True)
st.subheader(":point_right: Month wise Category Deaths Summary")
with st.expander("Summary_Table"):
    df_sample=df.sort_values(by="Recovered",ascending=True).head(10)
    fig = ff.create_table(df_sample,colorscale="Cividis")
    st.plotly_chart(fig ,use_container_width=True)
    st.markdown("Month wise Country Table(Deaths)")
    filtered_df["month"] = filtered_df["Date"].dt.month_name()
    sub_category_year = pd.pivot_table(data=filtered_df,values = "Deaths",index=["Country/Region"],columns="month")
    st.write(sub_category_year.style.background_gradient(cmap="Blues"))
# Create a scatter plot
data1 = px.scatter(filtered_df,x="Confirmed",y="Deaths",size="Deaths")
data1['layout'].update(title="Relationship between Confirmed Patients and Dead Patients using Scatter plot.",titlefont = dict(size=20),xaxis=dict(title="Confirmed",titlefont=dict(size=19)),yaxis = dict(title="Deaths",titlefont = dict(size=19)))
st.plotly_chart(data1,use_container_width=True)

with st.expander("View Data"):
    st.write(filtered_df.drop(["Lat","Long","month_year", "month"],axis = 1).iloc[:500].style.background_gradient(cmap="Oranges"))
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("Download Original Dataset",data=csv , file_name= "Covid_19.csv",mime="text/csv")