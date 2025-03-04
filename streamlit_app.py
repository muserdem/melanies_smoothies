import streamlit as st
import requests
from snowflake.snowpark.functions import col

st.title("Customize Your Smoothie :cup_with_straw:")
st.write("Choose up to 5 ingredients!")

# Name input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie is:", name_on_order)

# Fetch fruit list from Snowflake
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUITNAME')).collect()
fruit_list = [row["FRUITNAME"] for row in my_dataframe]

# Multiselect for fruit choices
ingredients_list = st.multiselect("Choose your ingredients:", fruit_list)

# Validation: Ensure max 5 ingredients
if len(ingredients_list) > 5:
    st.error("You can only select up to 5 ingredients! Please remove one or more.")

# Show nutrition info for selected fruits
if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)

    for fruit_chosen in ingredients_list:
        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Fetch nutrition data
        response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}")

        if response.status_code == 200:
            sf_df = response.json()
            st.dataframe(data=sf_df, use_container_width=True)
        else:
            st.write(f"Sorry, {fruit_chosen} is not in the Fruitvice database.")

# Submit button to store order in Snowflake
if ingredients_list and len(ingredients_list) <= 5:
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}! ✅")
