
from typing import Optional
from PIL import Image
from io import BytesIO

from abyss_diver.models import CharacterData, SceneData
from abyss_diver.workflows.portrait import PortraitT2IGenericWorkflow, PrepareSimpleT2IWorkflow, PortraitT2IDepthControlWorkflow, PrepareSDXLDepthWorkflow
from abyss_diver.comfyui import ComfyUI_API

DEFAULT_POSITIVE_PROMPT : str = "(masterpiece,best quality,high quality,medium quality,normal quality)"
DEFAULT_NEGATIVE_PROMPT : str = "lowres, text, error, cropped, worst quality, low quality, jpeg artifacts, ugly, duplicate, morbid, mutilated, out of frame, extra fingers, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed, blurry, dehydrated, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers, long neck, username, watermark, signature"

BODY_FITNESS : list[str] = ["fragile body", "weak body", "average body", "fit body", "very fit body"]
HEIGHT_RANGES : list[tuple[str, int]] = [("dwarf",150),("midget",160),("short",170),("",183),("tall",195)]

# GENDER_REVERSAL_STAGE = ["", "dainty, twink,", "androgynous", "feminine", "female"]
PENIS_SIZES : list[str] = ["small penis", "below average penis", "average penis", "large penis", "huge penis"]

def height_to_ranged_value(height : int | float) -> str:
	for item in HEIGHT_RANGES:
		if height < item[1]:
			return item[0]
	return HEIGHT_RANGES[len(HEIGHT_RANGES)-1][0]

# PORTRAIT GENERATOR
async def prepare_portrait_prompt(
	character_data : CharacterData
) -> str:

	base_prompt = DEFAULT_POSITIVE_PROMPT
	base_prompt += ",solo,portrait,upper_body,plain dark background,"

	# temporary
	base_prompt += character_data.state.sex + ","
	base_prompt += f"{max(character_data.state.apparent_age, 21)} years old,"
	base_prompt += BODY_FITNESS[max(min(character_data.character.fit+2, 4), 0)] + ","
	base_prompt += height_to_ranged_value(character_data.state.height) + ","
	base_prompt += character_data.state.hair + " hair,"
	for tail in character_data.state.tail:
		base_prompt += character_data.state.hair + " " + tail + " tail,"
	base_prompt += character_data.state.hair + " " + character_data.state.ears + " ears,"

	# CreatureOfTheNight -> Vampire
	if "CreatureOfTheNight" in character_data.curses:
		base_prompt += "vampire,fangs,red eyes,glowing eyes,pale skin,"
	else:
		base_prompt += character_data.state.eyeColor + " eyes,"
		base_prompt += character_data.state.skinColor + " skin,"

	if "WrigglyAntennae" in character_data.curses:
		base_prompt += "pink antennae,"
	if "Megadontia" in character_data.curses:
		base_prompt += "sharp teeth,"
	if "FreckleSpeckle" in character_data.curses:
		base_prompt += "freckles,"
	if "KnifeEar" in character_data.curses:
		base_prompt += "pointy ears,"
	if "Horny" in character_data.curses:
		base_prompt += "succubus horns,"
	if "DrawingSpades" in character_data.curses:
		base_prompt += "spade tail,"

	if "ClothingRestrictionA" not in character_data.curses:
		base_prompt += "earrings,"

	if "ClothingRestrictionC" not in character_data.curses:
		base_prompt += "adventurer,leather armor,"

	if "ClothingRestrictionC" in character_data.curses:
		if "ClothingRestrictionB" in character_data.curses:
			base_prompt += "nude,"
		else:
			if character_data.state.sex == "female":
				base_prompt += "bra,panties,"
			else:
				base_prompt += "underwear,shirtless,no pants,"
				base_prompt += "small penis bulge,"

	if "ClothingRestrictionC" in character_data.curses and "ClothingRestrictionB" in character_data.curses:
		# NUDE
		if "Null" in character_data.curses:
			# null curse
			base_prompt += "smooth featureless body, no genitalia, soft abstract body aesthetic without explicit details,"
		else:
			# sex-specific
			if character_data.state.sex == "female":
				# female
				if "TattooTally" in character_data.curses:
					base_prompt += "succubus tattoo,"
				if "Leaky" in character_data.curses:
					base_prompt += "pussy juice,"
			else:
				# male
				if "TattooTally" in character_data.curses:
					base_prompt += "incubus tattoo,"
				if "Leaky" in character_data.curses:
					base_prompt += "pre-ejaculation,"

			# lactation (both M/F)
			lactation : int = 0
			if "LactationRejuvenationA" in character_data.curses:
				lactation += 1
			if "LactationRejuvenationB" in character_data.curses:
				lactation += 1

			if lactation == 2:
				base_prompt += "milk,lactating,lactation,"
			elif lactation == 1:
				base_prompt += "dripping lactation,"

			if character_data.state.penis_size > 0:
				base_prompt += PENIS_SIZES[character_data.state.penis_size-1] + ","

	base_prompt += character_data.state.breastsLabel + " breasts,"

	return base_prompt

async def generate_character(
	character : CharacterData
) -> Optional[Image.Image]:
	prompt : str = await prepare_portrait_prompt(character)
	print(prompt)

	params = PortraitT2IGenericWorkflow(
		checkpoint="hassakuXLHentai_v13.safetensors",
		positive_prompt=prompt,
		negative_prompt=DEFAULT_NEGATIVE_PROMPT
	)
	print(params)

	workflow = await PrepareSimpleT2IWorkflow(params)
	print(workflow)

	COMFYUI_NODE = ComfyUI_API('127.0.0.1:8188')
	await COMFYUI_NODE.is_available()
	await COMFYUI_NODE.open_websocket()

	image_array : list[dict] = await COMFYUI_NODE.generate_images_using_worflow_prompt(workflow)

	await COMFYUI_NODE.close_websocket()

	if len(image_array) == 0: return None

	raw_image : bytes = image_array[0]['image_data']
	return Image.open(BytesIO(raw_image))
