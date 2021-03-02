import numpy as np


class ConvolutionEncoder:
    def __init__(self, code_type: str):
        self.code_type = code_type
        self.flag = True
        if code_type == 'Intelsat 1/2':
            self.shiftReg = np.zeros(36, dtype=int)
        elif code_type == 'Intelsat 3/4':
            self.shiftReg = np.zeros(63, dtype=int)
            self.perf_sh = ''
        else:
            print('This class does not contain code rate -', self.code_type)
            print('Intelsat1/2 сoding rate selected')
            self.shiftReg = np.zeros(36, dtype=int)

    def reset(self):
        if self.code_type == 'Intelsat 1/2':
            self.shiftReg = np.zeros(36, dtype=int)
        elif self.code_type == 'Intelsat 3/4':
            self.shiftReg = np.zeros(63, dtype=int)
        else:
            self.shiftReg = np.zeros(36, dtype=int)

    def encode(self, data: str):
        if self.code_type == 'Intelsat 1/2':
            self.shiftReg = np.delete(self.shiftReg, self.shiftReg.size - 1)  # Удаление последнего элемента буфера
            self.shiftReg = np.hstack([int(data), self.shiftReg])  # Добавление символа в начало буфера
            data_sym = self.shiftReg[0]
            parity_sym = (self.shiftReg[0] ^ self.shiftReg[1] ^ self.shiftReg[2] ^ self.shiftReg[5]
                          ^ self.shiftReg[6] ^ self.shiftReg[9] ^ self.shiftReg[12] ^ self.shiftReg[13]
                          ^ self.shiftReg[17] ^ self.shiftReg[18] ^ self.shiftReg[19] ^ self.shiftReg[22]
                          ^ self.shiftReg[24] ^ self.shiftReg[26] ^ self.shiftReg[28] ^ self.shiftReg[29]
                          ^ self.shiftReg[32] ^ self.shiftReg[34] ^ self.shiftReg[35])
            return str(data_sym) + str(parity_sym)
        elif self.code_type == 'Intelsat 3/4':
            self.shiftReg = np.delete(self.shiftReg, self.shiftReg.size - 1)
            self.shiftReg = np.hstack([int(data), self.shiftReg])
            parity = (self.shiftReg[0] ^ self.shiftReg[1] ^ self.shiftReg[2]
                      ^ self.shiftReg[4] ^ self.shiftReg[5] ^ self.shiftReg[6]
                      ^ self.shiftReg[7] ^ self.shiftReg[9] ^ self.shiftReg[10]
                      ^ self.shiftReg[11] ^ self.shiftReg[12] ^ self.shiftReg[14]
                      ^ self.shiftReg[18] ^ self.shiftReg[22] ^ self.shiftReg[24]
                      ^ self.shiftReg[25] ^ self.shiftReg[27] ^ self.shiftReg[28]
                      ^ self.shiftReg[29] ^ self.shiftReg[32] ^ self.shiftReg[33]
                      ^ self.shiftReg[34] ^ self.shiftReg[35] ^ self.shiftReg[39]
                      ^ self.shiftReg[41] ^ self.shiftReg[45] ^ self.shiftReg[46]
                      ^ self.shiftReg[47] ^ self.shiftReg[48] ^ self.shiftReg[49]
                      ^ self.shiftReg[50] ^ self.shiftReg[52] ^ self.shiftReg[54]
                      ^ self.shiftReg[55] ^ self.shiftReg[56] ^ self.shiftReg[57]
                      ^ self.shiftReg[62])
            return str(self.shiftReg[0]) + str(parity)
        else:
            return 'Encoder err'

    # Накпливает 6 символов, делает выкалывание и возвращает 4.
    # Пока не накопил 6 символов возвращает None
    def perforate(self, data: str):
        perforate_mask = '111010'
        self.perf_sh += data
        if len(self.perf_sh) == len(perforate_mask):
            for i in range(len(perforate_mask)):
                if perforate_mask[i] == '0':
                    if i != len(perforate_mask)-1:
                        self.perf_sh = self.perf_sh[i:] + self.perf_sh[i+1:]
                    else:
                        self.perf_sh = self.perf_sh[:-1]
            return self.perf_sh
        else:
            return None

    def test_encode(self, data: str):
        self.shiftReg = np.delete(self.shiftReg, self.shiftReg.size - 1)
        self.shiftReg = np.hstack([int(data), self.shiftReg])
        xor_data = (self.shiftReg[0] ^ self.shiftReg[1] ^ self.shiftReg[2]
                    ^ self.shiftReg[4] ^ self.shiftReg[5] ^ self.shiftReg[6]
                    ^ self.shiftReg[7] ^ self.shiftReg[9] ^ self.shiftReg[10]
                    ^ self.shiftReg[11] ^ self.shiftReg[12] ^ self.shiftReg[14]
                    ^ self.shiftReg[18] ^ self.shiftReg[22] ^ self.shiftReg[24]
                    ^ self.shiftReg[25] ^ self.shiftReg[27] ^ self.shiftReg[28]
                    ^ self.shiftReg[29] ^ self.shiftReg[32] ^ self.shiftReg[33]
                    ^ self.shiftReg[34] ^ self.shiftReg[35] ^ self.shiftReg[39]
                    ^ self.shiftReg[41] ^ self.shiftReg[45] ^ self.shiftReg[46]
                    ^ self.shiftReg[47] ^ self.shiftReg[48] ^ self.shiftReg[49]
                    ^ self.shiftReg[50] ^ self.shiftReg[52] ^ self.shiftReg[54]
                    ^ self.shiftReg[55] ^ self.shiftReg[56] ^ self.shiftReg[57]
                    ^ self.shiftReg[62])
        return str(self.shiftReg[0]) + str(xor_data)

    def recover_encoder(self, shReg):
        if self.code_type == 'Intelsat 1/2':
            # В имени переменной 0 - признак верхнего ребра, 1 - признак нижнего ребра
            sh_r = np.delete(shReg, shReg.size - 1)
            shReg_0 = np.hstack([0, sh_r])
            shReg_1 = np.hstack([1, sh_r])
            data_sym_0 = shReg_0[0]
            data_sym_1 = shReg_1[0]
            parity_sym_0 = (shReg_0[0] ^ shReg_0[1] ^ shReg_0[2] ^ shReg_0[5]
                            ^ shReg_0[6] ^ shReg_0[9] ^ shReg_0[12] ^ shReg_0[13]
                            ^ shReg_0[17] ^ shReg_0[18] ^ shReg_0[19] ^ shReg_0[22]
                            ^ shReg_0[24] ^ shReg_0[26] ^ shReg_0[28] ^ shReg_0[29]
                            ^ shReg_0[32] ^ shReg_0[34] ^ shReg_0[35])
            parity_sym_1 = (shReg_1[0] ^ shReg_1[1] ^ shReg_1[2] ^ shReg_1[5]
                            ^ shReg_1[6] ^ shReg_1[9] ^ shReg_1[12] ^ shReg_1[13]
                            ^ shReg_1[17] ^ shReg_1[18] ^ shReg_1[19] ^ shReg_1[22]
                            ^ shReg_1[24] ^ shReg_1[26] ^ shReg_1[28] ^ shReg_1[29]
                            ^ shReg_1[32] ^ shReg_1[34] ^ shReg_1[35])
            encode_data_0 = str(data_sym_0) + str(parity_sym_0)
            encode_data_1 = str(data_sym_1) + str(parity_sym_1)
            return encode_data_0, encode_data_1
        elif self.code_type == 'Intelsat 3/4':
            sh_r = np.delete(shReg, shReg.size - 1)
            sh_r0 = np.hstack([0, sh_r])
            sh_r1 = np.hstack([1, sh_r])
            parity_0 = (sh_r0[0] ^ sh_r0[1] ^ sh_r0[2]
                        ^ sh_r0[4] ^ sh_r0[5] ^ sh_r0[6]
                        ^ sh_r0[7] ^ sh_r0[9] ^ sh_r0[10]
                        ^ sh_r0[11] ^ sh_r0[12] ^ sh_r0[14]
                        ^ sh_r0[18] ^ sh_r0[22] ^ sh_r0[24]
                        ^ sh_r0[25] ^ sh_r0[27] ^ sh_r0[28]
                        ^ sh_r0[29] ^ sh_r0[32] ^ sh_r0[33]
                        ^ sh_r0[34] ^ sh_r0[35] ^ sh_r0[39]
                        ^ sh_r0[41] ^ sh_r0[45] ^ sh_r0[46]
                        ^ sh_r0[47] ^ sh_r0[48] ^ sh_r0[49]
                        ^ sh_r0[50] ^ sh_r0[52] ^ sh_r0[54]
                        ^ sh_r0[55] ^ sh_r0[56] ^ sh_r0[57]
                        ^ sh_r0[62])
            parity_1 = (sh_r1[0] ^ sh_r1[1] ^ sh_r1[2]
                        ^ sh_r1[4] ^ sh_r1[5] ^ sh_r1[6]
                        ^ sh_r1[7] ^ sh_r1[9] ^ sh_r1[10]
                        ^ sh_r1[11] ^ sh_r1[12] ^ sh_r1[14]
                        ^ sh_r1[18] ^ sh_r1[22] ^ sh_r1[24]
                        ^ sh_r1[25] ^ sh_r1[27] ^ sh_r1[28]
                        ^ sh_r1[29] ^ sh_r1[32] ^ sh_r1[33]
                        ^ sh_r1[34] ^ sh_r1[35] ^ sh_r1[39]
                        ^ sh_r1[41] ^ sh_r1[45] ^ sh_r1[46]
                        ^ sh_r1[47] ^ sh_r1[48] ^ sh_r1[49]
                        ^ sh_r1[50] ^ sh_r1[52] ^ sh_r1[54]
                        ^ sh_r1[55] ^ sh_r1[56] ^ sh_r1[57]
                        ^ sh_r1[62])
            encode_data_0 = (str(sh_r0[1]) + str(sh_r0[2])
                             + str(sh_r0[0]) + str(parity_0))
            encode_data_1 = (str(sh_r1[1]) + str(sh_r1[2])
                             + str(sh_r1[0]) + str(parity_1))
            return encode_data_0, encode_data_1
        else:
            return 'Recover encoder err'


