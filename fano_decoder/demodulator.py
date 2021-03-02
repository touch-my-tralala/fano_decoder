import numpy as np


class Demodulator:
    def __init__(self, psk_type: str):
        self.mod_type = psk_type
        if psk_type == 'BPSK':
            self.fname = 'ph/fm2.csv'
            self.phData = np.zeros((3, 3), dtype=float)
        elif psk_type == 'QPSK':
            self.fname = 'D:/EvstigneevD/py_Prj/fano_decoder/ph/fm4.csv'
            self.phData = np.zeros((5, 3), dtype=float)
        elif psk_type == '8PSK':
            self.fname = 'ph/fm8.csv'
            self.phData = np.zeros((9, 3), dtype=float)
        else:
            self.mod_type = 'QPSK'
            self.fname = 'ph/fm4.csv'
            self.phData = np.zeros((5, 3), dtype=float)
            print('Не верный тип модуляции демодулятора. Выбран QPSK')
        k = 0
        j = 0
        sym = ''
        with open(self.fname, 'r') as f:
            fdata = f.read()
            for i in range(len(fdata)):
                if fdata[i] == '\n':
                    self.phData[j][k] = float(sym)
                    sym = ''
                    j += 1
                    k = 0
                else:
                    if fdata[i] == ';':
                        self.phData[j][k] = float(sym)
                        sym = ''
                        k += 1
                    else:
                        sym += fdata[i]

    def hard_decision(self, I, Q):
        numerator = self.phData[0][1]
        denominator = self.phData[0][2]
        euclidMetric = np.zeros(2**int(self.phData[0][0]), dtype=float)
        # Вычисление Евклидовой метрики до каждой идеальной точки созвздия
        for j in range(1, 2**int(self.phData[0][0])+1):
            idI = self.phData[j][1] * numerator / denominator
            idQ = self.phData[j][2] * numerator / denominator
            euclidMetric[j-1] = np.sqrt((I - idI)**2 + (Q - idQ)**2)
        minMetric = euclidMetric.argmin()  # Индекс минимальной метрики
        if self.mod_type == 'QPSK':
            hd = '0' + str(bin(minMetric))[2:] if len(str(bin(minMetric))[2:]) < 2 else str(bin(minMetric))[2:]
        elif self.mod_type == '8PSK':
            if len(str(bin(minMetric))[-2:]) < 2:
                hd = '00' + str(bin(minMetric))[-2:]
            elif len(str(bin(minMetric))[-2:]) < 3:
                hd = '0' + str(bin(minMetric))[-2:]
            else:
                hd = str(bin(minMetric))[-2:]
        else:
            hd = str(bin(minMetric))[-2:]
        return hd


