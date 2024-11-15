# https://huggingface.co/spaces/SmilingWolf/wd-v1-4-tags

from onnxruntime import InferenceSession
from PIL import Image

import numpy as np
import csv
import os
import requests

defaults = {
	"model": "wd-v1-4-moat-tagger-v2",
	"threshold": 0.35,
	"character_threshold": 0.85,
	"replace_underscore": False,
	"trailing_comma": False,
	"exclude_tags": "",
	"ortProviders": ["CUDAExecutionProvider", "CPUExecutionProvider"],
	"HF_ENDPOINT": "https://huggingface.co"
}

models_dir = "models"

config = {
	"models": {
		"wd-vit-tagger-v3": "{HF_ENDPOINT}/SmilingWolf/wd-vit-tagger-v3",
		"wd-swinv2-tagger-v3": "{HF_ENDPOINT}/SmilingWolf/wd-swinv2-tagger-v3",
		"wd-convnext-tagger-v3": "{HF_ENDPOINT}/SmilingWolf/wd-convnext-tagger-v3",
		"wd-v1-4-moat-tagger-v2": "{HF_ENDPOINT}/SmilingWolf/wd-v1-4-moat-tagger-v2",
		"wd-v1-4-convnextv2-tagger-v2": "{HF_ENDPOINT}/SmilingWolf/wd-v1-4-convnextv2-tagger-v2",
		"wd-v1-4-convnext-tagger-v2": "{HF_ENDPOINT}/SmilingWolf/wd-v1-4-convnext-tagger-v2",
		"wd-v1-4-convnext-tagger": "{HF_ENDPOINT}/SmilingWolf/wd-v1-4-convnext-tagger",
		"wd-v1-4-vit-tagger-v2": "{HF_ENDPOINT}/SmilingWolf/wd-v1-4-vit-tagger-v2",
		"wd-v1-4-swinv2-tagger-v2": "{HF_ENDPOINT}/SmilingWolf/wd-v1-4-swinv2-tagger-v2",
		"wd-v1-4-vit-tagger": "{HF_ENDPOINT}/SmilingWolf/wd-v1-4-vit-tagger"
	}
}

cache = {}

def get_installed_models():
	models = filter(lambda x: x.endswith(".onnx"), os.listdir(models_dir))
	models = [m for m in models if os.path.exists(os.path.join(models_dir, os.path.splitext(m)[0] + ".csv"))]
	return models

def download_file(url: str, destination: str) -> None:
	try:
		# Send a GET request to the URL
		response = requests.get(url, stream=True)
		response.raise_for_status()  # Raise an error for bad responses

		# Open the destination file in write-binary mode
		with open(destination, 'wb') as file:
			for chunk in response.iter_content(chunk_size=8192):
				file.write(chunk)  # Write the chunk to the file

		print(f"File downloaded successfully: {destination}")

	except requests.exceptions.RequestException as e:
		print(f"Error downloading file: {e}")

def download_model(model):
	hf_endpoint = os.getenv("HF_ENDPOINT", defaults["HF_ENDPOINT"])
	if not hf_endpoint.startswith("https://"):
		hf_endpoint = f"https://{hf_endpoint}"
	if hf_endpoint.endswith("/"):
		hf_endpoint = hf_endpoint.rstrip("/")

	url = config["models"][model]
	url = url.replace("{HF_ENDPOINT}", hf_endpoint)
	url = f"{url}/resolve/main/"
	download_file(f"{url}model.onnx", os.path.join(models_dir,f"{model}.onnx"))
	download_file(f"{url}selected_tags.csv", os.path.join(models_dir,f"{model}.csv"))

def tag(image : Image.Image, model_name, threshold=0.35, character_threshold=0.85, exclude_tags="", replace_underscore=True):
	if model_name.endswith(".onnx"):
		model_name = model_name[0:-5]
	installed = list(get_installed_models())
	if not any(model_name + ".onnx" in s for s in installed):
		download_model(model_name)

	name = os.path.join(models_dir, model_name + ".onnx")
	if cache.get(name) is None:
		cache[name] = InferenceSession(name, providers=defaults["ortProviders"])

	model = cache[name]

	input = model.get_inputs()[0]
	height = input.shape[1]

	# Reduce to max size and pad with white
	ratio = float(height)/max(image.size)
	new_size = tuple([int(x*ratio) for x in image.size])
	image = image.resize(new_size, Image.LANCZOS)
	square = Image.new("RGB", (height, height), (255, 255, 255))
	square.paste(image, ((height-new_size[0])//2, (height-new_size[1])//2))

	image = np.array(square).astype(np.float32)
	image = image[:, :, ::-1]  # RGB -> BGR
	image = np.expand_dims(image, 0)

	# Read all tags from csv and locate start of each category
	tags = []
	general_index = None
	character_index = None
	with open(os.path.join(models_dir, model_name + ".csv")) as f:
		reader = csv.reader(f)
		next(reader)
		for row in reader:
			if general_index is None and row[2] == "0":
				general_index = reader.line_num - 2
			elif character_index is None and row[2] == "4":
				character_index = reader.line_num - 2
			if replace_underscore:
				tags.append(row[1].replace("_", " "))
			else:
				tags.append(row[1])

	label_name = model.get_outputs()[0].name
	probs = model.run([label_name], {input.name: image})[0]

	result = list(zip(tags, probs[0]))

	# rating = max(result[:general_index], key=lambda x: x[1])
	general = [item for item in result[general_index:character_index] if item[1] > threshold]
	character = [item for item in result[character_index:] if item[1] > character_threshold]

	all = character + general
	remove = [s.strip() for s in exclude_tags.lower().split(",")]
	all = [tag for tag in all if tag[0] not in remove]

	return all
