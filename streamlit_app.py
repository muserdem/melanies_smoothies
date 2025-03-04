import streamlit as st
#from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

st.title("Customize Your Smoothie :cup_with_straw:")
st.write("Choose up to 5 ingredients!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie is", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session() #get_active_session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUITNAME')).collect()
fruit_list = [row["FRUITNAME"] for row in my_dataframe]  # Extracting fruit names from Snowflake result

# Let users select without a strict limit, but handle validation separately
ingredients_list = st.multiselect("Choose your ingredients:", fruit_list)

if len(ingredients_list) > 5:
    st.error("You can only select up to 5 ingredients! Please remove one or more.")

if ingredients_list and len(ingredients_list) <= 5:
    ingredients_string = ', '.join(ingredients_list)

    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}! ✅")

import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.text(smoothiefroot_response.json())
