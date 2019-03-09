import numpy as np


class Indicators():
    ''' Standard methods for calculating observables '''

    def sma(self, observable, window_size):
        try:
            window_size = int(window_size)
            data = self.memory[observable][-window_size:]
            val = np.mean(np.array(data))
            return val
        except IndexError as e:  # Window size exceeds current memory
            return np.nan

    def gradient(self, observable, window_size):
        ''' Returns slope as degrees '''
        try:
            window_size = int(window_size)
            data = self.memory[observable][-window_size:]
            slope_rad = np.arctan(data)[-1]
            slope_deg = np.rad2deg(slope_rad)
            return slope_deg
        except IndexError as e:  # Window size exceeds current memory
            pass
        except ValueError as e:
            pass
        except KeyError as e:
            print('Warning: observable does not exist')
            pass
        return np.nan

    def upcross(self, a, b):
        ''' Signal if a surpasses b '''
        pass

    def downcross(self, a, b):
        ''' Signal if a falls below b '''
        pass
