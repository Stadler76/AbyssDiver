
# https://9elements.com/blog/hosting-a-comfyui-workflow-via-api/
# pip install pydantic pillow websockets-client aiohttp

from io import BytesIO
from typing import Literal, Optional, Union
from urllib.parse import urlencode
from uuid import uuid4
from PIL import Image

import aiohttp
import asyncio
import base64
import json
import traceback
import websockets

COMFYUI_IMAGE_TYPE = Literal["input", "output", "temp"]

COMFYUI_SAMPLERS = Literal[
	"euler", "euler_ancestral", "heun",
	"dpm_2", "dpm_2_ancestral", "lms",
	"ddpm", "ddim", "uni_pc"
]

COMFYUI_SCHEDULERS= Literal[
	"normal", "karras", "exponential",
	"simple", "ddim_uniform", "beta"
]

def image_to_base64(image : Image.Image) -> str:
	buffered = BytesIO()
	image.save(buffered, format="PNG")
	return base64.b64encode(buffered.getvalue()).decode("utf-8")

def base64_to_image(b64 : str) -> Image.Image:
	buffer = BytesIO(base64.b64decode(b64))
	return Image.open(buffer).convert('RGB')

async def async_post(url : str, headers : Optional[dict] = None, cookies : Optional[dict] = None, json : Optional[dict] = None, data : Optional[str] = None) -> bytes:
	'''Asynchronously POST to the given url with the parameters.'''
	client : aiohttp.ClientSession
	async with aiohttp.ClientSession(headers=headers, cookies=cookies) as client:
		response : aiohttp.ClientResponse = await client.post(url, data=data, json=json)
		return await response.read()

async def post_json_response(url : str, data : Optional[dict]) -> Union[dict, list, None]:
	try:
		response : bytes = await async_post(url, json=data)
		return json.loads(response.decode('utf-8'))
	except Exception as e:
		traceback.print_exception(e)
		return None

async def async_get(url : str, headers : Optional[dict] = None, cookies : Optional[dict] = None, json : Optional[dict] = None, data : Optional[str] = None) -> bytes:
	'''Asynchronously POST to the given url with the parameters.'''
	client : aiohttp.ClientSession
	async with aiohttp.ClientSession(headers=headers, cookies=cookies) as client:
		response : aiohttp.ClientResponse = await client.get(url, data=data, json=json)
		return await response.read()

async def get_json_response(url : str) -> Union[dict, list, None]:
	try:
		response : bytes = await async_get(url)
		return json.loads(response.decode('utf-8'))
	except Exception as e:
		traceback.print_exception(e)
		return None

