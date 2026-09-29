import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

try:
    df = pd.read_excel("Sample - Superstore 2019.xls")
    print("File loaded successfully.")
except FileNotFoundError:
    print("File not found.")
    print("Error: The file was not found.")
    exit()
except Exception as e:
    print(f"An error occurred: {e}")
    exit()


df.info()   
print(df.shape) 
df.describe()
print(df.columns)
print(df.isnull().sum())
mss = df.isnull().mean()*100
print("number of missing is : " , mss)
dub = df.duplicated().sum()
print ("number of dublicates = "  , dub)
missing_postal = df[df["Postal Code"].isnull()]
print(missing_postal)

#""""""""""Reusable Preprocessing Function""""""""""""""""""

def convert_dates(df):
        df = df.copy()
        df["Order Date"] = pd.to_datetime(df["Order Date"])
        df["Ship Date"] = pd.to_datetime(df["Ship Date"])
        return df
def remove_duplicates(df):
    df= df.copy()
    df= df.drop_duplicates()
    return df

def handle_missing_values(df):
    df = df.copy()
    df["Postal Code"]= df["Postal Code"].fillna(df["Postal Code"].median())
    return df

def clean_text_columns(df):
    df= df.copy()
    text_columns = df.select_dtypes(include =  "object").columns
    for col in text_columns :
        df[col]= df[col].str.strip()
        df[col]= df[col].str.replace(r"\s+", " ", regex=True) #if there is whitespaces ,remove it
    return df


def preprocess_data(df):
  try:
        df = convert_dates(df)
        df = handle_missing_values(df)
        df = remove_duplicates(df)
        df= clean_text_columns(df)
        return df
  except KeyError as k:   
      print("missing column : " + k)
      return None
  except Exception as e:
      print(f"There is an error: {e}")
      return None



  
df_clean = preprocess_data(df)

df_clean.info()
df_clean["Postal Code"] = df_clean["Postal Code"].astype("Int64")
print("Missing Postal Codes:", df_clean["Postal Code"].isnull().sum())
print("Original shape:", df.shape)
print("Cleaned shape:", df_clean.shape)

#-----------------------------------------------------------------------------
#detect Outliers 
Q1_sales = df_clean["Sales"].quantile(0.25)
Q3_sales = df_clean["Sales"].quantile(0.75)

print("Q1:", Q1_sales)
print("Q3:", Q3_sales)
IQR_sales = Q3_sales - Q1_sales

print("IQR:", IQR_sales)

lower_sales = Q1_sales - 1.5 * IQR_sales
upper_sales = Q3_sales + 1.5 * IQR_sales

print("Lower Bound:", lower_sales)
print("Upper Bound:", upper_sales)


sales_outliers = df_clean[
    (df_clean["Sales"] > upper_sales)|
    (df_clean["Sales"] < lower_sales)
]

print("Number of Sales outliers:", len(sales_outliers))
print(sales_outliers["Sales"].sort_values(ascending=False).head(10))
len(sales_outliers)



Q1_profit= df_clean["Profit"].quantile(0.25)
Q3_profit= df_clean["Profit"].quantile(0.75)

print("Q1 profit : " ,Q1_profit )
print("Q3 profit : " ,Q3_profit)

IQR_profit= Q3_profit - Q1_profit
print("IQR Profit:", IQR_profit)

lower_profit =Q1_profit- 1.5*IQR_profit
upper_profit =Q3_profit+ 1.5*IQR_profit
print("Lower Bound Profit:", lower_profit)
print("Upper Bound Profit:", upper_profit)
# print("Max profit: " , df_clean["Profit"].max())
profit_outliers= df_clean[
        (df_clean["Profit"]< lower_profit)|
        (df_clean["Profit"]> upper_profit)
]

print("Number of profit outliers: " , len(profit_outliers))

