
from PIL import Image
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
from pydantic import BaseModel
from typing import List

from comfyui import ComfyUI_API, image_to_base64

import uvicorn
import asyncio

COMFYUI_NODE_URL : str = '127.0.0.1:8188'
# COMFYUI_NODE_URL : str = '192.168.1.54:8188' (another device on the network with "--listen 0.0.0.0" cmd line arg)

class GenerateImagesResponse(BaseModel):
	images : List[str]

app = FastAPI(title='Local Image Generation', description='This api allows local image generation with ComfyUI. Coded by @SPOOKEXE on GitHub', version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get('/echo', description='Echo back to let the client know the api is running.')
async def echo() -> bool:
	return True

@app.post('/generate_workflow', description='Generate a image given the generation workflow.')
async def generate_image(workflow : dict) -> GenerateImagesResponse:
	print(workflow)
	COMFYUI_NODE = ComfyUI_API(COMFYUI_NODE_URL)
	await COMFYUI_NODE.is_available()
	await COMFYUI_NODE.open_websocket()
	image_array : list[dict] = await COMFYUI_NODE.generate_images_using_workflow_prompt(workflow)
	await COMFYUI_NODE.close_websocket()
	if len(image_array) == 0: return None
	raw_image : bytes = image_array[0]['image_data']
	image = Image.open(BytesIO(raw_image))
	b64_image = image_to_base64(image)
	return GenerateImagesResponse(images=[b64_image])

async def uvicorn_run(app : FastAPI, host : str = "127.0.0.1", port : int = 12500) -> None:
	config = uvicorn.Config(app, host=host, port=port, access_log=False, server_header=True, date_header=False, proxy_headers=False)
	await uvicorn.Server(config).serve()

if __name__ == '__main__':
	asyncio.run(uvicorn_run(app, host='127.0.0.1', port=12500))
