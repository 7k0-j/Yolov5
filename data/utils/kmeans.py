#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np


# ����IOU�ĸ��������ֻ�ǿ���anchor�ĳ���
def wh_iou(wh1, wh2):
    # Returns the nxm IoU matrix. wh1 is nx2, wh2 is mx2
    wh1 = wh1[:, None]  # [N,1,2]
    wh2 = wh2[None]  # [1,M,2]
    inter = np.minimum(wh1, wh2).prod(2)  # [N,M]
    return inter / (wh1.prod(2) + wh2.prod(2) - inter)  # iou = inter / (area1 + area2 - inter)


# k-means���࣬������ָ�����IOU
def k_means(boxes, k, dist=np.median, use_iou=True, use_pp=False):
 
    #yolo k-means methods
   #Args:
       # boxes: ��Ҫ�����bboxes,bboxesΪn*2����w��h
        #k: ����(�۳ɼ���)
       # dist: ���´�����ķ���(Ĭ��ʹ����λ�����Ⱦ�ֵЧ���Ժ�)
       # use_iou���Ƿ�ʹ��IOU��Ϊ����
        #use_pp���Ƿ���ͬk-means++�㷨
  
    box_number = boxes.shape[0]
    last_nearest = np.zeros((box_number,))
    # �����е�bboxes�������ѡk����Ϊ�ص�����
    if not use_pp:
        clusters = boxes[np.random.choice(box_number, k, replace=False)]
    # k_means++�����ʼֵ
    else:
        clusters = calc_center(boxes, k)

    # print(clusters)
    while True:
        # ����ÿ��bboxes��ÿ���صľ��� 1-IOU(bboxes, anchors)
        if use_iou:
            distances = 1 - wh_iou(boxes, clusters)
        else:
            distances = calc_distance(boxes, clusters)
        # ����ÿ��bboxes��������Ĵ�����
        current_nearest = np.argmin(distances, axis=1)
        # ÿ������Ԫ�ز��ڷ����仯˵���Լ��������
        if (last_nearest == current_nearest).all():
            break  # clusters won't change
        for cluster in range(k):
            # ����ÿ�����е�bboxes���¼��������
            clusters[cluster] = dist(boxes[current_nearest == cluster], axis=0)

        last_nearest = current_nearest

    return clusters


# ���㵥��һ�����һ�����ĵľ���
def single_distance(center, point):
    center_x, center_y = center[0] / 2, center[1] / 2
    point_x, point_y = point[0] / 2, point[1] / 2
    return np.sqrt((center_x - point_x) ** 2 + (center_y - point_y) ** 2)


# �������ĵ��������ֱ�ӵľ���
def calc_distance(boxes, clusters):
   
   # :param obs: ���еĹ۲��
   # :param clusters: ���ĵ�
    #:return:ÿ�����Ӧ���ĵ�ľ���
    
    distances = []
    for box in boxes:
        # center_x, center_y = x/2, y/2
        distance = []
        for center in clusters:
            # center_xc, cneter_yc = xc/2, yc/2
            distance.append(single_distance(box, center))
        distances.append(distance)

    return distances


# k_means++������������
def calc_center(boxes, k):
    box_number = boxes.shape[0]
    # ���ѡȡ��һ�����ĵ�
    first_index = np.random.choice(box_number, size=1)
    clusters = boxes[first_index]
    # ����ÿ�����������ĵ�ľ���
    dist_note = np.zeros(box_number)
    dist_note += np.inf
    for i in range(k):
        # ����Ѿ��ҹ��˾������ģ����˳�
        if i + 1 == k:
            break
        # ���㵱ǰ���ĵ��������ľ���
        for j in range(box_number):
            j_dist = single_distance(boxes[j], clusters[i])
            if j_dist < dist_note[j]:
                dist_note[j] = j_dist
        # ת��Ϊ����
        dist_p = dist_note / dist_note.sum()
        # ʹ�ö����̷�ѡ����һ����
        next_index = np.random.choice(box_number, 1, p=dist_p)
        next_center = boxes[next_index]
        clusters = np.vstack([clusters, next_center])
    return clusters