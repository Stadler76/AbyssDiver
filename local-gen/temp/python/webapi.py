
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from modals import SceneData, CharacterData, GenerateImagesResponse, GeneratePortraitPromptResponse
from workflows import PortraitT2IGenericWorkflow

app = FastAPI(title='Abyss Diver Local Generation', description='This api allows local image generation for the purpose for the game Abyss Diver.', version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.post('/generate_portrait_prompt', description='Generate a portrait prompt given the character state data from the Abyss Diver game.')
async def generate_portrait_prompt(
	character_data : CharacterData
) -> GeneratePortraitPromptResponse:
	print(character_data.model_dump())
	raise NotImplementedError

@app.post('/generate_portrait', description='Generate a portrait given the generation parameters.')
async def generate_portrait(
	generation_parms : PortraitT2IGenericWorkflow
) -> GenerateImagesResponse:
	print(generation_parms.model_dump())
	raise NotImplementedError

@app.post('/generate_scene', description='Generate a scene image given the generation parameters.')
async def generate_scene(
	scene_data : SceneData
) -> GenerateImagesResponse:
	print(scene_data.model_dump())
	raise NotImplementedError
