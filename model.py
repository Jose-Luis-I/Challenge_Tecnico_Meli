import pandas as pd
from sklearn.cluster import KMeans, AffinityPropagation, AgglomerativeClustering
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import silhouette_score
import plotly.express as px

df = pd.read_csv('clust.csv')


df.level_seller.unique()
df.drop('level_seller', axis=1, inplace=True)


enc = OneHotEncoder(handle_unknown='ignore')
enc.fit(df[['status_seller']])
enc_df = pd.DataFrame(enc.transform(df[['status_seller']]
                                    ).toarray(), columns=enc.get_feature_names_out())

df = pd.concat([df, enc_df], axis=1).drop('status_seller', axis=1)

dfp = df.drop(['id_seller', 'name_seller', 'ciudad', 'region'], axis=1)

# kmeans
k = KMeans(n_clusters=5)
k.fit(dfp)
k_df = k.predict(dfp)

df['k_means'] = k_df

metric_kmeans = silhouette_score(dfp, df.k_means)

# Affinity Propagation
a = AffinityPropagation(damping=0.75)
a.fit(dfp)
a_df = a.predict(dfp)

df['affinity'] = a_df

metric_affinity = silhouette_score(dfp, a_df)

# Agglomerative Clustering
ac = AgglomerativeClustering(n_clusters=5)
ac_df = ac.fit_predict(dfp)

df['agglomerative'] = ac_df

metric_agglo = silhouette_score(dfp, ac_df)

# ,'sold_quantity','antiguedad'
df.groupby('agglomerative')[['title']].describe()

# Plots
px.scatter(df, x='title', y='price_med', template='simple_white',
           color='k_means', title='KMeans Productos vs Precio').write_image('Imagenes/kMeans.png')

px.scatter(df, x='title', y='price_med', template='simple_white',
           color='affinity', title='Affinity Productos vs Precio').write_image('Imagenes/Affinity.png')

px.scatter(df, x='title', y='price_med', template='simple_white',
           color='agglomerative', title='Agglomerative Productos vs Precio').write_image('Imagenes/Agglomerative.png')

px.histogram(df, x='k_means', histnorm='percent',
             template='simple_white', title='Histogram kMeans', text_auto='.2f').write_image('Imagenes/Histograma_kMeans.png')
px.histogram(df, x='affinity', histnorm='percent',
             template='simple_white', title='Histogram Affinity', text_auto='.2f').write_image('Imagenes/Histograma_Affinity.png')
px.histogram(df, x='agglomerative', histnorm='percent',
             template='simple_white', title='Histogram Agglomerative', text_auto='.2f').write_image('Imagenes/Histograma_Agglomerative.png')

fig = px.box(df, x='agglomerative', y='title',
             title='Agglomerative # de Productos', template='simple_white')
fig.update_layout(yaxis_range=[0, 75])
fig.show()
fig.write_image('Imagenes/box.png')

fig = px.scatter(df, y='sold_quantity', x='precio_med',
                 title='Agglomerative Sold Quantity vs Precio', template='simple_white', color='agglomerative')
fig.show()
fig.write_image('Imagenes/scatter.png')

fig = px.scatter(df, y='neg_r', x='pos_r',
                 title='Agglomerative Sold Quantity vs Precio', template='simple_white', color='agglomerative')
fig.show()
fig.write_image('Imagenes/scatter_rating.png')
