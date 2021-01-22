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


    def decode(self, data: str):
        cnt = 0  # счетчик исследованных ребер
        branch = True  # Ветка по которой идем по кодовому древу. True -верхняя, False - нижняя
        hemming_d1 = 0
        hemming_d2 = 0
        i = 0
        while i < len(len(data))/2:
            if cnt < 2:  # Существуют ли ранее не исследованные ветви?
                if branch:  # Выбор по какой ветке идем верхней или нижней

                else:
            else:



    def __hamming_distance(str1, str2):
        d = 0
        for n in range(len(str1)):
            if str1[n] != str2[n]:
                d += 1
        return d