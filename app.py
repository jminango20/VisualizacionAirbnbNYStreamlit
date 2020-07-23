#Created by Juan Minango
import pandas as pd
import streamlit as st
import plotly.express as px

#Voy a leer la base de datos de precios de Airbnb de la ciudad de Nueva York
@st.cache
def get_data():
    return pd.read_csv("http://data.insideairbnb.com/united-states/ny/new-york-city/2019-09-12/visualisations/listings.csv")

df = get_data()
st.title("Tutorial de Uso de Streamlit para Visualización")
st.markdown("Para este ejercicio usaremos el [dataset](http://data.insideairbnb.com/united-states/ny/new-york-city/2019-09-12/visualisations/listings.csv) de precios de Airbnb en la ciudad de Nueva York.")
st.header("Airbnb NYC Lista:")
st.markdown("Las 5 primeras lineas del dataset Airbnb NYC descargado.")
st.dataframe(df.head())
st.header("Almacenamiento en caché de los datos")
st.markdown("Streamlit tiene un práctido decorador [`st.cache`](https://streamlit.io/docs/api.html#optimize-performance) para habilitar el almacenamiento en caché de los datos.")
#Ejemplo de colocar codigo en Streamlit
st.code("""
@st.cache
def get_data():
    url = "http://data.insideairbnb.com/united-states/ny/new-york-city/2019-09-12/visualisations/listings.csv"
    return pd.read_csv(url)
""", language="python")
st.markdown("_Para mostrar un bloque de código pulse en el string [`st.code`](https://streamlit.io/docs/api.html#streamlit.code)_.")
with st.echo():
    st.markdown("Alternativamente se puede usar [`st.echo`](https://streamlit.io/docs/api.html#streamlit.echo).")

st.header("¿Dónde se encuentran las propiedades más caras en NY?")
st.subheader("Visualizando en el Mapa")
st.markdown("El siguiente mapa muestra el 1% de Airbnbs más caros con un precio de $ 800 o más.")
st.map(df.query("price>=800")[["latitude", "longitude"]].dropna(how="any"))
st.subheader("Visualizando en una Tabla")
st.markdown("A continuación el top 5 de las propiedades más caras.")
st.write(df.query("price>=800").sort_values("price", ascending=False).head())

st.subheader("Seleccionando un subconjunto de columnas")
st.write(f"De las {df.shape[1]} columnas del dataset, a veces deseamos solamente visualizar un subconjunto de ellas. Streamlit tiene [multiselect](https://streamlit.io/docs/api.html#streamlit.multiselect) widget para este fin.")
defaultcols = ["name", "host_name", "neighbourhood", "room_type", "price"]
cols = st.multiselect("Columns", df.columns.tolist(), default=defaultcols)
st.dataframe(df[cols].head(10))

st.header("Precio medio por tipo de habitación")
st.write("También podemos mostrar tablas estáticas. A diferencia de un dataframe, con una tabla estática no se puede ordenar haciendo clic en el encabezado de una columna.")
st.table(df.groupby("room_type").price.mean().reset_index()\
    .round(2).sort_values("price", ascending=False)\
    .assign(avg_price=lambda x: x.pop("price").apply(lambda y: "%.2f" % y)))

st.header("¿Qué anfitrión tiene la mayoría de las propiedades?")
listingcounts = df.host_id.value_counts()
top_host_1 = df.query('host_id==@listingcounts.index[0]')
top_host_2 = df.query('host_id==@listingcounts.index[1]')
st.write(f"""**{top_host_1.iloc[0].host_name}** es el top 1 con {listingcounts.iloc[0]} propiedades en el dataset.
**{top_host_2.iloc[1].host_name}** is el segundo con {listingcounts.iloc[1]} propiedades en el dataset. Los siguientes propietarios son elegidos al azar
a parte además de los 2 tops. Este resultado se muestra en un archivo JSON usando [`st.json`](https://streamlit.io/docs/api.html#streamlit.json).""")

