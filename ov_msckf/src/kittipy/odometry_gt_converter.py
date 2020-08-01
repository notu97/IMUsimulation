#!/usr/bin/env python
from transformation_helpers import euler_to_quat
import numpy as np
import os
import pandas as pd
import pykitti

# Change this to the directory where you store KITTI data
basedir = '/home/jamesdi1993/datasets/Kitti'

# Specify the dataset to load
sequence = '06'
date = '2011_09_30' # mapping from odometry to raw dataset 
drive = '0020'

odometry_path = os.path.join(basedir, 'dataset')
raw_data_path = os.path.join(basedir, 'raw_data')

# Read both odometry and raw datasets;
odometry_data = pykitti.odometry(odometry_path , sequence)
raw_data = pykitti.raw(raw_data_path, date, drive)

output_path = os.path.join(odometry_path, "poses/" + sequence + "_converted.txt")

# print(raw_data.calib)

P = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1]])


poses_camk_imu = [P.dot(T.dot(raw_data.calib.T_cam0_imu)) for T in odometry_data.poses]


# dataset.calib:      Calibration data are accessible as a named tuple
# dataset.timestamps: Timestamps are parsed into a list of timedelta objects
# dataset.poses:      List of ground truth poses T_w_cam0
# dataset.camN:       Generator to load individual images from camera N
# dataset.gray:       Generator to load monochrome stereo pairs (cam0, cam1)
# dataset.rgb:        Generator to load RGB stereo pairs (cam2, cam3)
# dataset.velo:       Generator to load velodyne scans as [x,y,z,reflectance]

print("Shape of the ground-truth poses: " + str(len(poses_camk_imu)))
print("\nShape of timestamps: " + str(len(odometry_data.timestamps)))

print("=======================================")

print("\nExample of ground-truth pose: " + str(poses_camk_imu[0]))
print("\nExample of timestamps: " + str(odometry_data.timestamps[0:10]))


# extract timestamps
timestamps = np.array(map(lambda x: x.total_seconds(), odometry_data.timestamps)).reshape(-1, 1)

# print(timestamps.shape)

# extra Rotations and Translations
(R_w_cam0, p_w_cam0) = zip(*map(lambda pose: (pose[0:3, 0:3], pose[0:3, 3]), poses_camk_imu))
print("\nExample of extracted rotation: " + str(R_w_cam0[0]))
print("\nExample of extracted translation: " + str(p_w_cam0[0]))

q_w_cam0 = np.array(map(euler_to_quat, R_w_cam0))
p_w_cam0 = np.array(p_w_cam0)

qs, qv = q_w_cam0[:, 0].reshape(-1, 1), q_w_cam0[:, 1:] 

# Construct dataset and output
dataset = pd.DataFrame(np.hstack((timestamps, p_w_cam0, qv, qs))) # (timestamp(s) tx ty tz qx qy qz qw)
dataset.to_csv(output_path, sep=' ', header=False, index=False)
 








