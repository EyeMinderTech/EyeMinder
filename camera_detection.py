from torch.autograd import Variable
from detection import *
from ssd_net_vgg import *
from voc0712 import *
import torch
import torch.nn as nn
import numpy as np
import cv2
import utils
import torch.backends.cudnn as cudnn
import time
import tkinter as tk

class FatigueDetection:
    def __init__(self, model = './weights/ssd300_VOC_100000.pth'):
        # 检测cuda是否可用
        if torch.cuda.is_available():
            print('-----gpu mode-----')
            torch.set_default_tensor_type('torch.cuda.FloatTensor')
        else:
            print('-----cpu mode-----')
        self.show_result = 0
        self.show_keypoint = 1
        self.text_input_frame = None
        self.img_mean = (104.0, 117.0, 123.0)
        self.colors_tableau = [
            (214, 39, 40), (23, 190, 207), (188, 189, 34), (188, 34, 188), (205, 108, 8)]
        # Eye state list, suggest modifying based on fps
        self.list_B = np.ones(15)
        # Mouth state list, suggest modifying based on fps
        self.list_Y = np.zeros(50)
        # If list_Y has list_Y1, it is judged as yawning. Same as above, suggest modifying length
        self.list_Y1 = np.ones(5)
        self.blink_count = 0
        self.yawn_count = 0
        self.blink_start = time.time()
        self.yawn_start = time.time()
        self.blink_freq = 0.5
        self.yawn_freq = 0

        self.net = SSD()
        self.net = torch.nn.DataParallel(self.net)
        self.net.train(mode=False)
        self.net.load_state_dict(torch.load(
            model, map_location=lambda storage, loc: storage))
        self.detect = Detect.apply
        self.priors = utils.default_prior_box()
        self.labels = VOC_CLASSES
        # 调用摄像头
        self.cap = cv2.VideoCapture(0)
        self.max_fps = 0
        self.detect_fatigue()

    def Yawn(list_Y, list_Y1):
        list_cmp = list_Y[:len(list_Y1)] == list_Y1
        for flag in list_cmp:
            if flag == False:
                return False
        return True

    def get_frame_size(self):
        return int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def detect_fatigue(self):
        flag_B = True  # 是否闭眼的flag
        flag_Y = False
        num_rec = 0  # 检测到的眼睛的数量
        start = time.time()  # 计时
        ret, img = self.cap.read()  # 读取图片

        # 检测
        x = cv2.resize(img, (300, 300)).astype(np.float32)
        x -= self.img_mean
        x = x.astype(np.float32)
        x = x[:, :, ::-1].copy()
        x = torch.from_numpy(x).permute(2, 0, 1)
        xx = Variable(x.unsqueeze(0))
        if torch.cuda.is_available():
            xx = xx.cuda()
        y = self.net(xx)
        softmax = nn.Softmax(dim=-1)
        # detect=Detect(config.class_num,0,200,0.01,0.45)
        detect = Detect.apply
        priors = utils.default_prior_box()

        loc, conf = y
        loc = torch.cat([o.view(o.size(0), -1)for o in loc], 1)
        conf = torch.cat([o.view(o.size(0), -1)for o in conf], 1)

        detections = detect(
            loc.view(loc.size(0), -1, 4),
            softmax(conf.view(conf.size(0), -1, config.class_num)),
            torch.cat([o.view(-1, 4) for o in priors], 0),
            config.class_num,
            200,
            0.7,
            0.45
        ).data
        labels = VOC_CLASSES
        top_k = 10

        # 将检测结果放置于图片上
        scale = torch.Tensor(img.shape[1::-1]).repeat(2)
        for i in range(detections.size(1)):

            j = 0
            while detections[0, i, j, 0] >= 0.4:
                score = detections[0, i, j, 0]
                label_name = labels[i-1]
                if label_name == 'closed_eye':
                    flag_B = False
                if label_name == 'open_mouth':
                    flag_Y = True
                display_txt = '%s:%.2f' % (label_name, score)
                pt = (detections[0, i, j, 1:]*scale).cpu().numpy()
                coords = (pt[0], pt[1]), pt[2]-pt[0]+1, pt[3]-pt[1]+1
                color = self.colors_tableau[i]
                if self.show_keypoint:
                    cv2.rectangle(img, (int(pt[0]), int(
                        pt[1])), (int(pt[2]), int(pt[3])), color, 2)
                    cv2.putText(img, display_txt, (int(pt[0]), int(
                        pt[1])+10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, 8)
                j += 1
                num_rec += 1
        if num_rec > 0:
            if flag_B:
                # print(' 1:eye-open')
                self.list_B = np.append(self.list_B, 1)  # 睁眼为‘1’
            else:
                # print(' 0:eye-closed')
                self.list_B = np.append(self.list_B, 0)  # 闭眼为‘0’
            self.list_B = np.delete(self.list_B, 0)
            if flag_Y:
                self.list_Y = np.append(self.list_Y, 1)
            else:
                self.list_Y = np.append(self.list_Y, 0)
            self.list_Y = np.delete(self.list_Y, 0)
        # else:
        #     print('nothing detected')
        # print(list)
        # 实时计算PERCLOS
        perclos = 1-np.average(self.list_B)
        # print('perclos={:f}'.format(perclos))
        if self.list_B[13] == 1 and self.list_B[14] == 0:
            # 如果上一帧为’1‘，此帧为’0‘则判定为眨眼
            print('----------------眨眼----------------------')
            if self.show_result:
                self.text_input_frame.textbox.tag_config("debug", foreground="grey")
                self.text_input_frame.textbox.insert(tk.END, '<debug> 眨眼\n', 'debug')
            self.blink_count += 1
        blink_T = time.time()-self.blink_start
        if blink_T > 10:
            # 每10秒计算一次眨眼频率
            self.blink_freq = self.blink_count/blink_T
            self.blink_start = time.time()
            self.blink_count = 0
            print('blink_freq={:f}'.format(self.blink_freq))
        # 检测打哈欠
        # if Yawn(list_Y,list_Y1):
        if (self.list_Y[len(self.list_Y)-len(self.list_Y1):] == self.list_Y1).all():
            print('----------------------打哈欠----------------------')
            if self.show_result:
                self.text_input_frame.textbox.tag_config("debug", foreground="black", background="white")
                self.text_input_frame.textbox.insert(tk.END, '<debug> ----------------------打哈欠----------------------\n', 'debug')
            self.yawn_count += 1
            self.list_Y = np.zeros(50)
        # 计算打哈欠频率
        yawn_T = time.time()-self.yawn_start
        if yawn_T > 60:
            self.yawn_freq = self.yawn_count/yawn_T
            self.yawn_start = time.time()
            self.yawn_count = 0
            print('yawn_freq={:f}'.format(self.yawn_freq))

        # 此处为判断疲劳部分
        '''
			想法1：最简单，但是太影响实时性
			if(perclos>0.4 or blink_freq<0.25 or yawn_freq>5/60):
				print('疲劳')
				if(blink_freq<0.25)
			else:
				print('清醒')
			'''
        # 想法2：
        if (perclos > 0.4):
            print('疲劳')
            if self.show_result:
                self.text_input_frame.textbox.tag_config("debug", foreground="grey")
                self.text_input_frame.textbox.insert(tk.END, '<debug> 疲劳\n', 'debug')
        elif (self.blink_freq < 0.25):
            print('疲劳')
            if self.show_result:
                self.text_input_frame.textbox.tag_config("debug", foreground="grey")
                self.text_input_frame.textbox.insert(tk.END, '<debug> 疲劳\n', 'debug')
            self.blink_freq = 0.5  # 如果因为眨眼频率判断疲劳，则初始化眨眼频率
        elif (self.yawn_freq > 5.0/60):
            print("疲劳")
            if self.show_result:
                self.text_input_frame.textbox.tag_config("debug", foreground="grey")
                self.text_input_frame.textbox.insert(tk.END, '<debug> 疲劳\n', 'debug')
            self.yawn_freq = 0  # 初始化，同上
        # else:
        #     print('清醒')f
        if self.show_keypoint:
            T = time.time()-start
            fps = 1/T  # 实时在视频上显示fps
            if fps > self.max_fps:
                self.max_fps = fps
            fps_txt = 'fps:%.2f' % (fps)
            cv2.putText(img, fps_txt, (0, 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, 8)
            # cv2.imshow("ssd", img)
        self.image = img