print(profit_outliers["Profit"].sort_values(ascending= False).head(10))
print(profit_outliers["Profit"].sort_values(ascending=True).head(10))
print("Negative Sales:", (df_clean["Sales"] < 0).sum())
print("Invalid Quantity:", (df_clean["Quantity"] <= 0).sum())
print("Invalid Discount:", ((df_clean["Discount"] < 0) | (df_clean["Discount"] > 1)).sum())
print(df_clean[["Order Date", "Ship Date", "Sales", "Quantity", "Discount", "Profit"]].dtypes)

#-------------------------------------------------


def create_features(df):
     df = df.copy()
     df["Profit Margin"] = (df["Profit"] / df["Sales"])*100

     df["Shipping Duration"] = (df["Ship Date"] - df["Order Date"]).dt.days

     df["Sales Performance Category"] =pd.cut(
        df["Sales"], bins=[0, 100, 500, float("inf")],labels=["Low", "Medium", "High"])
     return df
df_clean = create_features(df_clean)




class DataAnalyzer:

    def __init__(self, df):
        self.df = df

    def calculate_kpis(self):
        kpis = {
            "Total Sales": self.df["Sales"].sum(),
            "Total Profit": self.df["Profit"].sum(),
            "Total Quantity": self.df["Quantity"].sum(),
            "Average Sales": self.df["Sales"].mean(),
            "Average Profit": self.df["Profit"].mean(),
            "Average Discount": self.df["Discount"].mean()
        }

        return kpis

analyzer = DataAnalyzer(df_clean)

kpi_summary = analyzer.calculate_kpis()

print("KPI Summary:")

for key, value in kpi_summary.items():
    print(f"{key}: {value:.2f}")


try:
    with open("Superstore_Analytical_Report.txt", "w") as file:

        file.write("SUPERSTORE ANALYTICAL REPORT\n")
        file.write("=" * 40 + "\n\n")

        file.write("KPI SUMMARY\n")
        file.write("-" * 20 + "\n")

        for key, value in kpi_summary.items():
            file.write(f"{key}: {value:.2f}\n")

        file.write("\nEDA INSIGHTS\n")
        file.write("-" * 20 + "\n")

        file.write(
            "1. Technology has the highest total sales and profit among all categories.\n"
        )

        file.write(
            "2. Furniture has relatively high sales but the lowest total profit, "
            "which indicates lower profitability compared with the other categories.\n"
        )

        file.write(
            "3. The West region has the highest total sales, while the South region "
            "has the lowest total sales.\n"
        )

        file.write(
            "4. Sales generally increase toward the end of the year, with November 2019 "
            "recording the highest monthly sales.\n"
        )

        file.write(
            "5. Consumer is the largest customer segment by sales, followed by Corporate "
            "and Home Office.\n"
        )

        file.write(
            "6. Sean Miller is the top customer by total sales.\n"
        )

        file.write(
            "7. Technology has the highest profit margin at 17.39%, while Furniture "
            "has the lowest at 2.49%.\n"
        )

    print("Analytical report generated successfully.")

except Exception as e:
    print(f"An error occurred while exporting the report: {e}")



#------------------------------------------------------------------
#corr.
numeric_cols = df_clean.select_dtypes(include="number")
print(numeric_cols.columns)
correlation_data = df_clean[
    ["Sales", "Quantity", "Discount", "Profit", "Profit Margin", "Shipping Duration"]
]
print(correlation_data.corr())

try:
  df_clean.to_excel("Cleaned- Superstore.xlsx" , index = False)
  print("Cleaned dataset exported successfully.")
except Exception as e:
  print(f"An error occurred while exporting the cleaned dataset: {e}")



#---------------------------------Memory ----------------------------------

print("Memory usage before optimization:")
print(df_clean.memory_usage(deep=True).sum() / 1024**2, "MB")

for col in ["Ship Mode", "Segment", "Country/Region",
            "Region", "Category", "Sub-Category"]:
    df_clean[col] = df_clean[col].astype("category")

print("Memory usage after optimization:")
print(df_clean.memory_usage(deep=True).sum() / 1024**2, "MB")


#==================================
category_sales = df_clean.groupby("Category")["Sales"].sum()

region_sales = df_clean.groupby("Region")["Sales"].sum()

