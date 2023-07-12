import requests
import pandas as pd


class info_data():
    def __init__(self, pais: str = 'MLA'):
        # La clase se debe inicializar con el id del pais que se quiera obtener información
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
        # diccionario de id:categoria dentro del pais con el que se inicializa la clase
        self.categorias = {int(el['id'].replace(
            self.pais, '')): el['name'] for el in self.cats_1}
        pass

    def items(self, cat_id: int, offset: int):
        """Devuelve la respuesta directamente del api segun la categoria y el offset"""
        url = f'https://api.mercadolibre.com/sites/{self.pais}/search?category={self.pais+str(cat_id)}&offset={offset}'
        request = requests.get(url)
        items = request.json()
        return items

    def df_items(self, categoria_id: int, offset: int = 50):
        """Devuelve un dataframe que contiene los items de la categoria segun el id y el offset"""
        return pd.DataFrame(self.items(str(categoria_id), offset)['results'])

    def get_results(self, categoria_id: int, n: int):
        """Devuelve un dataframe con los items de la categoria contenidos en el rango de offset de 0 a n"""
        ran = range(0, n, 50)
        return pd.concat([self.df_items(categoria_id, el) for el in ran], ignore_index=True)
