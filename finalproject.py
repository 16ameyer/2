'''
Name: Audrey Meyer
CS230: Section 2
Data: Volcano Data from Smithsonian
URL: https://6susdvchyy6qyyueyyrhts.streamlit.app/

Description:
This program aims to educate individuals on information relating to volcanoes.
Users can choose to look at historical data of volcanic eruptions, or they can choose to analyze the difference in mean elevations for different volcanic regions.
The most interesting feature of Volcano 101 is the customized map that will focus on the specific volcanoes in a chosen country.
'''
import streamlit as st
import matplotlib.pyplot as plt
import pydeck as pdk
import pandas as pd
from PIL import Image

df_volcano = pd.read_csv("volcanoes.csv",skiprows=1,encoding="ISO-8859-1") #Saved in this encoding because my csv contains special characters, so this allows Pandas to load it without crashing
df_volcano.columns = [col.strip() for col in df_volcano.columns] #Getting rid of spaces
df_volcano.set_index("Volcano Number",inplace=True) #Index set to Volcano Number, which seems practical
st.header("Volcano 101") #A nice header to have the whole time the program is running

def show_main_menu(): #This will be the main menu that user sees when opening the program
    main_header = '<p style="font-family:monospace; color:orange; font-size: 28px;">Welcome to Volcano Information!' #Fun header
    st.markdown(main_header, unsafe_allow_html=True)
    st.success("The purpose of this program is to help you learn more about volcanoes.")
    st.write("Here is a preview of the data looks like. Obviously a very large dataset that was provided by Smithsonian, but it is provided below so that you can get a feel for the types of information available here. There are awesome options on the sidebar to your left :)") #Being friendly and encouraging learning
    st.dataframe(df_volcano) # [VIZ1] A table with a title, colors, and labels
    image_path = "volcano.jpg" #Cool picture so people can recall what a volcano can look like
    img = Image.open(image_path) # [ST4] Customized page design feature (image)
    st.image(img, width=700)

def eruption_date(): #A function that will produce graphs showing the volcanic eruptions in time, split into BCE and CE because large dataset
    st.subheader("Volcanic Eruption Dates")
    date_range = st.radio("What area of time would you like to view:", ["BCE", "CE"]) # [ST1] A multi-select Streamlit widget
    df_eruption = df_volcano[df_volcano["Last Known Eruption"].str.lower() != "unknown"].copy()  #If last known eruption is not known, then it does not need to be included in this new dataframe
    df_eruption["Last Known Eruption"] = df_eruption["Last Known Eruption"].str.strip() # [DA1] Clean the data
    eruption_years = []
    for val in df_eruption["Last Known Eruption"]:
        try: # [PY3] Error checking with try/except
            if date_range == "BCE" and "BCE" in val: #Splitting the data into two chunks, BCE and CE
                val = val.replace("BCE", "").strip() #Then removing the labels, as they are not needed
                eruption_years.append(-int(val))
            elif date_range == "CE":
                val = val.replace("CE", "").strip()
                if val.isdigit():
                    eruption_years.append(int(val))
                else:
                    eruption_years.append(None)
            else:
                eruption_years.append(None)
        except:
            eruption_years.append(None)
    df_eruption["Eruption Year"] = eruption_years # [DA9] Adding a new column in the copy dataframe of df volcanoes
    df_eruption = df_eruption.dropna(subset=["Eruption Year"])
    if df_eruption.empty: #Giving an option in case data is not found, which would indicate a problem with the program, so then it could be fixed
        st.warning(f"No valid eruption data found for {date_range}.")
        return
    df_eruption["Century"] = (df_eruption["Eruption Year"] // 100) * 100 #Adding another new column that
    eruption_counts = df_eruption["Century"].value_counts().sort_index() # [DA2] Sort data
    chart_type = st.radio("Select chart type:", ["Bar Chart", "Line Chart"]) #Asking the user what type of chart they want to view
    fig, ax = plt.subplots(figsize=(16, 8)) #Creating chart variables
    if chart_type == "Bar Chart": # [VIZ2] A bar chart with a title, colors, and labels
        ax.bar(eruption_counts.index.astype(int), eruption_counts.values, color="orange",width=80) #Bar chart with orange bars (orange for lava)
    else:
        ax.plot(eruption_counts.index.astype(int), eruption_counts.values, marker="o") # [VIZ3] A line chart with a title, colors, and labels
    ax.set_xlabel("Century") #X-axis label
    ticks = eruption_counts.index[::5] #Skipping by 5s because there are a lot of labels and they overlapped
    labels = [f'{abs(c):.0f} BCE' if c < 0 else f'{c:.0f} CE' for c in ticks] # [PY4] A list comprehension
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels, rotation=60, ha='right', fontsize=8) #Making the x-axis labels look nice
    ax.set_ylabel("Number of Volcanoes") #Y-axis label
    ax.set_title(f"Volcanoes by Century of Last Known Eruption ({date_range})")
    st.pyplot(fig)

