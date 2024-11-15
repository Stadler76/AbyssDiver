
# https://github.com/CMU-Perceptual-Computing-Lab/openpose
# https://github.com/CMU-Perceptual-Computing-Lab/openpose/releases



# from openpose import pyopenpose as op

# import cv2
# import numpy as np

# def preprocess_openpose(image : np.ndarray) -> tuple[np.ndarray, list]:
# 	# Set OpenPose parameters
# 	params = {
# 		"model_folder": "path_to_openpose/models/",  # Adjust to your OpenPose model directory
# 		"hand": False,
# 		"face": False,
# 		"keypoint_scale": 3,
# 		"net_resolution": "-1x368",  # Resolution of the neural network input
# 	}

# 	# Initialize OpenPose
# 	opWrapper = op.WrapperPython()
# 	opWrapper.configure(params)
# 	opWrapper.start()

# 	# Process the image
# 	datum = op.Datum()
# 	datum.cvInputData = image
# 	opWrapper.emplaceAndPop([datum])

# 	# Extract keypoints
# 	keypoints = datum.poseKeypoints
# 	if keypoints is None:
# 		return None, None

# 	# Create a image for the skeleton
# 	skeleton_image = np.zeros_like(image)
# 	for person in keypoints:
# 		for i in range(len(person)):
# 			if person[i][2] > 0:  # Check if the keypoint is valid
# 				cv2.circle(skeleton_image, (int(person[i][0]), int(person[i][1])), 5, (0, 255, 0), -1)

# 	# Get the keypoint json data
# 	skeleton_data : list = keypoints.tolist()

# 	# Return the skeleton image and keypoints
# 	return skeleton_image, skeleton_data