class ComfyUI_API:
	'''
	server_address : str = "127.0.0.1:8188"

	Cleaned up and asynchronous version of:
	- https://github.com/9elements/comfyui-api/blob/main/basic_api.py
	'''
	server_address : str
	client_id : str

	_active_ids : dict[str, bool]
	_websocket : Optional[websockets.WebSocketClientProtocol]

	def __init__(self, server_address : str) -> None:
		self.server_address = server_address
		self.client_id = uuid4().hex
		self._active_ids = dict()

		print(self.client_id)

	async def is_available(self) -> None:
		try:
			_ = await async_get(f"http://{self.server_address}")
		except:
			raise Exception("Cannot connect to ComfyUI!")

	async def open_websocket(self) -> None:
		address : str = f"ws://{self.server_address}/ws?clientId={self.client_id}"
		self._websocket = websockets.connect(address)

	async def close_websocket(self) -> None:
		self._websocket = None

	async def queue_prompt(self, prompt : dict) -> str:
		'''Queue the given prompt and return a prompt_id'''
		payload = {"prompt": prompt, "client_id": self.client_id}
		response = await post_json_response(f"http://{self.server_address}/prompt", data=payload)
		prompt_id : str = response['prompt_id']
		print(prompt_id)
		self._active_ids[prompt_id] = False
		return prompt_id

	async def is_prompt_id_finished(self, prompt_id : str) -> Optional[bool]:
		'''Check if the given prompt_id is finished.'''
		return self._active_ids.get(prompt_id)

	async def await_prompt_id(self, prompt_id : str) -> Optional[bool]:
		'''Await for the prompt id to finish - also returns if it finished or not.'''
		finished : Optional[bool] = self.is_prompt_id_finished(prompt_id)
		while finished is False:
			await asyncio.sleep(1.0)
			finished = self.is_prompt_id_finished(prompt_id)
		return finished

	async def fetch_prompt_id_history(self, prompt_id : str) -> dict:
		'''Fetch the generation history for the given prompt_id.'''
		history = await get_json_response(f"http://{self.server_address}/history/{prompt_id}")
		return history.get(prompt_id)

	async def fetch_image(self, filename : str, subfolder : str, folder_type : str) -> bytes:
		payload = {"filename": filename, "subfolder": subfolder, "type": folder_type}
		query : str = urlencode(payload)
		response : bytes = await async_get(f"http://{self.server_address}/view?{query}")
		return response

	async def fetch_prompt_id_images(self, prompt_id : str, include_previews : bool = False) -> list[dict]:
		'''Fetch the generated images for the given prompt_id if any.'''
		images : list[dict] = list()
		history : dict = await self.fetch_prompt_id_history(prompt_id)
		for node_id in history['outputs']:
			node_output = history['outputs'][node_id]
			if 'images' not in node_output:
				continue
			for image in node_output['images']:
				output_data = {"node_id" : node_id, "file_name" : image["filename"], "type" : image["type"]}
				if include_previews is True and image['type'] == 'temp':
					preview_data : bytes = await self.fetch_image(image['filename'], image['subfolder'], image['type'])
					output_data['image_data'] = preview_data
				if image['type'] == 'output':
					image_data : bytes = await self.fetch_image(image['filename'], image['subfolder'], image['type'])
					output_data['image_data'] = image_data
				images.append(output_data)

		return images

	async def track_progress(self, prompt_id : str, node_ids : list[int]) -> None:
		'''Echo the progress of the prompt_id.'''
		finished_nodes : list[str] = []
		async with self._websocket as socket:
			while True:
				# receive content
				content = await socket.recv()
				if isinstance(content, str) is False:
					continue
				message = json.loads(content)
				# progression of current
				if message['type'] == 'progress':
					data = message['data']
					current_step = data['value']
					print('In K-Sampler -> Step: ', current_step, ' of: ', data['max'])
				# another step of execution done
				if message['type'] == 'execution_cached':
					data = message['data']
					for itm in data['nodes']:
						if itm not in finished_nodes:
							finished_nodes.append(itm)
							print('Progess: ', len(finished_nodes)-1, '/', len(node_ids), ' Tasks done')
				# executing a new node if any
				if message['type'] == 'executing':
					data = message['data']
					if data['node'] not in finished_nodes:
						finished_nodes.append(data['node'])
						print('Progess: ', len(finished_nodes)-1, '/', len(node_ids), ' Tasks done')
					if data['node'] is None and data['prompt_id'] == prompt_id:
						# execution is done
						self._active_ids[prompt_id] = True
						break

	async def cleanup_prompt_id(self, prompt_id : str) -> None:
		self._active_ids.pop(prompt_id, None)

	async def generate_images_using_worflow_prompt(self, prompt : dict, include_previews : bool = True) -> list[dict]:
		'''Complete the full sequence of giving a prompt and receiving the images.'''
		prompt_id : str = await self.queue_prompt(prompt)
		await self.track_progress( prompt_id, prompt.keys() )
		images : list[dict] = await self.fetch_prompt_id_images(prompt_id, include_previews=include_previews)
		await self.cleanup_prompt_id(prompt_id)
		return images

	async def upload_image(self, image : Image.Image, save_name : str, image_type : COMFYUI_IMAGE_TYPE = "input", overwrite : bool = True) -> bool:
		"""Upload an image to ComfyUI to be used for workflows."""
		# use 'save_name' in LoadImage objects (with extension)
		# prepare image data
		byte_io = BytesIO()
		image.save(byte_io, format='PNG')
		byte_data = byte_io.getvalue()
		# prepare form data
		data = aiohttp.FormData()
		data.add_field('image', byte_data, filename=save_name, content_type="image/png")
		data.add_field('type', image_type)
		data.add_field('overwrite', str(overwrite).lower())
		# send request
		try:
			url : str = f'http://{self.server_address}/upload/image'
			client : aiohttp.ClientSession
			async with aiohttp.ClientSession() as client:
				response : aiohttp.ClientResponse = await client.post(url, data=data)
				if response.status != 200:
					print(f"Failed to upload image due to: {response.reason} (typicallycfile data)")
			return True
		except Exception as e:
			traceback.print_exception(e)
			return False
