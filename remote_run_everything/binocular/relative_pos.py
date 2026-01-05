# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 12:23:35 2020
@author: 陨星落云
"""
import numpy as np
from numpy import linalg
from remote_run_everything.binocular.cam_tool import CamTool
import copy
from remote_run_everything.binocular.ba_front import BaFront


class RelativePos:
    def __init__(self, pathl,pathr,unitl,unitr):
        self.pathl=pathl
        self.pathr=pathr
        self.unitl=unitl
        self.unitr=unitr
        self.cam=CamTool()
        self.f=self.cam.fx(self.pathl)*self.unitl
        self.fi = 0
        self.omega = 0
        self.kapa = 0
        self.u_bv = 0
        self.r_bw = 0


    def rel_one(self, l0, r0):
        cxcyl = self.cam.cx_cy(self.pathl)
        cxcyr = self.cam.cx_cy(self.pathr)
        # 像素坐标换相平面坐标 输入同名像素点 [(u,v),]
        l = self.uv_process(self.unitl, cxcyl[0], cxcyl[1], copy.deepcopy(l0))
        r = self.uv_process(self.unitr, cxcyr[0], cxcyr[1], copy.deepcopy(r0))
        # 后方交汇 改写右边-->左边的旋角,u,v,返回使用到的像素点index
        new_match = self.back_intersect(l, r)
        if new_match is None:
            print("can not solve relative pos")
            return None
        a1 = [0, 0, 0]
        a2 = [self.fi, self.omega, self.kapa]
        S1 = np.array([0., 0., 0.])
        S2 = np.array([1, self.u_bv, self.r_bw])
        l = l[new_match, :]
        r = r[new_match, :]
        fl=self.cam.fx(self.pathl)*self.unitl
        fr=self.cam.fx(self.pathr)*self.unitr
        f = BaFront(fl, fr, S1, S2, a1, a2, l[:, 0], l[:, 1], r[:, 0],
                    r[:, 1])
        # 前方交汇
        pcd = f.first_cpt()
        d = {"pcd": pcd, "T": S2, "angle": a2, "match": new_match
             # "match": np.concatenate([i['l'][new_match, :], i['r'][new_match, :]], axis=1),
             }
        return d

    def uv_process(self, unit, cx, cy, l):
        l[:, 0] = unit * (l[:, 0] - cx)
        l[:, 1] = unit * (cy - l[:, 1])
        return l

    def cptaq(self, i, l, r):
        # 计算旋转矩阵
        R = CamTool().calcR(self.fi, self.omega, self.kapa)
        # 比例尺  怎么都无所谓
        bu = l[0][0] - r[0][0]
        bv = bu * self.u_bv
        bw = bu * self.r_bw
        # 左片相对摄影测量坐标
        u1 = l[i][0]
        v1 = l[i][1]
        w1 = -self.f
        # 计算相对摄影测量坐标
        mr = np.dot(R, np.array([r[i][0], r[i][1], -self.f]))
        # 右片相对摄影测量坐标
        u2 = mr[0]
        v2 = mr[1]
        w2 = mr[2]
        # 计算N1,N2
        N1 = (bu * w2 - bw * u2) / (u1 * w2 - u2 * w1)
        N2 = (bu * w1 - bw * u1) / (u1 * w2 - u2 * w1)
        # 计算每个点Q
        Q = N1 * v1 - N2 * v2 - bv
        a = -u2 * v2 * N2 / w2
        b = -N2 * (w2 + v2 * v2 / w2)
        c = u2 * N2
        d = bu
        e = -v2 * bu / w2
        return np.array([a, b, c, d, e]), Q

    def back_intersect(self, l, r):
        n = l.shape[0]
        countx, countj = (0, 0)
        # 误差方程参数
        # 右片相对相空间坐标，相对摄影测量坐标
        # 迭代运算
        while True:
            Al = []
            Ll = []
            new_match = []

            # 计算每个点参数，组成法方程矩阵
            for i in range(n):
                ai, Q = self.cptaq(i, l, r)
                if np.isnan(Q):
                    continue
                new_match.append(i)
                Al.append(ai)
                Ll.append(Q)
                # A[i, :] = ai
                # L[i] = Q
            # 求解X
            A = np.array(Al)
            L = np.array(Ll)
            try:
                inv = linalg.inv(np.dot(A.T, A))
            except:
                return None
            X = np.dot(np.dot(inv, A.T), L)
            # 累加五参数
            self.fi += X[0]
            self.omega += X[1]
            self.kapa += X[2]
            self.u_bv += X[3]
            self.r_bw += X[4]
            # 循环次数＋
            countx += 1
            # 判断是否收敛
            if countx > 1000:
                return None

            if (np.abs(X) < 0.00003).all():
                print("五参数", self.fi, self.omega, self.kapa, self.u_bv, self.r_bw)
                # 精度评定
                V = np.dot(A, X.T) - L
                c1 = np.sqrt(np.dot(V.T, V) / n)
                print("相对定向精度：", c1)
                print("相对定向迭代次数：", countx)
                print("新的配对长度：", len(new_match))
                return new_match



