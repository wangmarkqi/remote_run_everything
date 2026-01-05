import numpy as np


#   4.213158  0.669677 -3.907534 -0.750835   60  0  -60
# 内方位元素：f，x0，y0  单位mm

class FrontTool:
    def coordinate(self, R, u, v, f):  # 计算所求点的像空间辅助坐标系,xyz--> XYZ,R为旋转矩阵,P所求点像空间坐标,f为主距
        XYZ = []
        for i in range(len(u)):
            xyz = np.array([[u[i]], [v[i]], [-f]])
            XYZ.append(np.dot(R, xyz))
        return XYZ

    def projection_index(self, B, XYZ1, XYZ2):  # 投影系数计算
        bu = B[0]
        bw = B[2]
        u1 = XYZ1[0]
        w1 = XYZ1[2]
        u2 = XYZ2[0]
        w2 = XYZ2[2]
        N1 = (bu * w2 - bw * u2) / (u1 * w2 - u2 * w1)
        N2 = (bu * w1 - bw * u1) / (u1 * w2 - u2 * w1)
        return [N1[0], N2[0]]

    def genN(self, B, XYZ1, XYZ2):
        N = []
        for i in range(len(XYZ1)):
            N.append(self.projection_index(B, XYZ1[i], XYZ2[i]))
        return N

    def xyz(self, S1, XYZ1, N):
        l = []
        for i in range(len(XYZ1)):
            XYZ = XYZ1[i].reshape((3,))
            # 地面控制点坐标计算
            res = S1 + N[i][0] * XYZ
            l.append(res)
        return np.array(l)
