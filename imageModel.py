import numpy as np
import cv2 as cv

class ImageModel():
    def __init__(self,path):
        self.path = path
        self.image = cv.imread(self.path,flags=cv.IMREAD_GRAYSCALE).T
        self.size = self.image.shape

        self.dft = np.fft.fft2(self.image)
        self.dft_shift = np.fft.fftshift(self.dft)

        self.magnitude = np.abs(self.dft)
        self.magnitude_shift = 20*np.log(np.abs(self.dft_shift))

        self.phase = np.angle(self.dft)
        self.phase_shift = np.angle(self.dft_shift)

        self.real = np.real(self.dft)
        self.real_shift = 20*np.log(np.real(self.dft_shift))

        self.imaginary = np.imag(self.dft)
        self.imaginary_shift = np.imag(self.dft_shift)

        self.uniform_magnitude = np.ones(self.magnitude.shape)
        self.uniform_phase = np.zeros(self.phase.shape)

    def mix(self, image2:'Image', mag_real_ratio, ph_img_ratio, mode):
        w1 = mag_real_ratio
        w2 = ph_img_ratio        
        mixInverse = None

        if mode == "magnitudeandphase" or mode == "phaseandmagnitude":
            print("Mixing Magnitude and Phase")
            
            M1 = self.magnitude
            M2 = image2.magnitude

            P1 = self.phase
            P2 = image2.phase

            magnitudeMix = w1*M1 + (1-w1)*M2
            phaseMix = (1-w2)*P1 + w2*P2

            combined = np.multiply(magnitudeMix, np.exp(1j * phaseMix))
            mixInverse = np.real(np.fft.ifft2(combined))
            
        elif mode == "realandimaginary" or mode == "imaginaryandreal":
            print("Mixing Real and Imaginary")

            R1 = self.real
            R2 = image2.real

            I1 = self.imaginary
            I2 = image2.imaginary

            realMix = w1*R1 + (1-w1)*R2
            imaginaryMix = (1-w2)*I1 + w2*I2

            combined = realMix + imaginaryMix * 1j
            mixInverse = np.real(np.fft.ifft2(combined))
            
        #must set sliders to zeros 
        elif mode == "magnitudeanduniform phase":
            print("Mixing Magnitude and Uniform Phase")

            M1 = self.magnitude
            M2 = image2.magnitude

            P1 = self.phase
            P2 = image2.uniform_phase
            
            w2=0
            magnitudeMix = w1*M1 + (1-w1)*M2
            phaseMix = (1-w2)*P1 + w2*P2

            combined = np.multiply(magnitudeMix, np.exp(1j * phaseMix))
            mixInverse = np.real(np.fft.ifft2(combined))

        elif mode == "uniform phaseandmagnitude":
            print("Mixing Uniform Phase and Magnitude")

            M1 = self.magnitude
            M2 = image2.magnitude

            P1 = self.uniform_phase
            P2 = image2.phase
            
            w1=0
            magnitudeMix = w1*M1 + (1-w1)*M2
            phaseMix = (1-w2)*P1 + w2*P2

            combined = np.multiply(magnitudeMix, np.exp(1j * phaseMix))
            mixInverse = np.real(np.fft.ifft2(combined))

        elif mode == "uniform magnitudeandphase":
            print("Mixing Uniform Magnitude and Phase")
            M1 = self.uniform_magnitude
            M2 = image2.magnitude

            P1 = self.phase
            P2 = image2.phase
            
            w1=0
            magnitudeMix = w1*M1 + (1-w1)*M2
            phaseMix = (1-w2)*P1 + w2*P2

            combined = np.multiply(magnitudeMix, np.exp(1j * phaseMix))
            mixInverse = np.real(np.fft.ifft2(combined))

        elif mode == "phaseanduniform magnitude":
            print("Mixing Phase and Uniform Magnitude")
            M1 = self.magnitude
            M2 = image2.uniform_magnitude

            P1 = self.phase
            P2 = image2.phase
            
            w2=0
            magnitudeMix = w1*M1 + (1-w1)*M2
            phaseMix = (1-w2)*P1 + w2*P2

            combined = np.multiply(magnitudeMix, np.exp(1j * phaseMix))
            mixInverse = np.real(np.fft.ifft2(combined))

        return abs(mixInverse)