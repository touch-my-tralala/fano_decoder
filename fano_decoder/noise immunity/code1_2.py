from func import PrsGenerate, BerTester, modulator, hamming_distance, awgn_generate, sigma_calc
from demodulator import Demodulator
from fano_decoder import FanoDecoder
from conv_encoder import ConvolutionEncoder
from matplotlib import pyplot as plt
import numpy as np


def code1_2():
    mod_type = 'QPSK'
    code_type = 'Intelsat 3/4'
    mod_order = {'BPSK': 1, 'QPSK': 2, '8PSK': 3}
    sym_rate = {'Intelsat 1/2': 2, 'Intelsat 3/4': 4, 'Intelsat 7/8': 8}
    SNR = 6
    max_SNR = 15
    SNR_step = 1
    sym_num = 20000  # Символов в одной генерации ПСП
    max_back_step = 180  # Макс. количество шагов назад для декодера
    cur_back_step = 180  # Текущее количество шагов назад для декодера
    encoder_len = 63  # Длина регистра кодера: 1/2 = 36, 3/4 = 63
    del_sym = encoder_len + max_back_step  # Количесво 0, которое надо удалить вначале декод-й последовательно
    num_iter = int((max_SNR - SNR) / SNR_step)  # Количество генераций ПСП
    prsGen = PrsGenerate(prs_type='Default')
    demode = Demodulator(psk_type=mod_type)
    encoder = ConvolutionEncoder(code_type=code_type)
    decoder = FanoDecoder(delta_T=5, max_back_step=max_back_step, code_type=code_type)
    tester = BerTester(prs_type='Default')
    plotBER = np.zeros(num_iter, dtype=np.float)
    plotSNR = np.zeros(num_iter, dtype=np.float)

    k = 0
    while True:

        if k >= num_iter:
            break
        elif k < num_iter:
            demode_buf = ''
            prs_data = ''
            encode_seq = ''
            decode_seq = ''
            tester.reset()
            encoder.reset()
            decoder.reset()
            prsGen.reset()

            # Генерация ПСП -> кодирование ->
            for j in range(sym_num):
                prs_sym = prsGen.generate()
                prs_data += prs_sym
                encode_word = encoder.encode(prs_sym)
                encode_seq += encode_word

            # -> Модулирование -> + абгш -> демодулирование ->
            noise_sigma = sigma_calc(SNR, 0.5, mod_type)
            for j in range(len(encode_seq) // mod_order[mod_type]):
                I, Q = modulator(encode_seq[mod_order[mod_type] * j:mod_order[mod_type] * j + mod_order[mod_type]])
                x, y = awgn_generate()
                noisy_I = I + x * noise_sigma
                noisy_Q = Q + y * noise_sigma
                demode_buf += demode.hard_decision(noisy_I, noisy_Q)

            # -> Декодирование
            for j in range(len(demode_buf) // sym_rate[code_type]):
                decode_seq += decoder.decode(demode_buf[sym_rate[code_type] * j:sym_rate[code_type] * j + sym_rate[code_type]], cur_back_step)

            # ber tester
            decode_seq = decode_seq[del_sym:-200]
            for j in range(len(decode_seq)):
                bit, err = tester.check(decode_seq[j])

            noise_sigma = sigma_calc(SNR, 0.5, mod_type)
            for j in range(sym_num):
                # Генерация ПСП -> кодирование ->
                prs_sym = prsGen.generate()
                prs_data += prs_sym
                encode_word = encoder.encode(prs_sym)
                encode_seq += encode_word

                # -> Модулирование -> + абгш -> демодулирование ->
                I, Q = modulator(encode_word)
                x, y = awgn_generate()
                noisy_I = I + x * noise_sigma
                noisy_Q = Q + y * noise_sigma
                demode_sym = demode.hard_decision(noisy_I, noisy_Q)
                demode_buf += demode_sym

                # -> Декодирование
                decode_seq += decoder.decode(demode_sym, cur_back_step)

            print('Encode seq =', encode_seq)
            print('Demode seq =', demode_buf)
            a = hamming_distance(encode_seq, demode_buf)
            print('Err after demode =', a)

            print('Prs data   =', prs_data[:-del_sym])
            print('Decode seq =', decode_seq)
            a = hamming_distance(prs_data[:-(del_sym+200)], decode_seq)
            print('Err after decode =', a)
            print('Bit cntr =', bit)
            print('Err cntr =', err)

            # b = ''
            # for j in range(len(encode_seq)):
            #     if encode_seq[j] != demode_buf[j]:
            #         b += str(j) + ', '
            # print(b)
            if bit != 0:
                print('BER = ' + str(err / bit))
            plotBER[k] = err / bit
            plotSNR[k] = SNR
        print('SNR =', SNR)
        SNR += SNR_step
        k += 1

    # plot create
    plt.semilogy(plotSNR, plotBER)
    plt.xlabel('SNR(db)')
    plt.ylabel('BER')
    plt.grid()
    plt.xticks([i for i in range(0, max_SNR)])
    plt.show()


if __name__ == '__main__':
    code1_2()
