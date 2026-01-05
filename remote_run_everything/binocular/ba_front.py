import numpy as np
from remote_run_everything.binocular.back_tool import BackTool
from remote_run_everything.binocular.front_tool import FrontTool
from remote_run_everything.binocular.cam_tool import CamTool

#   4.213158  0.669677 -3.907534 -0.750835   60  0  -60
# 内方位元素：f，x0，y0  单位mm

class BaFront:
    def __init__(self, f1, f2, s1, s2, angle1, angle2, u1, v1, u2, v2):
        # 内方位元素：f，x0，y0  单位mm
        self.f1 = f1
        self.f2 = f2
        # 左右像片外方位元素  单位mm
        self.S1 = s1
        self.S2 = s2
        self.angle1 = angle1
        self.angle2 = angle2
        self.u1 = u1
        self.v1 = v1
        self.u2 = u2
        self.v2 = v2
        self.ftool = FrontTool()
        self.btool1 = BackTool(self.f1, u1, v1)
        self.btool2 = BackTool(self.f2, u2, v2)
        self.max_step = 1000000

    def first_cpt(self):
        # 计算基线分量，L.R为左右像片线元素
        B = self.S2 - self.S1
        R1 = CamTool().calcR(*self.angle1)
        R2 = CamTool().calcR(*self.angle2)
        XYZ1 = self.ftool.coordinate(R1, self.u1, self.v1, self.f1)  # 左片像空间辅助坐标
        XYZ2 = self.ftool.coordinate(R2, self.u2, self.v2, self.f2)  # 右片像空间辅助坐标
        N = self.ftool.genN(B, XYZ1, XYZ2)
        XYZ = self.ftool.xyz(self.S1, XYZ1, N)
        # CamTool().view_pcd(gp)
        return XYZ

    def refine(self, XYZ, which):
        X = XYZ[:, 0]
        Y = XYZ[:, 1]
        Z = XYZ[:, 2]
        if which == 1:
            btool = self.btool1
            X0, Y0, Z0 = self.S1.tolist()
            phi, omega, kappa = self.angle1
        else:
            btool = self.btool2
            X0, Y0, Z0 = self.S2.tolist()
            phi, omega, kappa = self.angle2
        for i in range(self.max_step):
            L = btool.genL(X, Y, Z, phi, omega, kappa, X0, Y0, Z0)
            A, B = btool.genAB(X, Y, Z, phi, omega, kappa, X0, Y0, Z0)
            dxyz = btool.genDxyz(B, L)

            # ex[dxs,dys,dzs,dphi,domega,dkappa]
            X += dxyz[0]
            Y += dxyz[1]
            Z += dxyz[2]

            limit = 0.00001
            if np.abs(dxyz[0]) < limit or np.abs(dxyz[1]) < limit or np.abs(dxyz[2]) < limit:
                err = np.mean(np.abs(dxyz))
                return XYZ, err

    def refine_all(self, XYZ):
        xyz1, err1 = self.refine(XYZ, 1)
        xyz2, err2 = self.refine(XYZ, 2)
        xyz = (xyz1 + xyz2) / 2
        return xyz, (err1 + err2) / 2

