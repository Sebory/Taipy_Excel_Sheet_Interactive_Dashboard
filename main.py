from taipy.gui import Gui, notify
import taipy.gui.builder as tgb
import pandas as pd

# Load data from Excel
data = pd.read_excel("./supermarket_sales.xlsx", usecols='B:R', skiprows=3, nrows=1000)

# Add 'hour' column to dataframe
data["hour"] = pd.to_datetime(data["Time"], format="%H:%M:%S").dt.hour

cities = list(data["City"].unique())
customer_types = list(data["Customer_type"].unique())
genders = list(data["Gender"].unique())

layout = {
  "xaxis": {"title": ""},
  "yaxis": {"title": ""},
  "margin": {"t": 150},
}

def on_filter(state):
  if (
    len(state.cities) == 0
    or len(state.customer_types) == 0
    or len(state.genders) == 0
  ):
    notify(state, "Error", "No result found. Check the filters.")
    return
  state.data_filtered, state.sales_by_product_line, state.sales_by_hour = filter_data(
    state.cities, state.customer_types, state.genders
  )

def filter_data(cities, customer_types, genders):
  data_filtered = data[data["City"].isin(cities) & data["Customer_type"].isin(customer_types) & data["Gender"].isin(genders)]
  sales_by_product_line = data_filtered[["Product line", "Total"]].groupby("Product line").sum().sort_values("Total", ascending=True).reset_index()
  sales_by_hour = data_filtered[["hour", "Total"]].groupby("hour").sum().reset_index()
  return data_filtered, sales_by_product_line, sales_by_hour

def to_text(value):
  return "{:,}".format(int(value))

# Page building
with tgb.Page() as page:
  tgb.text("📊 Sales Dashboard", class_name="h1 text-center pb2")
  tgb.toggle(theme=True)

  with tgb.layout("1 1 1", class_name="p1"):
    with tgb.part(class_name="card"):
      tgb.text("## Total Sales:", mode="md")
      tgb.text("US $ {to_text(data_filtered['Total'].sum())}", class_name="h4")
    with tgb.part(class_name="card"):
      tgb.text("## Average Sales:", mode="md")
      tgb.text("US $ {to_text(data_filtered['Total'].mean())}", class_name="h4")
    with tgb.part(class_name="card"):
      tgb.text("## Average Rating:", mode="md")
      tgb.text("{round(data_filtered['Rating'].mean(),1)}  {'⭐'*int(round(data_filtered['Rating'].mean()))}", class_name="h4")

  with tgb.layout("1 1 1"):
    tgb.selector(
      value="{cities}",
      lov=cities,
      dropdown=True,
      multiple=True,
      label="Select cities",
      class_name="fullwidth",
      on_change=on_filter,
    )
    
    tgb.selector(
      value="{customer_types}",
      lov=customer_types,
      dropdown=True,
      multiple=True,
      label="Select customer types",
      class_name="fullwidth",
      on_change=on_filter,
    )

    tgb.selector(
      value="{genders}",
      lov=genders,
      dropdown=True,
      multiple=True,
      label="Select genders",
      class_name="fullwidth",
      on_change=on_filter,
    )

  with tgb.layout("1 1"):
    tgb.chart(
      "{sales_by_hour}",
      x="hour",
      y="Total",
      type="bar",
      title="Sales by Hour",
      layout=layout,
      class_name="card-chart",
    )
    tgb.chart(
      "{sales_by_product_line}",
      x="Total",
      y="Product line",
      type="bar",
      orientation="h",
      title="Sales by Product Line",
      layout=layout,
      class_name="card-chart",
    )

# Create the Gui object and run the application
if __name__ == "__main__":
  data_filtered, sales_by_product_line, sales_by_hour = filter_data(cities, customer_types, genders)
  gui = Gui(page, css_file="styles.css")
  gui.run(
    title="Sales Dashboard",
    use_reloader=True,
    debug=True,
    watermark="Made with 🧡 by Dr Diaby",
    margin="4em",
    stylekit={
      "color_primary": "#FF0000",
      "color_secondary": "#C0FFE",
    }
  )
