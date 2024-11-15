
from typing import Literal, Union
from pydantic import BaseModel

SDXL_MODELS = Literal["hassakuXLHentai_v13.safetensors"]
SDXL_DEPTH_CONTROL_MODELS = Literal["control-lora-depth-rank256.safetensors"]

SIMPLE_TXT2IMG_IMAGE_GENERIC_WORKFLOW : dict = {
	"5": {
		"inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"},
		"class_type": "CheckpointLoaderSimple",
		"_meta": {"title": "Load Checkpoint"}
	},
	"9": {
		"inputs": {"text": "","clip": ["5",1]},
		"class_type": "CLIPTextEncode",
		"_meta": {"title": "Positive Prompt"}
	},
	"10": {
		"inputs": {"text": "","clip": ["5",1]},
		"class_type": "CLIPTextEncode",
		"_meta": {"title": "Negative Prompt"}
	},
	"11": {
		"inputs": {
			"seed": 961176784184834,
			"steps": 35,
			"cfg": 7,
			"sampler_name": "dpmpp_3m_sde_gpu",
			"scheduler": "exponential",
			"denoise": 1,
			"model": ["5",0],
			"positive": ["9",0],
			"negative": ["10",0],
			"latent_image": ["12",0]
		},
		"class_type": "KSampler",
		"_meta": {"title": "KSampler"}
	},
	"12": {
		"inputs": {"width": 1024,"height": 1024,"batch_size": 1},
		"class_type": "EmptyLatentImage",
		"_meta": {"title": "Empty Latent Image"}
	},
	"15": {
		"inputs": {"samples": ["11",0],"vae": ["5",2]},
		"class_type": "VAEDecode",
		"_meta": {"title": "VAE Decode"}
	},
	"16": {
		"inputs": {"filename_prefix": "ComfyUI","images": ["15",0]},
		"class_type": "SaveImage",
		"_meta": {"title": "Save Image"}
	}
}

CONTROL_NET_DYNAMIC_DEPTH_WORKFLOW : dict = {
	"1": {
		"inputs": {"image": "00007-4032934194.png","upload": "image"},
		"class_type": "LoadImage",
		"_meta": {"title": "Load Image"}
	},
	"2": {
		"inputs": {"a": 6.2832,"bg_threshold": 0.1,"resolution": 512,"image": ["1",0]},
		"class_type": "MiDaS-DepthMapPreprocessor",
		"_meta": {"title": "MiDaS Depth Map"}
	},
	"3": {
		"inputs": {"images": ["2",0]},
		"class_type": "PreviewImage",
		"_meta": {"title": "Preview Image"}
	},
	"5": {
		"inputs": {"ckpt_name": "ThinkDiffusionXL.safetensors"},
		"class_type": "CheckpointLoaderSimple",
		"_meta": {"title": "Load Checkpoint"}
	},
	"7": {
		"inputs": {"control_net_name": "control-lora-depth-rank256.safetensors"},
		"class_type": "ControlNetLoader",
		"_meta": {"title": "Load ControlNet Model"}
	},
	"8": {
		"inputs": {
			"strength": 1,
			"start_percent": 0,
			"end_percent": 1,
			"positive": ["9",0],
			"negative": ["10",0],
			"control_net": ["7",0],
			"image": ["2",0]
		},
		"class_type": "ControlNetApplyAdvanced",
		"_meta": {"title": "Apply ControlNet (Advanced)"}
	},
	"9": {
		"inputs": {"text": "a futuristic cyborg on an alien spaceship","clip": ["5",1]},
		"class_type": "CLIPTextEncode",
		"_meta": {"title": "Positive Prompt"}
	},
	"10": {
		"inputs": {"text": "","clip": ["5",1]},
		"class_type": "CLIPTextEncode",
		"_meta": {"title": "Negative Prompt"}
	},
	"11": {
		"inputs": {
			"seed": 961176784184834,
			"steps": 35,
			"cfg": 7,
			"sampler_name": "dpmpp_3m_sde_gpu",
			"scheduler": "exponential",
			"denoise": 1,
			"model": ["5",0],
			"positive": ["8",0],
			"negative": ["8",1],
			"latent_image": ["12",0]
		},
		"class_type": "KSampler",
		"_meta": {"title": "KSampler"}
	},
	"12": {
		"inputs": {"width": 1024,"height": 1024,"batch_size": 1},
		"class_type": "EmptyLatentImage",
		"_meta": {"title": "Empty Latent Image"}
	},
	"15": {
		"inputs": {"samples": ["11",0], "vae": ["5",2]},
		"class_type": "VAEDecode",
		"_meta": {"title": "VAE Decode"}
	},
	"16": {
		"inputs": {"filename_prefix": "ComfyUI", "images": ["15",0]},
		"class_type": "SaveImage",
		"_meta": {"title": "Save Image"}
	}
}

# SIMPLE_TXT2IMG_IMAGE_GENERIC_WORKFLOW
class PortraitT2IGenericWorkflow(BaseModel):
	checkpoint : SDXL_MODELS
	positive_prompt : str
	negative_prompt : str

	steps : int = 20
	cfg : Union[float, int] = 7.0
	width : int = 1024
	height : int = 1024

	seed : int = 0

# CONTROL_NET_DYNAMIC_DEPTH_WORKFLOW
class PortraitT2IDepthControlWorkflow(BaseModel):
	checkpoint : SDXL_MODELS
	positive_prompt : str
	negative_prompt : str

	controlnet_depth_model : SDXL_DEPTH_CONTROL_MODELS
	depth_image_base64 : str

	steps : int = 25
	cfg : Union[int, float] = 7.0
	width : int = 1024
	height : int = 1024

	seed : int = -1

async def PrepareSimpleT2IWorkflow(params : PortraitT2IGenericWorkflow) -> dict:
	workflow = SIMPLE_TXT2IMG_IMAGE_GENERIC_WORKFLOW.copy()
	workflow["5"]["inputs"]["ckpt_name"] = params.checkpoint
	workflow["9"]["inputs"]["text"] = params.positive_prompt
	workflow["10"]["inputs"]["text"] = params.negative_prompt
	workflow["11"]["inputs"]["steps"] = params.steps
	workflow["11"]["inputs"]["cfg"] = params.cfg
	workflow["11"]["inputs"]["seed"] = params.seed
	workflow["12"]["inputs"]["width"] = params.width
	workflow["12"]["inputs"]["height"] = params.height
	return workflow

async def PrepareSDXLDepthWorkflow(params : PortraitT2IDepthControlWorkflow) -> dict:
	workflow = CONTROL_NET_DYNAMIC_DEPTH_WORKFLOW.copy()
	workflow["5"]["inputs"]["ckpt_name"] = params.checkpoint
	workflow["7"]["inputs"]["control_net_name"] = params.controlnet_depth_model
	workflow["9"]["inputs"]["text"] = params.positive_prompt
	workflow["10"]["inputs"]["text"] = params.negative_prompt
	workflow["11"]["inputs"]["seed"] = params.seed
	workflow["11"]["inputs"]["steps"] = params.steps
	workflow["11"]["inputs"]["cfg"] = params.cfg
	workflow["12"]["inputs"]["width"] = params.width
	workflow["12"]["inputs"]["height"] = params.height
	return workflow
