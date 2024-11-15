
'''
{
	"character":{
		"id":0,"name":"Nana","cost":-1,"carry":20,"affec":0,
		"swap":false,"mindSex":"female","osex":"female",
		"obreasts":1,"desiredBreasts":1,"openis":0,"ogender":6,
		"fit":0,"oheight":165,"comfortableHeight":170,"age":18,
		"appDesc":"","fear":"","ohair":"black","oskinColor":"pale",
		"oskinType":"","oears":"normal human","oeyeColor":"blue",
		"oblood":"red","pregnantT":999999999,"due":999999999,
		"tentaclePreg":false,"lastBirth":999999999,"switched":false,
		"gestationJumps":0,"location":-1
	},
	"curses":[
		"Libido Reinforcement A","Clothing Restriction A","Shrunken Assets",
		"Hair Removal","Knife-ear","Perma-dye","Freckle Speckle","Dizzying Heights",
		"Dizzying Heights","Dizzying Heights","Dizzying Heights","Dizzying Heights",
		"Increased Sensitivity","Refractory Refactorization","Libido Reinforcement B",
		"Age Reduction A","Fluffy Ears","Fluffy Tail","Heat/Rut","Lightweight",
		"Blushing Virgin"
	],
	"state":{
		"real_age":18.022,"apparent_age":16.022,"real_gender":6,
		"apparent_gender":9.951095162802796,"penis_size":0,
		"vagina_count":1,"double_penis":false,"sex":"female",
		"wombs":1,"lactation":0,"breasts":0.9021903256055908,
		"breastsLabel":"flat","height":141.6895679725032,
		"libido":12,"subdom":0,"hair":"magenta","ears":"furry cat",
		"bodyHair":0,"skinType":"hairless, smooth","skinColor":"pale",
		"eyeColor":"blue","tail":["flowing cat"],"description":"",
		"blood":"red","genderVoice":6,"fluids":100,"lewdness":72,
		"horns":0,"inhuman":3,"eyeCount":2,"armCount":2,"legCount":2,
		"tentacles":0,"extraEyes":0,"extraMouths":0
	}
}
'''

from typing import List
from pydantic import BaseModel

class CharacterInfo(BaseModel):
	id : int
	name : str
	cost : int
	carry : int
	affec : int
	swap : bool
	mindSex : str
	osex : str
	obreasts : int
	desiredBreasts : int
	openis : int
	ogender : int
	fit : int
	oheight : int
	comfortableHeight : int
	age : int
	appDesc : str
	fear : str
	ohair : str
	oskinColor : str
	oskinType : str
	oears : str
	oeyeColor : str
	oblood : str
	pregnantT : int
	due : int
	tentaclePreg : bool
	lastBirth : int
	switched : bool
	gestationJumps : int
	location : int

class CharacterState(BaseModel):
	apparent_age : int | float
	apparent_gender : int | float
	armCount : int
	blood : str
	bodyHair : int
	breasts : int | float
	breastsLabel : str
	description : str
	double_penis : int
	ears : str
	extraEyes : int
	extraMouths : int
	eyeColor : str
	eyeCount : int
	fluids : int
	genderVoice : int
	hair : str
	height : int | float
	horns : int
	inhuman : int
	lactation : int
	legCount : int
	lewdness : int
	libido : int
	penis_size : int
	real_age : int | float
	real_gender : int | float
	sex : str
	skinColor : str
	skinType : str
	subdom : int
	tail : list[str]
	tentacles : int
	vagina_count : int
	wombs : int

class CharacterData(BaseModel):
	character : CharacterInfo
	curses : list[str]
	state : CharacterState

class SceneData(BaseModel):
	scene_id : str
	scene_params : list
	character_data : CharacterData

class GeneratePortraitPromptResponse(BaseModel):
	positive_prompt : str
	negative_prompt : str

class GenerateImagesResponse(BaseModel):
	images : List[str]