st.json({top_host_1.iloc[0].host_name: top_host_1\
    [["name", "neighbourhood", "room_type", "minimum_nights", "price"]]\
        .sample(2, random_state=4).to_dict(orient="records"),
        top_host_2.iloc[0].host_name: top_host_2\
    [["name", "neighbourhood", "room_type", "minimum_nights", "price"]]\
        .sample(2, random_state=4).to_dict(orient="records")})

st.header("¿Cuál es la distribución del precio de las propiedades?")
st.write("""Seleccione un rango de precios personalizado de la barra lateral para actualizar el histograma que se muestra a continuación como un gráfico de trazado usando
[`st.plotly_chart`](https://streamlit.io/docs/api.html#streamlit.plotly_chart).""")
values = st.sidebar.slider("Rango de precios", float(df.price.min()), float(df.price.clip(upper=1000.).max()), (50., 300.))
f = px.histogram(df.query(f"price.between{values}"), x="price", nbins=15, title="Distribución de los Precios")
f.update_xaxes(title="Precio")
f.update_yaxes(title="No. de propiedades listadas")
st.plotly_chart(f)

st.header("¿Cuál es la distribución de disponibilidad en varios vecindarios?")
st.write("Usando un botón de radio restringe la selección a solo una opción a la vez.")
st.write("💡 Observe cómo usamos una tabla estática a continuación en lugar de un dataframe. \
        A diferencia de un dataframe, si el contenido se desborda del margen de la sección, \
            una tabla estática no lo oculta automáticamente dentro de un área desplazable. \
            En cambio, el contenido desbordado permanece visible.")
neighborhood = st.radio("Vecindarios", df.neighbourhood_group.unique())
show_exp = st.checkbox("Incluir propiedades caras")
show_exp = " and price<200" if not show_exp else ""

@st.cache
def get_availability(show_exp, neighborhood):
    return df.query(f"""neighbourhood_group==@neighborhood{show_exp}\
        and availability_365>0""").availability_365.describe(\
            percentiles=[.1, .25, .5, .75, .9, .99]).to_frame().T

st.table(get_availability(show_exp, neighborhood))

df.query("availability_365>0").groupby("neighbourhood_group")\
    .availability_365.mean().plot.bar(rot=0).set(title="Disponibilidad promedio por grupo de vecindario",
        xlabel="Grupo Vecindario", ylabel="Disponibilidad média (en no. de dias)")
st.pyplot()

st.header("Propiedades por número de opiniones")
st.write("Ingrese un rango de números en la barra lateral para ver las propiedades cuyo recuento de revisiones cae en ese rango.")
minimum = st.sidebar.number_input("Mínimo", min_value=0.0)
maximum = st.sidebar.number_input("Máximo", min_value=0.0, value=5.0)
if minimum > maximum:
    st.error("Por favor ingrese un rando válido")
else:
    df.query("@minimum<=number_of_reviews<=@maximum").sort_values("number_of_reviews", ascending=False)\
        .head(50)[["name", "number_of_reviews", "neighbourhood", "host_name", "room_type", "price"]]

st.write("486 es el número más alto de comentarios y dos propiedades lo tienen.\
     Ambos están en el Este de Elmhurst y son habitaciones privadas con precios de $ 65 y $ 45. \
     En general, los listados con más de 400 comentarios tienen un precio inferior a $ 100. \
     Algunos cuestan entre $ 100 y $ 200, y solo uno tiene un precio superior a $ 200.")

#EXTRA
st.header("Bónus Imagenes")
st.info("Como desplegar imagenes")
pics = {
    "Cat": "https://cdn.pixabay.com/photo/2016/09/24/22/20/cat-1692702_960_720.jpg",
    "Puppy": "https://cdn.pixabay.com/photo/2019/03/15/19/19/puppy-4057786_960_720.jpg",
    "Sci-fi city": "https://storage.needpix.com/rsynced_images/science-fiction-2971848_1280.jpg"
}
pic = st.selectbox("Escoja una imagen", list(pics.keys()), 0)
st.image(pics[pic], use_column_width=True, caption=pics[pic])

st.markdown("## Hemos Finalizado!")
btn = st.button("Celebrar!")
if btn:
    st.balloons()