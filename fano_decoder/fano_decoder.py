import numpy as np
from conv_encoder import ConvolutionEncoder
from func import SimpleEncoder

# FIXME: данные с выхода декодера всегда одинаковые?


class FanoDecoder:
    def __init__(self, delta_T: int, max_back_step: int, code_type: str):
        self.T = 0
        self.Vp = ''
        self.Vc = ''
        self.Vs = ''
        self.Mp = -10000
        self.Mc = 0
        self.Ms = 0
        self.A = False
        self.delta_T = delta_T
        # self.decode_data = ''
        self.st = 'Idle'
        self.cnt = 0
        self.max_back_step = max_back_step
        self.back_cnt = 0
        self.forward_cnt = 0
        self.code_type = code_type
        self.mask_cnt = 0
        # длина = кодовое огр-е + макс. кол-во шогов назад + символ который будет возвращаться
        # FIXME: может делать +1 и не имеет смысла и как декод-й символ надо забирать последний
        if code_type == 'Intelsat 1/2':
            self.coder_len = 36
            self.sym_rate = 2
            self.symShiftReg = np.zeros(self.coder_len + self.max_back_step + 1, dtype=int)
            self.fullShiftReg = np.zeros((self.coder_len + self.max_back_step) * 2, dtype=str)
            self.decodeShiftReg = np.zeros(self.max_back_step + 1, dtype=int)
            self.encoder = ConvolutionEncoder(code_type='Intelsat 1/2')
            self.perforate_mask = {0: '11', 1: '11', 2: '11'}
        elif code_type == 'Intelsat 3/4':
            self.coder_len = 63
            self.sym_rate = 4
            self.symShiftReg = np.zeros(self.coder_len + self.max_back_step + 1, dtype=int)
            self.fullShiftReg = np.zeros((self.coder_len + self.max_back_step) * 2, dtype=str)
            self.decodeShiftReg = np.zeros(self.max_back_step + 1, dtype=int)
            self.encoder = ConvolutionEncoder(code_type='Intelsat 3/4')
            self.perforate_mask = {0: '11', 1: '10', 2: '10'}
        else:
            print('Code type not found. Intelsat 1/2 selected')
            self.coder_len = 36
            self.sym_rate = 2
            self.symShiftReg = np.zeros(self.coder_len + self.max_back_step + 1, dtype=int)
            self.fullShiftReg = np.zeros((self.coder_len + self.max_back_step) * 2, dtype=str)
            self.decodeShiftReg = np.zeros(self.max_back_step + 1, dtype=int)
            self.encoder = ConvolutionEncoder(code_type='Intelsat 1/2')
            self.perforate_mask = {0: '11', 1: '11', 2: '11'}

    def decode(self, data: str, forward_step: int, perforate_mask: str):
        self.st = 'Idle'

        self.fullShiftReg = np.delete(self.fullShiftReg, self.fullShiftReg.size - 1)
        self.fullShiftReg = np.hstack([data, self.fullShiftReg])
        while True:
            if self.st == 'Idle':
                if self.forward_cnt > forward_step:
                    self.T = 0
                    self.Vp = ''
                    self.Vc = ''
                    self.Mc = 0
                    self.Mp = -10000
                    self.back_cnt = 0
                    self.forward_cnt = 0
                self.st = 'Metric_calc'

            elif self.st == 'Metric_calc':
                rib_0, rib_1 = self.encoder.recover_encoder(self.symShiftReg[0:self.coder_len])
                path, metric, decode_sym = self.__metric_calc(rib_0, rib_1, self.fullShiftReg[0 + self.back_cnt],
                                                              self.A)
                self.A = False
                self.Vs = self.Vc + path
                self.Ms = self.Mc + metric
                if self.Ms >= self.T:
                    self.symShiftReg = np.delete(self.symShiftReg, self.symShiftReg.size - 1)
                    self.symShiftReg = np.hstack([int(decode_sym), self.symShiftReg])
                    # self.decode_data += decode_sym
                    self.mask_cnt = self.mask_cnt + 1 if self.mask_cnt < 2 else 0
                    self.st = 'Forward_move'
                else:
                    self.st = 'Check_pointer'

            elif self.st == 'Check_pointer':
                if self.Mp >= self.T:
                    # self.decode_data = self.decode_data[:-1]
                    self.mask_cnt = self.mask_cnt - 1 if self.mask_cnt > 0 else 2
                    self.st = 'Backward_move'
                    if self.forward_cnt == 0:
                        print('alarm froward_cnt = 0')
                else:
                    self.T -= self.delta_T
                    self.st = 'Idle'

            elif self.st == 'Forward_move':
                self.Vp = self.Vc
                self.Vc = self.Vs
                self.Mp = self.Mc
                self.Mc = self.Ms
                self.forward_cnt += 1
                self.back_cnt = self.back_cnt - 1 if self.back_cnt >= 0 else self.back_cnt

                # if self.Mp < self.T + self.delta_T:
                #     if self.T <= self.Mc < self.T + self.delta_T:
                #         self.T += self.delta_T
                if self.Mp < self.T + self.delta_T:
                    self.T += self.delta_T

                self.st = 'Idle'
                if self.back_cnt < 0:
                    self.back_cnt = 0
                    break

            elif self.st == 'Backward_move':
                self.Vs = self.Vc
                self.Vc = self.Vp
                self.Vp = self.Vp[:-self.sym_rate]
                self.Ms = self.Mc
                self.Mc = self.Mp
                self.back_cnt += 1
                self.forward_cnt -= 1
                # Отступаем назад, удаляем текущий символ в конец добавляем 0 чтобы не изменять размер буфера
                self.symShiftReg = np.delete(self.symShiftReg, 0)
                self.symShiftReg = np.hstack([self.symShiftReg, 0])

                # Пересчет Mp
                if self.Vp != '':
                    rib_t0, rib_t1 = self.encoder.recover_encoder(self.symShiftReg[1:self.coder_len+1])
                    path_t, metric_t = self.__metric_calc(rib_t0, rib_t1, self.fullShiftReg[1 + self.back_cnt],
                                                          False)[0:2]
                    if path_t == self.Vc[-self.sym_rate:]:
                        self.Mp -= metric_t
                    else:
                        path_t, metric_t = self.__metric_calc(rib_t0, rib_t1, self.fullShiftReg[1 + self.back_cnt],
                                                              True)[0:2]
                        self.Mp -= metric_t
                        if path_t != self.Vc[-self.sym_rate:]:
                            print('Расчет Mp не верный')
                elif self.forward_cnt == 0:
                    self.Mp = -10000
                else:
                    self.Mp = 0

                rib_0, rib_1 = self.encoder.recover_encoder(self.symShiftReg[0:self.coder_len])
                p_bad = self.__metric_calc(rib_0, rib_1, self.fullShiftReg[0 + self.back_cnt], True)[0]
                if p_bad == self.Vs[-self.sym_rate:]:
                    self.st = 'Check_pointer'
                else:
                    self.A = True
                    self.st = 'Metric_calc'
            else:
                print('Ошибка состояния основной FSM')

        return str(self.symShiftReg[self.coder_len + self.max_back_step])

    def reset(self):
        self.T = 0
        self.Vp = ''
        self.Vc = ''
        self.Vs = ''
        self.Mp = -10000
        self.Mc = 0
        self.Ms = 0
        self.A = False
        self.st = 'Idle'
        self.cnt = 0
        self.back_cnt = 0
        self.forward_cnt = 0
        if self.code_type == 'Intelsat 1/2':
            self.symShiftReg = np.zeros(self.coder_len + self.max_back_step + 1, dtype=int)
            self.fullShiftReg = np.zeros((self.coder_len + self.max_back_step) * 2, dtype=str)
            self.decodeShiftReg = np.zeros(self.max_back_step + 1, dtype=int)
            self.encoder.reset()
        elif self.code_type == 'Intelsat 3/4':
            self.symShiftReg = np.zeros(self.coder_len + self.max_back_step + 1, dtype=int)
            self.fullShiftReg = np.zeros((self.coder_len + self.max_back_step) * 2, dtype=str)
            self.decodeShiftReg = np.zeros(self.max_back_step + 1, dtype=int)
            self.encoder.reset()
        else:
            self.symShiftReg = np.zeros(self.coder_len + self.max_back_step + 1, dtype=int)
            self.fullShiftReg = np.zeros((self.coder_len + self.max_back_step) * 2, dtype=str)
            self.decodeShiftReg = np.zeros(self.max_back_step + 1, dtype=int)
            self.encoder.reset()

    # Получает 4 символа, восстанавливает до 6, появляется два затертых символа
    @staticmethod
    def deperforator(data):
        data_copy = data
        perforate_mask = '111010'
        data_out = ''
        for i in range(len(perforate_mask)):
            if perforate_mask[i] == '1':
                data_out += data_copy[:1]
                data_copy = data_copy[1:]
            else:
                data_out += '0'
        return data_out

    def __metric_calc(self, rib_0: str, rib_1: str, data: str, A: bool):
        # A=True - возвращение худшей метрики, A=False - возвращение лучшей метрики
        hem_d0 = self.__hamming_distance12(data, rib_0)
        hem_d1 = self.__hamming_distance12(data, rib_1)
        if hem_d0 >= hem_d1:
            path = rib_1 if A else rib_0
            metric = hem_d1 if A else hem_d0
            decode_sym = '1' if A else '0'
        else:
            path = rib_0 if A else rib_1
            metric = hem_d0 if A else hem_d1
            decode_sym = '0' if A else '1'
        return path, metric, decode_sym

    def __hamming_distance12(self, str1, str2):
        a = 1 if self.code_type == 'Intelsat 1/2' else 2
        d = 0
        for n in range(len(str1)):
            if str1[n] != str2[n]:
                d += 1
        f = a if d == 0 else -(d * 4.5 // 1)
        return int(f)
