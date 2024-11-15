
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from modals import GenerateImagesResponse, GeneratePortraitPrompt

app = FastAPI(title='Local Image Generation', description='This api allows local image generation with ComfyUI.', version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.post('/generate_image', description='Generate a image given the generation parameters.')
async def generate_portrait(params : GeneratePortraitPrompt) -> GenerateImagesResponse:
	print(params.model_dump())
	raise NotImplementedError

# @app.post('/generate_scene', description='Generate a scene image given the generation parameters.')
# async def generate_scene(
# 	scene_data : SceneData
# ) -> GenerateImagesResponse:
# 	print(scene_data.model_dump())
# 	raise NotImplementedError
