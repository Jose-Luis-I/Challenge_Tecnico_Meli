from info_data import info_data
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import OneHotEncoder
import pandas as pd
import numpy as np

k = info_data('MCO')
categorias = k.categorias

cat_el = [1747, 1039, 1168, 1743, 1051, 1648, 1144, 1276, 5726, 1000]

vars = ['id', 'title', 'condition',
        'listing_type_id',  'buying_mode',  'category_id',
        'domain_id',    'price',
        'original_price', 'sold_quantity', 'available_quantity',
        'accepts_mercadopago', 'tags',
        'garantia', 'id_seller', 'name_seller', 'fecha_registro', 'level_seller', 'status_seller', 'cancelados',
        'neg_r', 'completados', 'pos_r', 'nrl_r', 'ciudad', 'region', 'logistic_type', 'precio', 'precio_base', 'cant_ini', 'nombre_garantia', 'n_garantia', 'unid_garantia', 'categoria']

info = k.man_inf(cat_el, 50)


final = [{x: y for x, y in el.items() if x in vars} for el in info]
df = pd.DataFrame(final)


df['now'] = pd.Timestamp.now().date()

df['antiguedad'] = (pd.to_datetime(df.now, utc=True) -
                    pd.to_datetime(df.fecha_registro, utc=True)).dt.days
df.drop(['now', 'fecha_registro'], axis=1, inplace=True)

item_vars = ['id', 'title', 'condition', 'listing_type_id', 'buying_mode',
             'category_id', 'domain_id', 'price', 'original_price', 'sold_quantity',
             'available_quantity', 'accepts_mercadopago',
             'tags', 'logistic_type', 'nombre_garantia', 'n_garantia', 'precio', 'precio_base', 'cant_ini', 'unid_garantia', 'categoria']  # NOTE: Agregar unid_garantia,categoria

seller_vars = [el for el in df.columns if el not in item_vars]


cat_vars = [el for el in df.columns if df[el].dtype == 'O']
num_vars = [el for el in df.columns if el not in cat_vars]
ohe_vars = ['condition', 'listing_type_id', 'buying_mode',
            'domain_id', 'logistic_type', 'nombre_garantia']
df.n_garantia.fillna(df.n_garantia.median(), inplace=True)
df.original_price.fillna(df.original_price.median(), inplace=True)
df.logistic_type.fillna(df.logistic_type.mode().values[0], inplace=True)
df.nombre_garantia.fillna(df.nombre_garantia.mode().values[0], inplace=True)

enc_i = OneHotEncoder(handle_unknown='ignore')
enc_i.fit(df[ohe_vars])
ohe_i_df = pd.DataFrame(enc_i.transform(
    df[ohe_vars]).toarray(), columns=enc_i.get_feature_names_out())

df = pd.concat([df, ohe_i_df], axis=1)


df['n_garantia'] = np.where(df.unid_garantia == 'meses', df.n_garantia*30,
                            np.where(df.unid_garantia == 'años', df.n_garantia*365, df.n_garantia))
dt = df[seller_vars].drop_duplicates().dropna()

# Medianas item_vars
med_df = df.groupby('id_seller')[['price', 'original_price',
                                  'available_quantity', 'n_garantia', 'precio', 'precio_base', 'sold_quantity', 'n_garantia']].median()
med_df.columns = [el+'_med' for el in med_df.columns]

dt = dt.merge(med_df, how='left', left_on='id_seller', right_index=True)

# Maximos item_vars
max_df = df.groupby('id_seller')[['price', 'original_price',
                                  'available_quantity', 'n_garantia', 'precio', 'precio_base', 'sold_quantity', 'n_garantia']].max()
max_df.columns = [el+'_max' for el in max_df.columns]

dt = dt.merge(max_df, how='left', left_on='id_seller', right_index=True)

# Minimos item_vars
min_df = df.groupby('id_seller')[['price', 'original_price',
                                  'available_quantity', 'n_garantia', 'precio', 'precio_base', 'sold_quantity', 'n_garantia']].min()
min_df.columns = [el+'_min' for el in min_df.columns]

dt = dt.merge(min_df, how='left', left_on='id_seller', right_index=True)

# Cant. Vendidad
cant_df = df.groupby('id_seller')['sold_quantity'].sum()
dt = dt.merge(cant_df, how='left', left_on='id_seller', right_index=True)


# Cant. Prod
prod_df = df.groupby('id_seller').title.nunique()
dt = dt.merge(prod_df, how='left', left_on='id_seller', right_index=True)


# Ohe Vars Cant.
ohe_group = df.groupby('id_seller')[enc_i.get_feature_names_out()].sum()
dt = dt.merge(ohe_group, how='left', left_on='id_seller', right_index=True)


dt.drop('level_seller', axis=1, inplace=True)


enc = OneHotEncoder(handle_unknown='ignore')
enc.fit(dt[['status_seller']])
enc_df = pd.DataFrame(enc.transform(dt[['status_seller']]
                                    ).toarray(), columns=enc.get_feature_names_out())

dt = pd.concat([dt.reset_index(drop=True), enc_df],
               axis=1).drop('status_seller', axis=1)

dtp = dt.drop(['id_seller', 'name_seller', 'ciudad', 'region'], axis=1)

ac = AgglomerativeClustering(n_clusters=5)
ac_df = ac.fit_predict(dtp)

dt['agglomerative'] = ac_df

dt.to_csv('classified.csv', index=False)
