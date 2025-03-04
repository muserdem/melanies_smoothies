import streamlit as st
import requests
from snowflake.snowpark.functions import col

st.title("Customize Your Smoothie :cup_with_straw:")
st.write("Choose up to 5 ingredients!")

# Name input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie is:", name_on_order)

# Fetch fruit list from Snowflake, including SEARCH_ON column
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUITNAME'), col('SEARCH_ON')).collect()

# Convert Snowflake result into a dictionary {Fruit Name -> Search On Value}
fruit_dict = {row["FRUITNAME"]: row["SEARCH_ON"] for row in my_dataframe}

# Debugging step: Display the dataframe to verify correct retrieval
st.dataframe(data=my_dataframe, use_container_width=True)
st.stop()  # Pause execution to inspect dataframe before continuing

# Multiselect for fruit choices (users see FRUITNAME, but we use SEARCH_ON for API calls)
ingredients_list = st.multiselect("Choose your ingredients:", list(fruit_dict.keys()))

# Validation: Ensure max 5 ingredients
if len(ingredients_list) > 5:
    st.error("You can only select up to 5 ingredients! Please remove one or more.")

# Show nutrition info for selected fruits using SEARCH_ON values
if ingredients_list:
    for fruit_chosen in ingredients_list:
        search_term = fruit_dict[fruit_chosen]  # Lookup SEARCH_ON value

        st.subheader(f"{fruit_chosen} Nutrition Information")
        response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_term}")

        if response.status_code == 200:
            sf_df = response.json()
            st.dataframe(data=sf_df, use_container_width=True)
        else:
            st.write(f"Sorry, {fruit_chosen} ({search_term}) is not in the Fruitvice database.")

# Submit button to store order in Snowflake
if ingredients_list and len(ingredients_list) <= 5:
    ingredients_string = ', '.join(ingredients_list)

    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}! ✅")