category_profit = df_clean.groupby("Category")["Profit"].sum()

sales_over_time = df_clean.groupby(df_clean["Order Date"].dt.to_period("M"))["Sales"].sum()

profit_over_time = df_clean.groupby(df_clean["Order Date"].dt.to_period("M"))["Profit"].sum()

segment_sales = df_clean.groupby("Segment")["Sales"].sum()

Top_10_Customers = (df_clean.groupby("Customer Name")["Sales"].sum().sort_values(ascending=False).head(10))

category_profit_margin = (category_profit / category_sales) * 100



# EDA Insights
print("\nEDA Insights")
print("-" * 40)

print("Technology has the highest total sales and profit among all categories.")

print("Furniture has relatively high sales but the lowest total profit, "
      "which may indicate lower profitability compared with other categories.")

print("The West region has the highest total sales, while the South region "
      "has the lowest total sales.")

print("Sales generally increase toward the end of the year, with November 2019 "
      "recording the highest monthly sales.")

print("Profit varies over time and includes some negative months, such as "
      "July 2016 and January 2017.")

print("Consumer is the largest customer segment by sales, followed by Corporate "
      "and Home Office.")

print("Sean Miller is the top customer by total sales.")

print("Technology has the highest profit margin at 17.39%, while Furniture "
      "has the lowest at 2.49%. Office Supplies has a profit margin of 17.03%.")


#---------------------------------------------------------------

#visualization

def plot_bar_chart(data, title, xlabel, ylabel):
    try:
        plt.figure(figsize=(8, 5))
        data.plot(kind="bar")
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.show()
    except Exception as e:
        print(f"An error occurred while plotting the bar chart: {e}")


def plot_line_chart(data, title, xlabel, ylabel):
    try:
       plt.figure(figsize=(8, 5))
       data.plot(kind="line")
       plt.title(title)
       plt.xlabel(xlabel)
       plt.ylabel(ylabel)
       plt.show()
    except Exception as e:
        print(f"An error occurred while plotting the line chart: {e}")


def plot_pie_chart(data, title):
    try:
       plt.figure(figsize=(8, 5))
       plt.pie(data,labels=data.index,autopct="%1.1f%%")
       plt.title(title)
       plt.show()
    except Exception as e:
        print(f"An error occurred while plotting the pie chart: {e}")


def plot_scatter_chart(x, y, title, xlabel, ylabel):
    try:
       plt.figure(figsize=(8, 5))
       plt.scatter(x, y)
       plt.title(title)
       plt.xlabel(xlabel)
       plt.ylabel(ylabel)
       plt.show()
    except Exception as e:
        print(f"An error occurred while plotting the scatter chart: {e}")


def plot_histogram(data, title, xlabel, ylabel):
    try: 
       plt.figure(figsize=(8, 5))
       sns.histplot(data, kde=True)
       plt.title(title)
       plt.xlabel(xlabel)
       plt.ylabel(ylabel)
       plt.show()
    except Exception as e:
        print(f"An error occurred while plotting the histogram: {e}")




#-----------------------------

plot_bar_chart(
    category_sales,
    "Sales by Category",
    "Category",
    "Sales"
)

plot_bar_chart(
    region_sales,
    "Sales by Region",
    "Region",
    "Total Sales"
)

plot_bar_chart(
    category_profit,
    "Profit by Category",
    "Category",
    "Profit"
)

plot_bar_chart(
    Top_10_Customers,
    "Top 10 Customers by Sales",
    "Customer Name",
    "Sales"
)

plot_line_chart(
    sales_over_time,
    "Sales Over Time",
    "Time",
    "Sales"
)

plot_line_chart(
    profit_over_time,
    "Profit Over Time",
    "Time",
    "Profit"
)

plot_pie_chart(
    segment_sales,
    "Sales by Segment"
)

plot_scatter_chart(
    df_clean["Discount"],
    df_clean["Profit"],
    "Discount vs Profit",
    "Discount",
    "Profit"
)

