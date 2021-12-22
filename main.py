import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# -----------------------------------Encode CSV File-----------------------------------
# df = pd.read_csv("superstore_dataset2011-2015.csv", encoding='latin-1')
# df.to_csv("superstore_dataset2011-2015_new.csv", index=False)

# ------------------------------------Load All Data------------------------------------
@st.cache
def load_all_data():
    df = pd.read_csv("superstore_dataset2011-2015_new.csv")
    df = df.drop(["City", "State", "Postal Code", "Market", "Country", "Discount",
                  "Shipping Cost", "Order Priority", "Ship Mode", "Row ID"], axis=1)
    return df

df_all_data = load_all_data()

# ----------------------------------Side Bar select box----------------------------------

def selectbox():
    add_selectbox = st.sidebar.selectbox(
        "Menu",
        ("Data Table", "Sales by Region", "Sales & Profits by Product Type", "Sales by Customer Segment", "Sales by Stock",
         "Sales & Profits by Date")
    )
    print("add_selectbox", add_selectbox)
    return add_selectbox

add_selectbox = selectbox()

st.title('Super Store Report')

# -------------------------------------00 Summary Data-----------------------------------

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        sum_of_sale = df_all_data['Sales'].sum()
        st.write(f'Total Sales: $ {format(sum_of_sale, ".2f")}')
        avg_units_per_customer = df_all_data['Quantity'].sum() / (len(df_all_data['Customer Name'].unique()))
        st.write(f'Avg units of sales/customer: {format(avg_units_per_customer, ".0f")}')

    with col2:
        sum_of_customer = len(df_all_data['Customer Name'].unique())
        st.write(f'Number of Customers: {sum_of_customer}')
        avg_transaction_price = sum_of_sale / sum_of_customer
        st.write(f'Avg Transaction Price : $ {format(avg_transaction_price, ".2f")}')

# --------------------------------------01 Data Table------------------------------------

if add_selectbox == "Data Table":
    def data_table():
        st.subheader("Data Table")
        st.write("***You can search the order by Customer Name / Customer ID / Order ID***")

        search_keyword = st.text_input("Search", placeholder="Search Customer Name/ID OR Order ID")
        with st.spinner('Wait for it...'):
            st.dataframe(df_all_data[
                             df_all_data['Customer ID'].str.contains(search_keyword) |
                             df_all_data['Customer Name'].str.contains(search_keyword) |
                             df_all_data['Order ID'].str.contains(search_keyword)
                             ].reset_index().set_index('index'), height=400)
        st.success('Done')
        return 0
    data_table = data_table()

# -----------------------------------02 Sales By Region---------------------------------

elif add_selectbox == "Sales by Region":
    def region():
        df_region = df_all_data[['Region', 'Profit', 'Quantity', 'Sales']].groupby(['Region']).sum().reset_index()

        st.subheader("Pie Chart - Sales by Region")
        method = df_region['Region']
        method_data = df_region['Sales']
        labels = method
        sizes = method_data
        fig1, ax1 = plt.subplots()

        ax1.pie(sizes, labels=labels, autopct='%1.1f%%')
        ax1.axis('equal')
        st.pyplot(fig1)

        st.subheader("Table - Sales by Region")
        st.dataframe(data=df_region, width=650, height=650)
        return 0
    region = region()

# -----------------------------------03 Sales By Product Type---------------------------------

elif add_selectbox == "Sales & Profits by Product Type":
    def product_type():
        df_category = df_all_data[['Sub-Category','Profit', 'Sales']].groupby(['Sub-Category']).sum().reset_index()

        st.subheader("Bar Chart - Sales & Profits by Product Type")
        df_category = df_category.set_index('Sub-Category')
        st.bar_chart(df_category)

        st.subheader("Table - Sales & Profits by Product Type")
        df_category2 = df_all_data[['Sub-Category', 'Sales', 'Quantity', 'Profit']].groupby(['Sub-Category']).sum().reset_index()
        st.dataframe(data=df_category2, width=650, height=650)
        return 0
    product_type = product_type()

# -------------------------------------04 Profits By Segment-----------------------------------

