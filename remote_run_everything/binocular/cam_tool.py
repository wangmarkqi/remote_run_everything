import os
import numpy as np

class CamTool:
    def calcR(self, phi, omega, kappa):
        a1 = np.cos(phi) * np.cos(kappa) - np.sin(phi) * np.sin(omega) * np.sin(kappa)
        a2 = -np.cos(phi) * np.sin(kappa) - np.sin(phi) * np.sin(omega) * np.cos(kappa)
        a3 = -np.sin(phi) * np.cos(omega)
        b1 = np.cos(omega) * np.sin(kappa)
        b2 = np.cos(omega) * np.cos(kappa)
        b3 = -np.sin(omega)
        c1 = np.sin(phi) * np.cos(kappa) + np.cos(phi) * np.sin(omega) * np.sin(kappa)
        c2 = -np.sin(phi) * np.sin(kappa) + np.cos(phi) * np.sin(omega) * np.cos(kappa)
        c3 = np.cos(phi) * np.cos(omega)
        arr = np.array([[a1, a2, a3], [b1, b2, b3], [c1, c2, c3]])
        return arr

    def intrisinc(self,path):
        path=os.path.abspath(path)
        return  np.loadtxt(path, delimiter=',')
    def cx_cy(self,path):
        ins=self.intrisinc(path)
        return ins[0, 2],ins[1, 2]
    def fx(self,path):
        ins=self.intrisinc(path)
        return ins[0,0]
