'''
Name: Audrey Meyer
CS230: Section 2
Data: Volcano Data from Smithsonian
URL:

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
#py -m streamlit run "C:\Users\audre\OneDrive - Bentley University\CS 230\Python\finalproject.py"

# [DA1] Clean the data
df_volcano = pd.read_csv("volcanoes.csv",skiprows=1,encoding="ISO-8859-1") #Saved in this encoding because my csv contains special characters, so this allows Pandas to load it without crashing
df_volcano.columns = [col.strip() for col in df_volcano.columns] #Cleaning up spaces
df_volcano.set_index("Volcano Number",inplace=True)
st.header("Volcano 101")

def show_main_menu():
    main_header = '<p style="font-family:monospace; color:orange; font-size: 28px;">Welcome to Volcano Information!'
    st.markdown(main_header, unsafe_allow_html=True)
    st.success("The purpose of this program is to help you learn more about volcanoes.")
    st.write("Here is a preview of the data. There are options on the sidebar.")
    st.write(df_volcano) # [VIZ1] A table with a title, colors, and labels
    image_path1 = "C:\\Users\\audre\\OneDrive - Bentley University\\CS 230\\Images\\volcano.jpg"
    img1 = Image.open(image_path1) # [ST4] Customized page design feature (image)
    st.image(img1, width=700)

def eruption_date():
    st.subheader("Volcanic Eruption Dates")
    date_range = st.radio("What area of time would you like to view:", ["BCE", "CE"]) # [ST1] A multi-select Streamlit widget
    cleaned = df_volcano[df_volcano["Last Known Eruption"].str.lower() != "unknown"].copy()
    cleaned["Last Known Eruption"] = cleaned["Last Known Eruption"].str.strip()
    eruption_years = []
    for val in cleaned["Last Known Eruption"]:
        try: # [PY3] Error checking with try/except
            if date_range == "BCE" and "BCE" in val:
                val = val.replace("BCE", "").strip()
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
    cleaned["Eruption Year"] = eruption_years
    cleaned = cleaned.dropna(subset=["Eruption Year"])
    if cleaned.empty:
        st.warning(f"No valid eruption data found for {date_range}.")
        return
    cleaned["Century"] = (cleaned["Eruption Year"] // 100) * 100
    eruption_counts = cleaned["Century"].value_counts().sort_index() # [DA2] Sort data
    chart_type = st.radio("Select chart type:", ["Bar Chart", "Line Chart"])
    fig, ax = plt.subplots(figsize=(16, 8))
    if chart_type == "Bar Chart": # [VIZ2] A bar chart with a title, colors, and labels
        ax.bar(eruption_counts.index.astype(int), eruption_counts.values, color="orange",width=80)
    else:
        ax.plot(eruption_counts.index.astype(int), eruption_counts.values, marker="o") # [VIZ3] A line chart with a title, colors, and labels
    xticks = eruption_counts.index.astype(int)
    if date_range == "BCE":
        xlabels = [f"{abs(x)} BCE" for x in xticks]
    else:
        xlabels = [f"{x} CE" for x in xticks]
    ax.set_xlabel("Century")
    ticks = eruption_counts.index[::5]
    labels = [f'{abs(c):.0f} BCE' if c < 0 else f'{c:.0f} CE' for c in ticks] # [PY4] A list comprehension
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
    ax.set_ylabel("Number of Volcanoes")
    ax.set_title(f"Volcanoes by Century of Last Known Eruption ({date_range})")
    st.pyplot(fig)

def activity_info():
    activity_type = st.selectbox("Select activity evidence:", df_volcano["Activity Evidence"].unique()) # [ST2] A drop down Streamlit widget
    filtered = df_volcano[df_volcano["Activity Evidence"]==activity_type] # [DA4] Filtering data by one condition
    n = len(filtered)
    st.write(f'There are {n} volcanoes with that classification.')
    st.write(filtered)

def map_creation():
    st.subheader("Map of Volcanoes for a Specific Country")
    country = st.text_input("Please enter the country you want to focus on") # [ST3] A textbox input Streamlit widget
    valid_countries = df_volcano["Country"].dropna().unique()
    normalized_countries = [c.lower().strip() for c in valid_countries]
    if country.lower().strip() not in normalized_countries:
        st.warning("Please enter a valid country.")
        return
    df_volcano3 = df_volcano[df_volcano["Country"].str.lower().str.strip() == country.lower().strip()]
    num = len(df_volcano3)
    st.write(f'In {country}, there are {num} volcanoes')
    ICON_URL = "https://upload.wikimedia.org/wikipedia/commons/9/96/Map_marker_icon_%E2%80%93_Nicolas_Mollet_%E2%80%93_Volcano_%E2%80%93_Nature_%E2%80%93_default.png"
    icon_data = {
        "url": ICON_URL,
        "width": 100,
        "height": 100,
        "anchorY": 1  # where you want the icon to be relative to location
    }
    df_volcano3["icon_data"] = [icon_data] * len(df_volcano3)
    icon_layer = pdk.Layer(type="IconLayer",
                           data=df_volcano3,
                           get_icon="icon_data",
                           get_position='[Longitude,Latitude]',
                           get_size=4,
                           size_scale=10,
                           pickable=True)

    view_state = pdk.ViewState(
        latitude=df_volcano3["Latitude"].mean(),
        longitude=df_volcano3["Longitude"].mean(),
        zoom=4,
        pitch=0
    )
    tool_tip = {"html": "<b>Volcano:</b> {Volcano Name}",
                "style": {"backgroundColor": "orange",
                          "color": "white"}
                }
    icon_map = pdk.Deck(
        map_style='mapbox://styles/mapbox/navigation-day-v1',
        layers=[icon_layer],
        initial_view_state=view_state,
        tooltip=tool_tip
    )
    st.pydeck_chart(icon_map) # [MAP] A detailed map

def volcano_elevation():
    st.subheader("Average Elevation of Various Volcanic Landforms in Volcanic Regions")
    df_volcano2 = pd.pivot_table(data=df_volcano, index=["Volcanic Region"], columns=["Volcano Landform"], values=["Elevation (m)"],aggfunc="mean")
    st.dataframe(df_volcano2.style.background_gradient(cmap="YlOrRd").format("{:.1f}")) # [DA6] Analyze data with a pivot table

def volcano_type_by_region(region=None, min_height=500):
    st.subheader("Volcano Type Distribution in a Region")
    # Let user pick region if not provided
    if region is None:
        region = st.selectbox("Select Region:", df_volcano["Region"].dropna().unique())
    # Let user pick min height
    min_height = st.number_input("Minimum Elevation (meters):", value=min_height)

    # Filter with multiple conditions
    filtered = df_volcano[
        (df_volcano["Region"] == region) &
        (df_volcano["Elevation (Meters)"] >= min_height)
    ]

    # Group by Volcano Type and count
    grouped = filtered.groupby("Primary Volcano Type").size().sort_values(ascending=False)

    st.write(f"Found {len(filtered)} volcanoes in {region} with elevation ≥ {min_height} m.")
    st.bar_chart(grouped)
    st.dataframe(filtered)


#Creating the sidebar
st.sidebar.title("What would you like to learn today?")
options = {"Main Menu":show_main_menu,
           "Volcanic Eruption Dates":eruption_date,
           "Volcanic Activity": activity_info,
           "Map of Volcanoes in a Country": map_creation,
           "Elevations of Volcanic Regions": volcano_elevation
           } # [PY5] A dictionary where you write code to access its keys, values, or items
selected_option = st.sidebar.radio("Please select an option",options.keys())
options[selected_option]()


