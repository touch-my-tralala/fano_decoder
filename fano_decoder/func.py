import numpy as np
import random
from math import log10, fabs


# Генератор различных ПСП
class PrsGenerate:
    def __init__(self, prs_type='Default'):
        self.shiftReg = 1
        self.prs_type = prs_type

    def generate(self):
        if self.prs_type == 'Fibonacci':  # последовательность Фибоначчи
            self.shiftReg = ((((self.shiftReg >> 31) ^ (self.shiftReg >> 30) ^ (self.shiftReg >> 29) ^ (
                    self.shiftReg >> 27)
                               ^ (self.shiftReg >> 25) ^ self.shiftReg) & 0x1) << 31) | (self.shiftReg >> 1)
            return str(self.shiftReg & 0x1)
        elif self.prs_type == 'Galois':  # последовательность Галуа
            if self.shiftReg & 1:
                self.shiftReg = ((self.shiftReg ^ 0xEA000001) >> 1) | 0x80000000
                return '1'
            else:
                self.shiftReg >>= 1
                return '0'
        else:  # 0 и 14 биты ксорятся
            prs = ((self.shiftReg >> 0) & 1) ^ ((self.shiftReg >> 14) & 1)
            self.shiftReg <<= 1
            self.shiftReg |= prs
            # self.shiftReg = (((self.shiftReg >> 13) ^ (self.shiftReg >> 12)) | (self.shiftReg << 1)) & 0x7FFF
            return str(prs)

    def reset(self):
        self.shiftReg = 1


class BerTester:
    def __init__(self, prs_type='Default'):
        self.shiftReg = 1
        self.prs_type = prs_type
        self.syncOk = False
        self.syncCnt = 0
        self.globalErrCnt = 0
        self.globalBitCnt = 0

    # Проверка совпадения ПСП
    def check(self, hd):
        errCnt = 0
        for i in range(len(hd)):
            if self.syncOk:
                prs = ((self.shiftReg >> 0) & 1) ^ ((self.shiftReg >> 14) & 1)
                self.shiftReg <<= 1
                self.shiftReg |= prs
                errCnt += prs ^ int(hd[i])
                self.syncCnt = self.syncCnt - 1 if prs == int(hd[i]) else self.syncCnt + 1
                if self.syncCnt == 10:
                    self.syncOk = False
                    self.syncCnt = 0
                self.syncCnt = 0 if self.syncCnt < 0 else self.syncCnt
            else:
                prs = ((self.shiftReg >> 0) & 1) ^ ((self.shiftReg >> 14) & 1)
                self.shiftReg <<= 1
                self.shiftReg |= int(hd[i])
                self.syncCnt = self.syncCnt + 1 if prs == int(hd[i]) else 0
                if self.syncCnt == 10:
                    self.syncOk = True
                    self.syncCnt = 0
        self.globalBitCnt = self.globalBitCnt + len(hd) if self.syncOk else self.globalBitCnt
        self.globalErrCnt += errCnt
        return self.globalBitCnt, self.globalErrCnt

    # Сброс статистики
    def reset(self):
        self.globalErrCnt = 0
        self.globalBitCnt = 0
        self.syncCnt = 0
        self.syncOk = False
        self.shiftReg = 1


# Декоратор для инициализации модулятора/демодулятора в зависимости от типа модуляции
def init_psk(mod_type: str):
    fm2_numerator = 180.0
    fm2_denominator = 511.0
    fm2_I = [1.0, -1.0]
    fm2_Q = [0.0, 0.0]
    fm4_numerator = 180.0
    fm4_denominator = 511.0
    fm4_I = [1.0, -1.0, 1.0, -1.0]
    fm4_Q = [1.0, 1.0, -1.0, -1.0]
    fm8_numerator = 1024.0
    fm8_denominator = 2048.0
    fm8_I = [0.924, 0.383, -0.924, -0.383, 0.924, 0.383, -0.924, -0.383]
    fm8_Q = [0.383, 0.924, 0.383, 0.924, -0.383, -0.924, -0.383, -0.924]

    def decorate(func):
        if mod_type == 'BPSK':
            idealPointsI = np.zeros(2, dtype=float)
            idealPointsQ = np.zeros(2, dtype=float)
            for i in range(2):
                idealPointsI[i] = fm2_I[i] * fm2_numerator / fm2_denominator
                idealPointsQ[i] = fm2_Q[i] * fm2_numerator / fm2_denominator
            setattr(func, 'idealPointsI', idealPointsI)
            setattr(func, 'idealPointsQ', idealPointsQ)
            setattr(func, 'mod_type', 'BPSK')
        elif mod_type == 'QPSK':
            idealPointsI = np.zeros(4, dtype=float)
            idealPointsQ = np.zeros(4, dtype=float)
            for i in range(4):
                idealPointsI[i] = fm4_I[i] * fm4_numerator / fm4_denominator
                idealPointsQ[i] = fm4_Q[i] * fm4_numerator / fm4_denominator
            setattr(func, 'idealPointsI', idealPointsI)
            setattr(func, 'idealPointsQ', idealPointsQ)
            setattr(func, 'mod_type', 'QPSK')
        elif mod_type == '8PSK':
            idealPointsI = np.zeros(8, dtype=float)
            idealPointsQ = np.zeros(8, dtype=float)
            for i in range(8):
                idealPointsI[i] = fm8_I[i] * fm8_numerator / fm8_denominator
                idealPointsQ[i] = fm8_Q[i] * fm8_numerator / fm8_denominator
            setattr(func, 'idealPointsI', idealPointsI)
            setattr(func, 'idealPointsQ', idealPointsQ)
            setattr(func, 'mod_type', '8PSK')
        else:
            idealPointsI = np.zeros(4, dtype=float)
            idealPointsQ = np.zeros(4, dtype=float)
            for i in range(4):
                idealPointsI[i] = fm4_I[i] * fm4_numerator / fm4_denominator
                idealPointsQ[i] = fm4_Q[i] * fm4_numerator / fm4_denominator
            setattr(func, 'idealPointsI', idealPointsI)
            setattr(func, 'idealPointsQ', idealPointsQ)
            setattr(func, 'mod_type', 'QPSK')
            print('По умолчанию установления модуляция QPSK')
        return func

    return decorate


