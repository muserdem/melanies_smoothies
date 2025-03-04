import streamlit as st
import requests
import pandas as pd  
from snowflake.snowpark.functions import col

st.title("🥤 Customize Your Smoothie")
st.write("Choose up to 5 ingredients!")

# Name input
name_on_order = st.text_input("Name on Smoothie:")

# Fetch fruit list from Snowflake
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUITNAME'), col('SEARCH_ON')).to_pandas()

# Replace None or NaN values in SEARCH_ON with FRUITNAME
my_dataframe["SEARCH_ON"].fillna(my_dataframe["FRUITNAME"], inplace=True)

# Debugging step: Show the fetched data
st.dataframe(my_dataframe, use_container_width=True)

# Ingredient selection box (MAKE SURE IT'S VISIBLE)
ingredients_list = st.multiselect("Choose your ingredients:", my_dataframe["FRUITNAME"].tolist())

# Validation: Max 5 ingredients
if len(ingredients_list) > 5:
    st.error("You can only select up to 5 ingredients! Please remove one or more.")

# Fetch nutrition info using SEARCH_ON values
if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # Safely retrieve the SEARCH_ON value
        search_on_value = my_dataframe.loc[my_dataframe['FRUITNAME'] == fruit_chosen, 'SEARCH_ON'].values[0]

        # Debugging Output
        st.write(f"🔍 The search value for **{fruit_chosen}** is **{search_on_value}**.")

        # Display Nutrition Information
        st.subheader(f"🍎 {fruit_chosen} Nutrition Information")
        
        fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_on_value}")
        
        if fruityvice_response.status_code == 200:
            fv_df = fruityvice_response.json()
            st.dataframe(data=fv_df, use_container_width=True)
        else:
            st.warning(f"⚠️ Sorry, {fruit_chosen} ({search_on_value}) is not available in the API.")

# Submit button for database insertion
if ingredients_list and len(ingredients_list) <= 5:
    ingredients_string = ', '.join(ingredients_list)
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """
    if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")

