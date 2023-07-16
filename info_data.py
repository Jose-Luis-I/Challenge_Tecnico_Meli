import requests
import pandas as pd
from typing import List
from ndicts import NestedDict
import numpy as np


class info_data():
    def __init__(self, pais: str = 'MLA'):
        """La clase se debe inicializar con el id del pais que se quiera obtener información"""
        self.con = requests.get('https://api.mercadolibre.com/sites')
        self.con_ans = self.con.json()
        self.dic_con = {el['id']: el['name'] for el in self.con_ans}
        try:
            print(f'La clase se inicializó con el pais {self.dic_con[pais]}')
        except Exception as err:
            print(
                f'Id incorrecto, debe ser un de los siguientes: \n {self.dic_con}')
            raise err
        self.pais = pais
        self.url = f'https://api.mercadolibre.com/sites/{self.pais}/categories'
        self.cats = requests.get(self.url)
        self.cats_1 = self.cats.json()
        """diccionario de id:categoria dentro del pais con el que se inicializa la clase"""
        self.categorias = {int(el['id'].replace(
            self.pais, '')): el['name'] for el in self.cats_1}
        pass

    def items(self, cat_id: int, offset: int):
        """Devuelve la respuesta directamente json del api segun la categoria y el offset
        cat_id: id de la categoria
        offset: offset con el que se requiere iterar"""
        url = f'https://api.mercadolibre.com/sites/{self.pais}/search?category={self.pais+str(cat_id)}&offset={offset}'
        request = requests.get(url)
        items = request.json()
        return items

    def df_items(self, categoria_id: int, offset: int = 50):
        """Devuelve un dataframe que contiene los items de la categoria segun el id y el offset
         categoria_id: id de la categoria
        n: offset con el cual se requiere iterar"""
        return pd.DataFrame(self.items(str(categoria_id), offset)['results'])

    def get_results(self, categoria_id: int, n: int):
        """Devuelve un dataframe con los items de la categoria contenidos en el rango de offset de 0 a n
        categoria_id: id de la categoria
        n: offset hasta el cual se requiere iterar desde 0 (rango de 0 a n)"""
        ran = range(0, n, 50)
        return pd.concat([self.df_items(categoria_id, el) for el in ran], ignore_index=True)

    # def info_item(self, item_id: str, info: str = 'warranty'):
    #     """Retorna la información requerida del producto seleccionado"""
    #     url = f"https://api.mercadolibre.com/items/{item_id}#json"
    #     ans = requests.get(url).json()
    #     return ans[info]

    def info_item(self, item_id: str, path: List):
        """Retorna la información requerida de un item directamente desde la api
        item_id: id del item
        path: lista con path de la informacion requerida dentro del elemento json"""
        url = f"https://api.mercadolibre.com/items/{item_id}#json"
        try:
            ans = NestedDict(requests.get(url).json())
            for el in range(len(path)):
                ans = ans[path[el]]
        except:
            ans = np.NaN
        return ans

    def concat_info(self, cat_el: List, n: int):
        """Concatena la informacion segun categoria y numero de items requeridos por cada una
         cat_el: lista de categorias en enteros (sin prefijo del pais)
          n: numero de items requeridos por cada categoria en cat_el """
        info = []
        for cat in cat_el:
            for el in range(0, n, 50):
                ans = self.items(cat, el)['results']
                ans[0]['categoria'] = self.categorias[cat]
                info += ans
                print(str(el)+' '+str(cat))
        return info

    def man_inf(self, cat_el: List, n: int):
        info = self.concat_info(cat_el, n)
        for n in range(len(info)):
            info[n]['garnatia'] = self.info_item(info[n]['id'], ['warranty'])
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
            info[n]['precio'] = self.info_item(info[n]['id'], ['price'])
            info[n]['precio_base'] = self.info_item(
                info[n]['id'], ['base_price'])
            info[n]['cant_ini'] = self.info_item(
                info[n]['id'], ['initial_quantity'])
            info[n]['nombre_garantia'] = self.info_item(
                info[n]['id'], ['sale_terms', 0, 'name'])
            info[n]['n_garantia'] = self.info_item(
                info[n]['id'], ['sale_terms', 0, 'value_struct', 'number'])
            info[n]['unid_garantia'] = self.info_item(
                info[n]['id'], ['sale_terms', 0, 'value_struct', 'unit'])
            if n % 250 == 0:
                print(n)
        return info