# Формироватеь созвездия
@init_psk(mod_type='QPSK')
def modulator(data: str):
    if modulator.mod_type == 'BPSK':
        I = modulator.idealPointsI[0] if data == '1' else modulator.idealPointsI[1]
        Q = modulator.idealPointsQ[0] if data == '1' else modulator.idealPointsQ[1]
    elif modulator.mod_type == 'QPSK':
        if data == '00':
            I = modulator.idealPointsI[0]
            Q = modulator.idealPointsQ[0]
        elif data == '01':
            I = modulator.idealPointsI[1]
            Q = modulator.idealPointsQ[1]
        elif data == '10':
            I = modulator.idealPointsI[2]
            Q = modulator.idealPointsQ[2]
        else:
            I = modulator.idealPointsI[3]
            Q = modulator.idealPointsQ[3]
    elif modulator.mod_type == '8PSK':
        if data == '000':
            I = modulator.idealPointsI[0]
            Q = modulator.idealPointsQ[0]
        elif data == '001':
            I = modulator.idealPointsI[1]
            Q = modulator.idealPointsQ[1]
        elif data == '010':
            I = modulator.idealPointsI[2]
            Q = modulator.idealPointsQ[2]
        elif data == '011':
            I = modulator.idealPointsI[3]
            Q = modulator.idealPointsQ[3]
        elif data == '100':
            I = modulator.idealPointsI[4]
            Q = modulator.idealPointsQ[4]
        elif data == '101':
            I = modulator.idealPointsI[5]
            Q = modulator.idealPointsQ[5]
        elif data == '110':
            I = modulator.idealPointsI[6]
            Q = modulator.idealPointsQ[6]
        else:
            I = modulator.idealPointsI[7]
            Q = modulator.idealPointsQ[7]
    else:
        print('Неверный тип модуляции')
        I = 0
        Q = 0
    return I, Q


def hamming_distance(str1, str2):
    d = 0
    num = []
    if len(str1) != len(str2):
        print('length string not equal')
        return 0
    for n in range(len(str1)):
        if str1[n] != str2[n]:
            num.append(n)
            d += 1
    print('Num err =', num)
    return d


class SimpleEncoder:
    def __init__(self):
        self.shreg = np.zeros(2, dtype=int)

    def encoder12(self, data: str):
        self.shreg = np.delete(self.shreg, self.shreg.size - 1)
        self.shreg = np.hstack([int(data), self.shreg])
        d_sym = self.shreg[0]
        p_sym = self.shreg[0] ^ self.shreg[1]
        return str(d_sym) + str(p_sym)

    @staticmethod
    def recover_encoder12(shift_r):
        sh_r = np.delete(shift_r, shift_r.size - 1)
        shiftR_0 = np.hstack([0, sh_r])
        shiftR_1 = np.hstack([1, sh_r])
        d_sym_0 = shiftR_0[0]
        d_sym_1 = shiftR_1[0]
        p_sym_0 = shiftR_0[0] ^ shiftR_0[1]
        p_sym_1 = shiftR_1[0] ^ shiftR_1[1]
        encode_data_0 = str(d_sym_0) + str(p_sym_0)
        encode_data_1 = str(d_sym_1) + str(p_sym_1)
        return encode_data_0, encode_data_1


def awgn_generate():
    while True:
        u1 = 2.0 * random.random() - 1.0
        u2 = 2.0 * random.random() - 1.0
        s = u1 ** 2 + u2 ** 2
        if s >= 1.0 or fabs(s) < 1e-10:
            continue
        else:
            break
    w = np.sqrt((-2.0 * np.log(s)) / s)

    return (u1 * w), (u2 * w)


def sigma_calc(snr, symbol_rate, mod_type: str):
    mean_power = {'BPSK': 0.12408, 'QPSK': 0.24816, '8PSK': 0.2501, '8QAM': 0.2750}
    modulation = mod_type
    if modulation not in mean_power:
        print('Modulation type not found. QPSK selected.')
        modulation = 'QPSK'
    # noise_sigma = mean_power[modulation] * np.sqrt(pow(10, -snr / 10) / symbol_rate)
    noise_sigma = 0.2501 * np.sqrt(pow(10, -snr / 10) / symbol_rate)

    if modulation == 'BPSK':
        return noise_sigma / 0.707
    else:
        return noise_sigma