elif add_selectbox == "Sales by Customer Segment":
    def segmentation():
        df_segment3 = df_all_data[['Segment', 'Category', 'Profit']].groupby(['Segment', 'Category']).sum().reset_index()

        st.subheader("Bar Chart - Profits by Customer Segment & Product Category")
        df_segment2 = df_segment3.set_index(['Category', 'Segment'])['Profit'].unstack().reset_index()

        fig, ax = plt.subplots()
        plt.figure(figsize=(8, 8))

        x = df_segment2['Category']
        y1 = df_segment2['Consumer']
        y2 = df_segment2['Corporate']
        y3 = df_segment2['Home Office']
        fig = px.bar(df_segment2, x=x, y=[y1, y2, y3], barmode='group')
        st.plotly_chart(fig)

        st.subheader("Table - Profits by Customer Segment & Product Category")
        st.dataframe(data=df_segment3, width=650, height=650)
        return 0
    segmentation = segmentation()

# -------------------------------------05 Sales by Stock-----------------------------------

elif add_selectbox == "Sales by Stock":
    def stock_of_product():
        df_stock = df_all_data[['Product ID', 'Product Name', 'Quantity', ]].groupby(['Product ID', 'Product Name']).sum().reset_index()
        df_stock = df_stock.rename({'Quantity': 'Quantity of Sales'}, axis=1)
        df_stock['Stock Count'] = (90 - df_stock['Quantity of Sales'])

        a = df_stock[df_stock['Stock Count'] < 0].count().count()

        def stock_replenish():
            if a > 0:
                    st.subheader("Urgent!!!! need to be replenished")
                    df_stock_need = df_stock[df_stock['Stock Count'] < 0]
                    st.dataframe(df_stock_need)
            else:
                pass

        stock_replenish()

        st.subheader("Table - Product Stock & Sales")
        st.write("You can check the product stock by Product Name & Product ID")
        search_keyword2 = st.text_input("Search", placeholder="Search Product ID or Product Name")
        with st.spinner('Wait for it...'):
            st.dataframe(df_stock[
                             df_stock['Product ID'].str.contains(search_keyword2) |
                             df_stock['Product Name'].str.contains(search_keyword2)
                             ].reset_index().set_index('index'), height=400)
        st.success('Done')

        df_stock2 = df_stock[['Quantity of Sales','Stock Count']]
        st.subheader("Area Chart - Stock Count vs Sales")
        st.area_chart(df_stock2, width=1000)

        return 0

    stock_of_product = stock_of_product()

# -------------------------------------06 Sales by Date-----------------------------------

elif add_selectbox == "Sales & Profits by Date":
    def sales_by_date():
        st.subheader("Line Chart - Profits & Sales in these 4 years")
        df_new_all = df_all_data.copy()
        df_new_all['Order Date'] = df_new_all['Order Date'].str.replace("-", "/")
        df_new_all['Order Date'] = pd.to_datetime(df_new_all['Order Date'], format='%d/%m/%Y')
        df_new_all['Year'] = pd.DatetimeIndex(df_new_all['Order Date']).year
        df_year_sale = df_new_all[['Year', 'Sales', 'Profit']].groupby(['Year']).sum()
        st.line_chart(df_year_sale)

        select_year = st.slider('Which Year Do want to check?', 2011, 2014, 2014)
        st.write("Select ", select_year, 'Year')
        st.subheader(f"Table - Profits & Sales by Product Category in {select_year}")
        df_date = df_new_all[['Year', 'Sales', 'Profit', 'Sub-Category']].groupby(['Year', 'Sub-Category']).sum().reset_index()
        df_date = df_date[df_date['Year'] == select_year]
        df_date2 = df_date[['Sub-Category', 'Sales', 'Profit']].set_index('Sub-Category').reset_index()
        st.dataframe(df_date2)
        st.write('Table - Bar Chart')
        df_date3 = df_date[['Sub-Category', 'Sales', 'Profit']].set_index('Sub-Category')
        st.bar_chart(df_date3)
        return 0
    sales_by_date = sales_by_date()

# ----------------------------------------Finished--------------------------------------

else:
    pass

