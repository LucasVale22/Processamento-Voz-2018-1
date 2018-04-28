#!/usr/bin/env python

from scipy.io import wavfile
import numpy as np
import sounddevice as sd
import os
import time


def speedx(sound_array, factor):
    """ Speeds up / slows down a sound, by some factor. """
    index = np.round(np.arange(0, len(sound_array), factor))
    index = index[index < len(sound_array)].astype(int)
    return sound_array[index]


def stretch(sound_array, factor, window_size=2**13, h=2**11):
    """ Stretches/shortens a sound, by some factor. """
    phase = np.zeros(window_size)
    hanning_window = np.hanning(window_size)
    result = np.zeros(int(len(sound_array) / factor + window_size))

    for i in np.arange(0, len(sound_array) - (window_size + h), h*factor):
        i = int(i)
        # Two potentially overlapping subarrays
        a1 = sound_array[i: i + window_size]
        a2 = sound_array[i + h: i + window_size + h]

        # The spectra of these arrays
        s1 = np.fft.fft(hanning_window * a1)
        s2 = np.fft.fft(hanning_window * a2)

        # Rephase all frequencies
        phase = (phase + np.angle(s2/s1)) % 2*np.pi

        a2_rephased = np.fft.ifft(np.abs(s2)*np.exp(1j*phase))
        i2 = int(i/factor)
        result[i2: i2 + window_size] += hanning_window*a2_rephased.real

    # normalize (16bit)
    result = ((2**(16-4)) * result/result.max())

    return result.astype('int16')


def pitchshift(sound_array, n, window_size=2**13, h=2**11):
    """ Changes the pitch of a sound by ``n`` semitones. """
    factor = 2**(1.0 * n / 12.0)
    stretched = stretch(sound_array, 1.0/factor, window_size, h)
    return speedx(stretched[window_size:], factor)

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
        
    fps, sound = wavfile.read('1.wav')

    teste_tones = (5,10,20,-5,-10,-20)
    print('Transponding teste sound file... ')
    transposed_sounds = [pitchshift(sound, n) for n in teste_tones]
    print('DONE')
    
    n = 5
    
    while True:
        print('1 : Stretch')
        print('2 : Speed')
        print('3 : Pitch Shift (strech + speed)')
        print('4 : Teste')
        print('n = '+str(n))
        print('5 : Mudar valor de n')
        print('\n')
        option = input('Selecione a Opcao: ')
        
        factor = 2**(1.0 * n / 12.0)
        
        if option == '1':
            print('Playing strechted sound')
            sound1 = stretch(sound,factor)
            sd.play(sound1,fps)
            print('Done')
            time.sleep(3)
            clear_terminal()           
        elif option == '2':
            print('Playing speeded sound')
            sound2 = speedx(sound,factor)
            sd.play(sound2,fps)
            print('Done')
            time.sleep(3)
            clear_terminal()   
        elif option == '3':
            print('Playing pitched sound')
            sound3 = pitchshift(sound,n)
            sd.play(sound3,fps)
            print('Done')
            time.sleep(3)
            clear_terminal()
        elif option == '4':
            print('Testing') 
            for i in range( len(transposed_sounds)):
                print('n = '+str(teste_tones[i]))
                sd.play(transposed_sounds[i], fps)
                time.sleep(3)
            print('Done')
            time.sleep(3)
            clear_terminal()
        elif option == '5':
            n = int( input('Novo valor de n: '))
            print('Novo n = '+str(n))
            time.sleep(3)
            clear_terminal()
        else:
            print('Opcao inexistente, escolha algo entre 1 e 5')
            time.sleep(3)
            clear_terminal()
    
    print('It worked!!')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Exiting')
