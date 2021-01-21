class FanoDecoder:
    def __init__(self, d0, d1, d2):
        self.T = 0  # Порог декодирования
        self.Vp = 0  # Прошла точка на деерве кода
        self.Mp = 0  # Прошлая метрика пути
        self.Vc = 0  # Текущая
        self.Mc = 0
        self.Vs = 0  # Следующая
        self.Ms = 0
        self.d0 = d0  # Метрика ребра при совпадени расстояний Хэмминга
        self.d1 = d1  # Метрика ребра при одном ошибочном бите
        self.d2 = d2  # Метрика ребра при двух ошибочных битах
        self.st = 0b00

    def decode(self, data):
        i = 0
        while i < len(bin(data)):
            if self.st == 0b00:
                
            elif self.st == 0b01:

            elif self.st == 0b10:

            else: