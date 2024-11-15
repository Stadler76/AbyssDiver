
from __future__ import annotations
from typing import Any, Generator, Iterable, Literal
from torchvision import transforms
from PIL import Image

import numpy as np
import torch
import os

def batch_iterable(iterable : Iterable, batch_size : int) -> Generator[list[str], None, None]:
	"""Yield successive batches from an iterable."""
	batch = []
	for item in iterable:
		batch.append(item)
		if len(batch) == batch_size:
			yield batch
			batch = []
	if batch: yield batch

class DepthEstimator:
	DEPTH_ESTIMATOR_MODELS = Literal["DPT_Large", "DPT_Hybrid", "MiDaS_small"]

	model_type : str
	model : Any
	transform : Any

	def __init__(self, model_type : DepthEstimator.DEPTH_ESTIMATOR_MODELS) -> None:
		self.model_type = model_type
		self.setup()

	def setup(self) -> None:
		self.model = torch.hub.load("intel-isl/MiDaS", self.model_type, pretrained=True).to('cuda')
		self.model.eval()

		self.transform = transforms.Compose([
			transforms.Resize(384),
			transforms.ToTensor(),
			transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
		])

	def preprocess(self, image : Image.Image) -> Image.Image:
		img_tensor : torch.Tensor = self.transform(image).unsqueeze(0)
		with torch.no_grad():
			depth_map : torch.Tensor = self.model(img_tensor.to('cuda')).to('cpu')
		del img_tensor
		depth_map : np.ndarray = depth_map.squeeze().numpy()
		depth_map = (depth_map / depth_map.max() * 255).astype(np.uint8)
		depth_image : Image.Image = Image.fromarray(depth_map)
		del depth_map
		return depth_image

	def preprocess_bulk(self, images : list[Image.Image]) -> list[Image.Image]:
		img_tensors : list[torch.Tensor] = [self.transform(image).unsqueeze(0) for image in images]
		with torch.no_grad():
			depth_maps : list[np.ndarray] = [self.model(tensor.to('cuda')).to('cpu') for tensor in img_tensors]
		del img_tensors
		depth_maps = [(depth / depth.max() * 255).astype(np.uint8) for depth in depth_maps]
		image_maps = [Image.fromarray(depth) for depth in depth_maps]
		del depth_maps
		return image_maps

	def preprocess_directory(self, input_directory : str, output_directory : str, batch_size : int = 16) -> None:
		os.makedirs(output_directory, exist_ok=True)

		for filenames in batch_iterable(os.listdir(input_directory), batch_size=batch_size):
			for filename in filenames:
				filepath : str = os.path.join(input_directory, filename)
				if os.path.isfile(filepath) is False: continue
				# depth map
				img = Image.open(filepath)
				depth = self.preprocess(img)
				# save the depth map
				raw_filename, raw_fileext = os.path.splitext(filename)
				output_filepath : str = os.path.join(output_directory, f'{raw_filename}_depth{raw_fileext}')
				depth.save(output_filepath)