def activity_info(): #Filtering volcanoes by activity classification, just to see which volcano classification occurs the most, vice versa
    activity_type = st.selectbox("Select activity evidence:", df_volcano["Activity Evidence"].unique()) # [ST2] A drop down Streamlit widget
    filtered = df_volcano[df_volcano["Activity Evidence"]==activity_type] # [DA4] Filtering data by one condition
    n = len(filtered)
    st.write(f'There are {n} volcanoes with that classification.') #Giving them a nice overview of results
    st.write(filtered)

def map_creation(): #Displaying a map based on the volcanoes in the country that the user types in
    st.subheader("Map of Volcanoes for a Specific Country")
    country = st.text_input("Please enter the country you want to focus on") # [ST3] A textbox input Streamlit widget
    valid_countries = df_volcano["Country"].dropna().unique() #Establishing what countries the user is allowed to type in
    normalized_countries = [c.lower().strip() for c in valid_countries] #Making everything run smoothly because everything will be lowercase and stripped
    if country.lower().strip() not in normalized_countries:
        st.warning("Please enter a valid country.") #Making the user enter a valid country
        return
    df_volcano3 = df_volcano[df_volcano["Country"].str.lower().str.strip() == country.lower().strip()]
    num = len(df_volcano3) #Counting how many volcanoes in the country that the user typed in
    st.write(f'In {country}, there are {num} volcanoes')
    ICON_URL = "https://upload.wikimedia.org/wikipedia/commons/9/96/Map_marker_icon_%E2%80%93_Nicolas_Mollet_%E2%80%93_Volcano_%E2%80%93_Nature_%E2%80%93_default.png" #The icon for the volcanoes on the map!!!
    icon_data = {
        "url": ICON_URL,
        "width": 100,
        "height": 100,
        "anchorY": 1  # where you want the icon to be relative to location
    }
    df_volcano3["icon_data"] = [icon_data] * len(df_volcano3) #We need an icon for each volcano
    icon_layer = pdk.Layer(type="IconLayer",
                           data=df_volcano3,
                           get_icon="icon_data",
                           get_position='[Longitude,Latitude]',
                           get_size=4,
                           size_scale=10,
                           pickable=True)
    view_state = pdk.ViewState(latitude=df_volcano3["Latitude"].mean(), longitude=df_volcano3["Longitude"].mean(), zoom=4,pitch=0) #How the map will appear on the screen. I found that zoom=4 works the best for small and large countries, like a perfect medium
    tool_tip = {"html": "<b>Volcano:</b> {Volcano Name}",
                "style": {"backgroundColor": "orange",
                          "color": "white"}
                }
    icon_map = pdk.Deck(map_style='mapbox://styles/mapbox/navigation-day-v1',layers=[icon_layer],initial_view_state=view_state,tooltip=tool_tip)
    st.pydeck_chart(icon_map) # [MAP] A detailed map, I would argue that this is the coolest feature of this project (I am pretty proud)

def volcano_elevation(): #Creating a pivot table to display data that is color coded, so easy for users to analyze data
    st.subheader("Average Elevation of Various Volcanic Landforms in Volcanic Regions")
    df_volcano2 = pd.pivot_table(data=df_volcano, index=["Volcanic Region"], columns=["Volcano Landform"], values=["Elevation (m)"],aggfunc="mean") #Creating the basis of the pivot table, fancy style things are in next line
    st.dataframe(df_volcano2.style.background_gradient(cmap="YlOrRd").format("{:.1f}")) # [DA6] Analyze data with a pivot table (Figuring out the gradient option was from streamlit help)

def region_elevation_filter(region,min_height=1000): # [PY1] A function with two parameters, one of which has a default (This function is the beginning for the final option on the menu)
    st.subheader(f'Volcanoes in {region} with Elevation ≥ {min_height} meters') #Personalized subheader
    filtered = df_volcano[(df_volcano["Volcanic Region"] == region) & (df_volcano["Elevation (m)"] >= min_height)] # [DA5] Filtering data by two or more conditions using &
    grouped = filtered.groupby("Primary Volcano Type").size().sort_values(ascending=False) # [DA7] Grouping data by primary volcano type
    st.write(f"Total volcanoes found: {len(filtered)}") #Summarizing data
    st.bar_chart(grouped) #Presenting the user with a bar chart and the filtered dataframe, so hopefully they will be able to learn more about volcanoes
    st.dataframe(filtered)

def region_elevation_filter_menu(): #Creating the menu option for the user to select
    region = st.selectbox("Select a Volcanic Region:", df_volcano["Volcanic Region"].dropna().unique())
    min_height = st.slider("Minimum Elevation (m):", 0, 8000, 1000)  # default is 1000
    region_elevation_filter(region, min_height) #Calling the function (yay!)

#Creating the sidebar menu that allows users to navigate website
st.sidebar.title("What would you like to learn today?")
options = {"Main Menu":show_main_menu,
           "Volcanic Eruption Dates":eruption_date,
           "Volcanic Activity": activity_info,
           "Map of Volcanoes in a Country": map_creation,
           "Elevations of Volcanic Regions": volcano_elevation,
           "Region and Elevation Filter": region_elevation_filter_menu
           } # [PY5] A dictionary where you write code to access its keys, values, or items
selected_option = st.sidebar.radio("Please select an option",options.keys())
options[selected_option]() #Run the program

#Thank you for reviewing my final project, have a great summer!
