
from PIL import Image
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
from pydantic import BaseModel
from typing import List

from comfyui import ComfyUI_API

import uvicorn
import asyncio

class GenerateImagesResponse(BaseModel):
	images : List[str]

app = FastAPI(title='Local Image Generation', description='This api allows local image generation with ComfyUI.', version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.post('/generate_workflow', description='Generate a image given the generation workflow.')
async def generate_image(workflow : dict) -> GenerateImagesResponse:
	print(workflow)
	COMFYUI_NODE = ComfyUI_API('127.0.0.1:8188')
	await COMFYUI_NODE.is_available()
	await COMFYUI_NODE.open_websocket()
	image_array : list[dict] = await COMFYUI_NODE.generate_images_using_workflow_prompt(workflow)
	await COMFYUI_NODE.close_websocket()
	if len(image_array) == 0: return None
	raw_image : bytes = image_array[0]['image_data']
	return Image.open(BytesIO(raw_image))

async def uvicorn_run(app : FastAPI, host : str = "127.0.0.1", port : int = 8000) -> None:
	config = uvicorn.Config(app, host=host, port=port, access_log=False, server_header=False, date_header=False, proxy_headers=False)
	await uvicorn.Server(config).serve()

if __name__ == '__main__':
	asyncio.run(uvicorn_run(app, host='127.0.0.1', port=8000))