plot_bar_chart(
    category_profit_margin,
    "Profit Margin by Category",
    "Category",
    "Profit Margin (%)"
)

plot_histogram(
    df_clean["Sales"],
    "Sales Distribution",
    "Sales",
    "Frequency")
# ---------------Dashboard1---------------

def Sales_Dashboard(category_sales , region_sales, sales_over_time ,Sales_Segment , kpi_summary ):
    fig, axes = plt.subplots(2, 2, figsize=(18, 14))

# Dashboard title
    fig.suptitle(
    "Sales Performance Dashboard",
    fontsize=22,
    color="#3F2D35",
    fontweight="bold",
    y=0.99
    )

# KPI Cards
    fig.text(
    0.18, 0.90,
    f"Total Sales\n${kpi_summary['Total Sales']:,.2f}",
    ha="center",
    va="center",
    fontsize=12,
    fontweight="bold",
    color="#A94F32",
    bbox=dict(boxstyle="round,pad=0.6", facecolor="#FCEDE7", edgecolor="#D97757")
    )

    fig.text(
    0.40, 0.90,
    f"Total Profit\n${kpi_summary['Total Profit']:,.2f}",
    ha="center",
    va="center",
    fontsize=12,
    fontweight="bold",
    color="#A96334",
    bbox=dict(boxstyle="round,pad=0.6", facecolor="#FCEDE8" ,edgecolor="#D97757" )
    )

    fig.text(
    0.62, 0.90,
    f"Total Quantity\n{kpi_summary['Total Quantity']:,.0f}",
    ha="center",
    va="center",
    fontsize=12,
    fontweight="bold",
    color="#A96338",
    bbox=dict(boxstyle="round,pad=0.6", facecolor="#FFF3E8" ,edgecolor="#E9A178", )
    )

    fig.text(
    0.82, 0.90,
    f"Average Sales\n${kpi_summary['Average Sales']:,.2f}",
    ha="center",
    va="center",
    fontsize=12,
    fontweight="bold",
    color="#8F4935" ,
    bbox=dict(boxstyle="round,pad=0.6" ,facecolor="#FFF9F5" ,edgecolor="#C96C4A")
    )





    category_sales.plot(kind="bar", ax=axes[0, 0] , color="#D97757")
    axes[0, 0].set_title("Sales by Category", fontsize=16, fontweight="bold")
    axes[0, 0].set_xlabel("Category", fontsize=12)
    axes[0, 0].set_ylabel("Sales", fontsize=12)
    axes[0, 0].tick_params(axis="x", rotation=0)


    region_sales.plot(kind="bar", ax=axes[0, 1] , color="#E9A178")
    axes[0, 1].set_title("Sales by Region", fontsize=16, fontweight="bold")
    axes[0, 1].set_xlabel("Region", fontsize=12)
    axes[0, 1].set_ylabel("Sales", fontsize=12)
    axes[0, 1].tick_params(axis="x", rotation=0)


    sales_over_time.plot(kind="line", ax=axes[1, 0], linewidth=2 , color="#A94F32")
    axes[1, 0].set_title("Sales Over Time", fontsize=16, fontweight="bold")
    axes[1, 0].set_xlabel("Time", fontsize=12)
    axes[1, 0].set_ylabel("Sales", fontsize=12)
    axes[1, 0].tick_params(axis="x", rotation=45)


    axes[1, 1].pie(segment_sales,labels=segment_sales.index,autopct="%1.1f%%",textprops={"fontsize": 12} , colors=["#C96C4A","#D1B7AD","#C74313"])
    axes[1, 1].set_title("Sales by Segment", fontsize=16, fontweight="bold")

    

    

    plt.subplots_adjust(
    top=0.78,
    hspace=0.55,
    wspace=0.25
    )
    try:
       plt.savefig("Sales_Dashboard.png",dpi=300,bbox_inches="tight")
    except Exception as e:
        print(f"An error occurred while saving the image: {e}")
    plt.show()





# ---------------DASHBOARD 2 -----------------

