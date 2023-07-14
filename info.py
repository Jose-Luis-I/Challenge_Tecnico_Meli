from info_data import info_data
import pandas as pd

k = info_data('MCO')
categorias = k.categorias

cat_el = [1747, 1039, 1168, 1743, 1051, 1648, 1144, 1276, 5726, 1000]

info = []
for cat in cat_el:
    for el in range(0, 500, 50):
        ans = k.items(cat, el)['results']
        ans[0]['categoria'] = categorias[cat]
        info += ans


vars = ['id', 'title', 'condition',
        'listing_type_id',  'buying_mode',  'category_id',
        'domain_id',    'price',
        'original_price', 'sold_quantity', 'available_quantity',
        'accepts_mercadopago', 'tags',
        'garantia', 'id_seller', 'name_seller', 'fecha_registro', 'level_seller', 'status_seller', 'cancelados',
        'neg_r', 'completados', 'pos_r', 'nrl_r', 'ciudad', 'region', 'logistic_type', 'precio', 'precio_base', 'cant_ini', 'nombre_garantia', 'n_garantia', 'unid_garantia', 'categoria']


for n in range(len(info)):
    info[n]['garnatia'] = k.info_item(info[n]['id'], ['warranty'])
    info[n]['id_seller'] = info[n]['seller']['id']
    info[n]['name_seller'] = info[n]['seller']['nickname']
    info[n]['fecha_registro'] = info[n]['seller']['registration_date']
    info[n]['level_seller'] = info[n]['seller']['seller_reputation']['level_id']
    info[n]['status_seller'] = info[n]['seller']['seller_reputation']['power_seller_status']
    info[n]['cancelados'] = info[n]['seller']['seller_reputation']['transactions']['canceled']
    info[n]['completados'] = info[n]['seller']['seller_reputation']['transactions']['completed']
    info[n]['neg_r'] = info[n]['seller']['seller_reputation']['transactions']['ratings']['negative']
    info[n]['pos_r'] = info[n]['seller']['seller_reputation']['transactions']['ratings']['positive']
    info[n]['nrl_r'] = info[n]['seller']['seller_reputation']['transactions']['ratings']['neutral']
    info[n]['ciudad'] = info[n]['seller_address']['city']['name']
    info[n]['region'] = info[n]['seller_address']['state']['name']
    info[n]['logistic_type'] = info[n]['shipping']['logistic_type']
    info[n]['precio'] = k.info_item(info[n]['id'], ['price'])
    info[n]['precio_base'] = k.info_item(info[n]['id'], ['base_price'])
    info[n]['cant_ini'] = k.info_item(info[n]['id'], ['initial_quantity'])
    info[n]['nombre_garantia'] = k.info_item(
        info[n]['id'], ['sale_terms', 0, 'name'])
    info[n]['n_garantia'] = k.info_item(
        info[n]['id'], ['sale_terms', 0, 'value_struct', 'number'])
    info[n]['unid_garantia'] = k.info_item(
        info[n]['id'], ['sale_terms', 0, 'value_struct', 'unit'])


final = [{x: y for x, y in el.items() if x in vars} for el in info]
df = pd.DataFrame(final)
df.to_csv('dataf.csv', index=False)
