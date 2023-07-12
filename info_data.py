import requests


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
        self.categorias = {el['id'].replace(
            self.pais, ''): el['name'] for el in self.cats_1}
        pass

    def items(self, cat_id: str, offset: int):
        url = f'https://api.mercadolibre.com/sites/{self.pais}/search?category={self.pais+cat_id}&offset={offset}'
        request = requests.get(url)
        items = request.json()
        return items
