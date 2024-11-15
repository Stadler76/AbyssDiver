from PIL import Image
from io import BytesIO

import base64
import cv2
import numpy as np

def image_to_b64(image : Image.Image) -> str:
	buffered = BytesIO()
	image.save(buffered, format="PNG")
	return base64.b64encode(buffered.getvalue()).decode("utf-8")

def b64_to_image(b64 : str) -> Image.Image:
	buffer = BytesIO(base64.b64decode(b64))
	return Image.open(buffer).convert('RGB')

def cv2_to_pil(cv2_image : np.ndarray) -> Image.Image:
	return Image.fromarray(cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB))

def pil_to_cv2(pil_image : Image.Image) -> np.ndarray:
	return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
