from func import PrsGenerate, BerTester, modulator, hamming_distance, awgn_generate, sigma_calc
from demodulator import Demodulator
from matplotlib import pyplot as plt
import numpy as np


def main():
    mod_type = 'QPSK'
    SNR = 1
    max_SNR = 15
    sym_num = 10000  # Символов в одной генерации ПСП
    snr_step = 1
    num_iter = int(max_SNR / snr_step)  # Количество генераций ПСП
    prsGen = PrsGenerate(prs_type='Default')
    demode = Demodulator(psk_type=mod_type)
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
            tester.reset()

            # Генерация ПСП
            for j in range(sym_num):
                prs_data += prsGen.generate()
            # Модулирование -> + абгш -> демодулирование
            noise_sigma = sigma_calc(SNR, 0.5, mod_type)
            for j in range(len(prs_data) // 2):
                I, Q = modulator(prs_data[2*j:2*j+2])
                x, y = awgn_generate()
                noisy_I = I + x * noise_sigma
                noisy_Q = Q + y * noise_sigma
                demode_buf += demode.hard_decision(noisy_I, noisy_Q)
            # ber tester
            for j in range(len(demode_buf)):
                bit, err = tester.check(demode_buf[j])
            print('Prs data =', prs_data)
            print('HD data  =', demode_buf)
            a = hamming_distance(prs_data, demode_buf)
            print('Err after decode =', a)
            print('Bit cntr =', bit)
            print('Err cntr =', err)
            if bit != 0:
                print('BER = ' + str(err / bit))
            plotBER[k] = err / bit
            plotSNR[k] = SNR
        print('SNR =', SNR)
        SNR += snr_step
        k += 1


    # plot create
    plt.semilogy(plotSNR, plotBER)
    plt.xlabel('SNR(db)')
    plt.ylabel('BER')
    plt.grid()
    plt.xticks([i for i in range(0, max_SNR)])
    plt.show()


if __name__ == '__main__':
    main()