def Profit_Dashboard(category_profit ,profit_over_time ,  discount, profit, category_profit_margin, kpi_summary ):
    fig, axes = plt.subplots(2, 2, figsize=(18, 14))

# Dashboard title
    fig.suptitle(
    "Profit Performance Dashboard",
    fontsize=22,
    color="#3F2D35",
    fontweight="bold",
    y=0.99
)

# KPI Cards
    fig.text(
    0.18, 0.90,
    f"Total Sales\n${kpi_summary['Total Sales']:,.2f}",
    ha="center",
    va="center",
    fontsize=12,
    color="#7C3F58" ,
    fontweight="bold",
    bbox=dict(boxstyle="round,pad=0.6", facecolor="#F4EAF0",edgecolor="#7C3F58")
)

    fig.text(
    0.40, 0.90,
    f"Total Profit\n${kpi_summary['Total Profit']:,.2f}",
    ha="center",
    va="center",
    fontsize=12,
    color = "#7C3F58",
    fontweight="bold",
    bbox=dict(boxstyle="round,pad=0.6", facecolor="#F4EAF0", edgecolor="#7C3F58")
)

    fig.text(
    0.62, 0.90,
    f"Total Quantity\n{kpi_summary['Total Quantity']:,.0f}",
    ha="center",
    va="center",
    fontsize=12,
    color="#7c3F58",
    fontweight="bold",
    bbox=dict(boxstyle="round,pad=0.6", facecolor="#F4EAF0", edgecolor="#7C3F58")
)

    fig.text(
    0.82, 0.90,
    f"Average Sales\n${kpi_summary['Average Sales']:,.2f}",
    ha="center",
    va="center",
    fontsize=12,
    color="#7C3F58",
    fontweight="bold",
    bbox=dict(boxstyle="round,pad=0.6", facecolor="#F4EAF0", edgecolor="#7C3F58")
     )


    category_profit.plot(kind="bar", ax=axes[0, 0], color="#7C3F58")
    axes[0, 0].set_title("Profit by Category", fontsize=16, fontweight="bold")
    axes[0, 0].set_xlabel("Category", fontsize=12)
    axes[0, 0].set_ylabel("Profit", fontsize=12)
    axes[0, 0].tick_params(axis="x", rotation=0)


    profit_over_time.plot(kind="line", ax=axes[0, 1], linewidth=2 ,color="#A86B83")
    axes[0, 1].set_title("Profit Over Time", fontsize=16, fontweight="bold")
    axes[0, 1].set_xlabel("Time", fontsize=12)
    axes[0, 1].set_ylabel("Profit", fontsize=12)
    axes[0, 1].tick_params(axis="x", rotation=45)


    axes[1, 0].scatter(discount, profit, alpha=0.5, color="#D46A6A")
    axes[1, 0].set_title("Discount vs Profit",fontsize=16,fontweight="bold" )
    axes[1, 0].set_xlabel("Discount", fontsize=12)
    axes[1, 0].set_ylabel("Profit", fontsize=12)

    category_profit_margin.plot(kind="bar", ax=axes[1, 1], color="#9B5C78")
    axes[1, 1].set_title("Profit Margin by Category", fontsize=16, fontweight="bold")
    axes[1, 1].set_xlabel("Category", fontsize=12)
    axes[1, 1].set_ylabel("Profit Margin (%)", fontsize=12)
    axes[1, 1].tick_params(axis="x", rotation=0)



    plt.subplots_adjust(
    top=0.78,
    hspace=0.65,
    wspace=0.25
    )
    try:
        plt.savefig("Profit_Dashboard.png",dpi=300,bbox_inches="tight")
    except Exception as e:
        print(f"An error occurred while saving the image: {e}")
    plt.show()




Sales_Dashboard(
    category_sales,
    region_sales,
    sales_over_time,
    segment_sales,
    kpi_summary
)


Profit_Dashboard(
    category_profit ,
    profit_over_time ,  
    df_clean["Discount"],
    df_clean["Profit"], 
    category_profit_margin,
    kpi_summary
)



#-----------------------------------------

