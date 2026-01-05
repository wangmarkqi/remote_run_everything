"""
后方交会代码
作者：Dash
version:0.1
without any optimization
"""
import numpy as np


class BackTool(object):
    def __init__(self, f, u, v):
        self.f = f
        self.u = u
        self.v = v
        self.max_step = 1000000

    def init_param(self, X, Y, Z, scale):
        n = len(X)
        # initial line paras
        Z0 = scale * self.f + (1 / n) * np.sum(Z)
        X0 = (1 / n) * np.sum(X)
        Y0 = (1 / n) * np.sum(Y)
        return X0, Y0, Z0

    def genL(self, X, Y, Z, phi, omega, kappa, X0, Y0, Z0):
        R = CamTool().calcR(phi, omega, kappa)
        a1, a2, a3, b1, b2, b3, c1, c2, c3 = [i for l in R.tolist() for i in l]
        L = []
        for j in range(len(self.u)):
            numerator_x = self.f * (a1 * (X[j] - X0) + b1 * (Y[j] - Y0) + c1 * (Z[j] - Z0))
            numerator_y = self.f * (a2 * (X[j] - X0) + b2 * (Y[j] - Y0) + c2 * (Z[j] - Z0))
            denomanator = (a3 * (X[j] - X0) + b3 * (Y[j] - Y0) + c3 * (Z[j] - Z0))
            lx = self.u[j] + numerator_x / denomanator
            ly = self.v[j] + numerator_y / denomanator
            L.append(lx)
            L.append(ly)
        L = np.array(L,dtype=np.float32)
        return L

    def genAB(self, X, Y, Z, phi, omega, kappa, X0, Y0, Z0):
        R = CamTool().calcR(phi, omega, kappa)
        a1, a2, a3, b1, b2, b3, c1, c2, c3 = [i for l in R.tolist() for i in l]
        num_of_samples = len(self.u)

        a11 = np.zeros(num_of_samples, dtype=np.float32)
        a12 = np.zeros(num_of_samples, dtype=np.float32)
        a13 = np.zeros(num_of_samples, dtype=np.float32)

        a14 = np.zeros(num_of_samples, dtype=np.float32)
        a15 = np.zeros(num_of_samples, dtype=np.float32)
        a16 = np.zeros(num_of_samples, dtype=np.float32)

        a21 = np.zeros(num_of_samples, dtype=np.float32)
        a22 = np.zeros(num_of_samples, dtype=np.float32)
        a23 = np.zeros(num_of_samples, dtype=np.float32)
        a24 = np.zeros(num_of_samples, dtype=np.float32)
        a25 = np.zeros(num_of_samples, dtype=np.float32)
        a26 = np.zeros(num_of_samples, dtype=np.float32)

        for j in range(num_of_samples):
            z_bar = a3 * (X[j] - X0) + b3 * (Y[j] - Y0) + c3 * (Z[j] - Z0)
            a11[j] = (a1 * self.f + a3 * self.u[j]) / z_bar
            a12[j] = (b1 * self.f + b3 * self.u[j]) / z_bar
            a13[j] = (c1 * self.f + c3 * self.u[j]) / z_bar
            a14[j] = (self.v[j] * np.sin(omega)) - (self.u[j] * (
                    self.u[j] * np.cos(kappa) - self.v[j] * np.sin(kappa)) / self.f + self.f * np.cos(
                kappa)) * np.cos(omega)
            a15[j] = -self.f * np.sin(kappa) - (self.u[j] / self.f) * (
                    self.u[j] * np.sin(kappa) + self.v[j] * np.cos(kappa))
            a16[j] = self.v[j]

            a21[j] = (a2 * self.f + a3 * self.v[j]) / z_bar
            a22[j] = (b2 * self.f + b3 * self.v[j]) / z_bar
            a23[j] = (c2 * self.f + c3 * self.v[j]) / z_bar
            a24[j] = -self.u[j] * np.sin(omega) - (self.v[j] / self.f) * (
                    (self.u[j] * np.cos(kappa) - self.v[j] * np.sin(kappa)) - self.f * np.sin(
                kappa)) * np.cos(omega)
            a25[j] = -self.f * np.cos(kappa) - (self.v[j] / self.f) * (
                    self.u[j] * np.sin(kappa) + self.v[j] * np.cos(kappa))
            a26[j] = -self.u[j]

        A = np.zeros((2 * num_of_samples, 6), dtype=np.float32)
        B = np.zeros((2 * num_of_samples, 3), dtype=np.float32)
        for j in range(num_of_samples):
            A[2 * j:2 * j + 2, :] = np.array([
                [a11[j], a12[j], a13[j], a14[j], a15[j], a16[j]],
                [a21[j], a22[j], a23[j], a24[j], a25[j], a26[j]]
            ], dtype=np.float32)
            B[2 * j:2 * j + 2, :] = np.array([
                [-a11[j], -a12[j], -a13[j]],
                [-a21[j], -a22[j], -a23[j]]
            ], dtype=np.float32)
        return A, B

    def genT_noba(self, A, L):

        AtA = np.dot(A.T, A)
        inverse_AtA = np.linalg.inv(AtA)
        print(333, inverse_AtA)
        combine = np.dot(inverse_AtA, A.T)
        X = np.dot(combine, L)
        return X

    def genT(self, A, B, L):
        N11 = A.T @ A
        N12 = A.T @ B
        N21 = B.T @ A
        N22 = B.T @ B
        M1 = A.T @ L
        M2 = B.T @ L
        right = M1 - N12 @ np.linalg.inv(N22) @ M2
        left = N11 - N12 @ np.linalg.inv(N22) @ N21
        print("begin inv")
        left_inv = np.linalg.inv(left)
        print("inv", left_inv)
        t = np.dot(left_inv, right)
        return t

    def genDxyz(self, B, L):
        inverse_BtB = np.linalg.inv(np.dot(B.T, B))
        combine = np.dot(inverse_BtB, B.T)
        X = np.dot(combine, L)
        return X
