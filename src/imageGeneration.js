
/**
 * @type {object}
 * @property {Object.<string, any>} variables
 */
State

/**
 * @callback variablesGetter
 * @returns {Object.<string, any>}
 */
/**
 * @type {variablesGetter}
 */
variables

// This JSDoc declaration defines the extensions we add to setup in this file
/**
 * @typedef SugarCubeSetupObject
 * @extends SugarCubeSetupObject
 * @property {string} Path
 * @property {string} ImagePath
 * @property {string} SoundPath
 * @property {int} never
 * @property {string[]} flaskLabels
 * @property {function} curse
 * @property {function} curses
 * @property {function} item
 * @property {function} items
 * @property {function} relic
 * @property {function} relics
 * @property {function} companion
 * @property {function} companions
 * @property {function} sellValue
 * @property {function} modAffection
 * @property {function} activeCurseCount
 * @property {number} carriedWeight
 * @property {boolean} haveCuttingTool
 * @property {boolean} haveSword
 * @property {boolean} haveScubaGear
 * @property {boolean} haveSmartphoneRegular
 * @property {boolean} haveSmartphoneAI
 * @property {boolean} haveSmartphone
 * @property {boolean} haveUnlimitedLightSource
 * @property {boolean} havePotentialLightSource
 * @property {boolean} haveTravelLightSource
 * @property {boolean} haveNotepad
 * @property {boolean} haveRope
 * @property {boolean} haveHealing
 * @property {boolean} haveColdProtection
 * @property {boolean} haveHeatProtection
 * @property {function} sellRelic
 * @property {function} unsellRelic
 * @property {function} loseRelic
 * @property {boolean} passingTime
 * @property {function} startPassingTime
 * @property {function} stopPassingTime
 * @property {function} isPregnant
 * @property {function} setConsideredPregnant
 * @property {function} setNotPregnant
 * @property {function} dueDate
 * @property {function} daysConsideredPregnant
 * @property {function} daysUntilDue
 * @property {function} willingCurses
 * @property {function} returnRelic
 * @property {function} getCurseSets
 * @property {function} getUserCurseSets
 * @property {function} setUserCurseSets
 * @property {function} addUserCurseSet
 */

/*
	===============================================
	WORKFLOWS
	===============================================
*/

const SIMPLE_T2I_PORTRAIT_WORKFLOW = {
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
			"seed": 0,
			"steps": 35,
			"cfg": 7,
			"sampler_name": "euler",
			"scheduler": "normal",
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

const SCENE_GENERATION_WITH_MIDAS_WORKFLOW = {
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

const SCENE_GENERATION_WITHOUT_MIDAS_WORKFLOW = {
	"1": {
		"inputs": {"image": "00007-4032934194.png","upload": "image"},
		"class_type": "LoadImage",
		"_meta": {"title": "Load Image"}
	},
	"3": {
		"inputs": {"images": ["1",0]},
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
			"image": ["1",0]
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

/*
	===============================================
	OPENAI DALLE GENERATOR
	===============================================
*/

setup.evaluateDalleCharacterDescription = function(mc) {
	let description = ``;
	if (mc.sex === "male") {
		description += "The character is a male. ";
	} else if (mc.sex === "female") {
		description += "The character is a female. ";
	} else {
		description += "";
	};

	description += `${mc.hair} colored hair. `;
	description += `${mc.eyeColor} colored eyes. `;
	description += `${mc.skinType} ${mc.skinColor} colored skin. `;

	if (mc.ears != "normal human") description += `${mc.ears} ears. `;

	if (mc.appAge < 15) {
		description += `A child. `;
	} else if (mc.appAge < 20) {
		description += `A teenager. `;
	} else if (mc.appAge < 30) {
		description += `A young adult. `;
	} else if (mc.appAge < 45) {
		description += `An adult. `;
	} else if (mc.appAge < 55) {
		description += `A middle-aged adult. `;
	} else if (mc.appAge < 65) {
		description += `And older adult. `;
	} else {
		description += `And elderly adult. `;
	}

	if (mc.subdom > 0) {
		description += "with a very shy body posture. ";
	} else if (mc.subdom < 0) {
		description += "with a very strong body posture. ";
	}

	if (mc.hasCurse("Horny")) {
		// Ensure these variables are defined
		let hornCount = State.variables.hornCount || 0;
		let hornAdjective = State.variables.hornAdjective || "";
		let hornVariation = State.variables.hornVariation || "";
		description += `with ${(hornCount === 1) ? "a" : "two"} noticeable ${hornAdjective} ${hornVariation} horn${(hornCount > 1) ? "s" : ""}. `;
	}

	// Gender and physical appearance
	switch(mc.gender) {
		case 1: description += "A masculine man. "; break;
		case 2: description += "A feminine man (twink, femboy). "; break;
		case 3: description += "A very androgynous man. "; break;
		case 4: description += "A very androgynous woman. "; break;
		case 5: description += "A masculine woman (tomboy). "; break;
		case 6: description += "A feminine woman. "; break;
	}

	// Breast size
	if (mc.breastsCor < 1 && mc.vagina === 0) {
		description += "";
	} else if (mc.breastsCor < 1 && mc.vagina === 1) {
		description += "with a totally flat chest. ";
	} else if (mc.breastsCor < 6) {
		description += "";
	} else {
		description += "with an abnormally large chest. ";
	}

	// Additional conditions
	if (mc.dollevent2) description += "Wearing a tattered pink dress, resembling a child's doll. ";

	// Pregnancy
	const pregnantDays = setup.daysConsideredPregnant(mc);
	if (120 <= pregnantDays && pregnantDays < 180) {
		description += mc.menFirstCycle ? "A noticeable pregnancy bump. " : "A small pregnancy bump. ";
	} else if (180 <= pregnantDays && pregnantDays < 240) {
		description += "A large pregnancy bump. ";
	} else if (pregnantDays >= 240 && setup.daysUntilDue(mc) > 0) {
		description += "A huge pregnancy belly. ";
	}

	// Curses and conditions
	if (mc.hasCurse("Freckle Speckle")) description += "Many freckles. ";
	if (mc.hasCurse("20/20000000")) description += "Wearing thick glasses. ";
	if (mc.hasCurse("Gooey")) description += "A slime person, transluscent slime-skinned. ";
	if (mc.hasCurse("Crossdress Your Heart")) description += "Crossdressing as the opposite gender. ";
	if (mc.hasCurse("Lingual Leviathan")) description += "A very long tongue sticking out. ";
	if (mc.hasCurse("Massacre Manicure")) description += "Abnormally sharp and long fingernails. ";
	if (mc.hasCurse("Flower Power")) description += "Covered in flowers. ";
	if (mc.hasCurse("Cellulose")) description += "Made of living plant matter, like a dryad. ";
	if (mc.hasCurse("Wriggly Antennae")) description += "Wriggly insect antennae on forehead. ";
	if (mc.hasCurse("Carapacian")) description += "Covered in an insect-like carapac. ";
	if (mc.hasCurse("Creature of the Night")) description += "A vampire, with vampire fangs. ";
	if (mc.hasCurse("Minish-ish")) description += `Very tiny, only a few inches tall. `;
	if (mc.hasCurse("Colossal-able")) description += `Enormous, asbolutely giant. `;
	if (mc.hasCurse("Seafolk")) description += "A merfolk with a merfolk tail. ";
	if (mc.hasCurse("Tickly Tentacles")) description += `${mc.tentacles} squirming tentacles growing from their body. `;
	if (mc.hasCurse("Eye-scream")) description += `${mc.extraEyes} extra eyes on their body. `;
	if (mc.hasCurse("A Mouthful")) description += `${mc.extraMouths} extra mouths on their body. `;
	if (mc.hasCurse("Below the Veil")) description += "A strange, eldritch entity that seems very creepy and *wrong* in subtle ways. ";
	description += "\n"+ SugarCube.setup.manualDesc;

	return description;
};

setup.openAI_InvokeDalleGenerator = async function(prompt) {
	const apiKey = settings.OpenAIAPIKey;

	const headers = {
		'Content-Type': 'application/json',
		'Authorization': `Bearer ${apiKey}`
	}

	const body = JSON.stringify({
		model: 'dall-e-3',
		prompt: prompt,
		n: 1,
		size: "1024x1024",
		response_format: "b64_json"
	})

	const response = await fetch('https://api.openai.com/v1/images/generations', {
		method: 'POST',
		headers: headers,
		body: body
	});

	// check if we connected to OpenAI
	if (!response.ok) {
		is_generation_busy = false;
		throw new Error('Failed to connect to OpenAI. Please check your API key and network connection and try again. If those are both correct, this may be due to a content policy error from OpenAI.');
	}

	// check if any image was given from Dalle
	const data = await response.json();
	// console.log(data);

	if (!data.data || data.data.length == 0) {
		is_generation_busy = false;
		console.error('No images returned from Dalle:', data);
		throw new Error('No images returned from server. This is likely due to a content policy error or server error from OpenAI.');
	}

	// once we receive the image, save it as the player portrait
	const storeKey = "playerPortrait";
	const b64Image = data.data[0].b64_json;
	console.log("Base64 Data Length: ", b64Image.length);

	// now save it in the local storage
	try {
		setup.storeImage(storeKey, b64Image);
		console.log('Image successfully stored.');
	} catch(error) {
		console.error('Failed to store image due to error:', error);
	}
}

setup.openAI_GenerateDallePortrait = async function() {
	if (is_generation_busy) {
		return;
	}
	is_generation_busy = true;

	// Notification element
	const notificationElement = document.getElementById('notification');

	// Static part of the prompt
	let staticPrompt = "Create an anime-inspired digital painting of a single character with each of the following traits. You must keep in mind every physical trait below. You must use an *anime-inspired digital painting* style. The character is an adventurer and the background of the scene is the Abyss from MiA. Do NOT use the word character in the final prompt.\n\nCharacter traits:\n";

	// Dynamically generated character description
	let characterDescription = setup.evaluateDalleCharacterDescription(State.variables.mc); // Assuming $mc is stored in State.variables.mc

	// Concatenate the static prompt with the dynamic description
	const prompt = staticPrompt + characterDescription;

	try {
		await setup.openAI_InvokeDalleGenerator(prompt);
		if (notificationElement != null) {
			notificationElement.style.display = 'hidden';
		}
	} catch (error) {
		console.error('Error generating image:', error);
		if (notificationElement != null) {
			notificationElement.style.display = 'block';
			notificationElement.textContent = 'Error generating image: ' + error.message + (error.response ? (await error.response.json()).error : ' No additional error information from OpenAI.');
		}
	}

	is_generation_busy = false;
}

/*
	===============================================
	(LOCAL) COMFYUI GENERATOR
	===============================================
*/

setup.comfyUI_InvokeGenerator = async function(url, payload) {
	// console.log(url, JSON.stringify(payload));
	const response = await fetch(url, {
		method: 'POST',
		headers: {'Origin' : 'AbyssDiver.html', 'Content-Type': 'application/json'},
		body: JSON.stringify(payload)
	});

	if (!response.ok) {
		throw new Error('Failed to connect to Proxy. Please check your Proxy and ensure the server is running.');
	}

	const data = await response.json();
	// Debugging: Inspect the structure of the response
	// console.log(data);
	// Return the data for further processing
	return data;
}

setup.comfyUI_PrepareCharacterData = async function() {
	// get the character curses
	const mc_curses = State.variables.mc.curses; // property: getter
	const mc_curse_names = mc_curses.map(curse => curse.name);

	// get special character data
	const mc_state = {
		'real_age' : State.variables.mc.realAge,
		'apparent_age' : State.variables.mc.appAge,
		'real_gender' : State.variables.mc.gender,
		'apparent_gender' : State.variables.mc.appGender,
		'penis_size' : State.variables.mc.penisCor,
		'vagina_count' : State.variables.mc.vagina,
		'double_penis' : State.variables.mc.doublePenis,
		'sex' : State.variables.mc.sex,
		'wombs' : State.variables.mc.womb,
		'lactation' : State.variables.mc.lactation,
		'breasts' : State.variables.mc.breastsCor,
		'breastsLabel' : State.variables.mc.breastsLabel,
		'height' : State.variables.mc.heightCor,
		'libido' : State.variables.mc.libido,
		'subdom' : State.variables.mc.subdom,

		'hair' : State.variables.mc.hair,
		'ears' : State.variables.mc.ears,
		'bodyHair' : State.variables.mc.bodyHair,
		'skinType' : State.variables.mc.skinType,
		'skinColor' : State.variables.mc.skinColor,
		'eyeColor' : State.variables.mc.eyeColor,
		'tail' : State.variables.mc.tail,
		'description' : State.variables.mc.desc,
		'blood' : State.variables.mc.blood,
		'genderVoice' : State.variables.mc.genderVoice,
		'fluids' : State.variables.mc.fluids,
		'lewdness' : State.variables.mc.lewdness,
		'horns' : State.variables.mc.horns,
		'inhuman' : State.variables.mc.inhuman,
		'eyeCount' : State.variables.mc.eyeCount,
		'armCount' : State.variables.mc.armCount,
		'legCount' : State.variables.mc.legCount,
		'tentacles' : State.variables.mc.tentacles,
		'extraEyes' : State.variables.mc.extraEyes,
		'extraMouths' : State.variables.mc.extraMouths
	};
	// console.log(mc_state);

	// get the character internal state (deep clone it)
	const mc_internal_state_clone = Object.fromEntries(Object.entries(State.variables.mc._internalState()));
	delete mc_internal_state_clone.image; // don't need the image to be sent
	delete mc_internal_state_clone.events; // dont need the events to be sent
	delete mc_internal_state_clone.imageIcon; // don't need the image icon to be sent

	// payload to send to proxy/comfyui
	const payload = {'character' : mc_internal_state_clone, 'curses' : mc_curse_names, 'state' : mc_state,};
	return payload;
}

const PREFIX_POSITIVE_PROMPT = "score_9, score_8_up, score_7_up, masterpiece, best quality, cowboy shot, 1girl, solo, source_anime, front view <lora:Dalle3_AnimeStyle_PONY_Lora:1>";
const PREFIX_NEGATIVE_PROMPT = "score_5, score_4, pony, ugly, ugly face, poorly drawn face, blurry, blurry face, (3d), realistic, muscular, long torso, blurry eyes, poorly drawn eyes, patreon, artist name, (sd, super deformed),";
const BODY_FITNESS = ["fragile body", "weak body", "average body", "fit body", "very fit body",];
const HEIGHT_RANGES = [ ["dwarf", 150], ["midget", 160], ["short", 170], ["", 183], ["tall", 195] ];
const PENIS_SIZES = ["small penis", "below average penis", "average penis", "large penis", "huge penis",];

function heightToRangedValue(height) {
	for (const [label, maxHeight] of HEIGHT_RANGES) {
		if (height < maxHeight) {
			return label;
		}
	}
	return HEIGHT_RANGES[HEIGHT_RANGES.length-1][0];
}

// TODO: ItsTheTwin is doing this (temporary code)
setup.comfyUI_GeneratePositiveNegative = async function() {
	const characterData = await setup.comfyUI_PrepareCharacterData();

	var positive = PREFIX_POSITIVE_PROMPT;
	positive += ",solo,portrait,upper_body,plain dark background,";

	var negative = PREFIX_NEGATIVE_PROMPT;

	positive += `${characterData.state.sex},`;
	positive += `${Math.max(characterData.state.apparent_age, 21)} years old,`;
	positive += BODY_FITNESS[Math.max(Math.min(characterData.character.fit + 2, 4), 0)] + ",";
	positive += `${heightToRangedValue(characterData.state.height)},`;
	positive += `${characterData.state.hair} hair,`;
	for (const tail of characterData.state.tail) {
		positive += `${characterData.state.hair} ${tail} tail,`;
	}
	positive += `${characterData.state.hair} ${characterData.state.ears} ears,`;

	// CreatureOfTheNight -> Vampire
	if (characterData.curses.includes("CreatureOfTheNight")) {
		positive += "vampire,fangs,red eyes,glowing eyes,pale skin,";
	} else {
		positive += `${characterData.state.eyeColor} eyes,`;
		positive += `${characterData.state.skinColor} skin,`;
	}

	if (characterData.curses.includes("WrigglyAntennae")) {
		positive += "pink antennae,";
	}
	if (characterData.curses.includes("Megadontia")) {
		positive += "sharp teeth,";
	}
	if (characterData.curses.includes("FreckleSpeckle")) {
		positive += "freckles,";
	}
	if (characterData.curses.includes("KnifeEar")) {
		positive += "pointy ears,";
	}
	if (characterData.curses.includes("Horny")) {
		positive += "succubus horns,";
	}
	if (characterData.curses.includes("DrawingSpades")) {
		positive += "spade tail,";
	}

	if (!characterData.curses.includes("ClothingRestrictionA")) {
		positive += "earrings,";
	}

	if (!characterData.curses.includes("ClothingRestrictionC")) {
		positive += "adventurer,leather armor,";
	}

	if (characterData.curses.includes("ClothingRestrictionC")) {
		if (characterData.curses.includes("ClothingRestrictionB")) {
			positive += "nude,";
		} else {
			if (characterData.state.sex === "female") {
				positive += "bra,panties,";
			} else {
				positive += "underwear,shirtless,no pants,small penis bulge,";
			}
		}

		if (characterData.curses.includes("ClothingRestrictionC") && characterData.curses.includes("ClothingRestrictionB")) {
			// NUDE
			if (characterData.curses.includes("Null")) {
				// null curse
				positive += "smooth featureless body, no genitalia, soft abstract body aesthetic without explicit details,";
			} else {
				// sex-specific
				if (characterData.state.sex === "female") {
					if (characterData.curses.includes("TattooTally")) {
						positive += "succubus tattoo,";
					}
					if (characterData.curses.includes("Leaky")) {
						positive += "pussy juice,";
					}
				} else {
					if (characterData.curses.includes("TattooTally")) {
						positive += "incubus tattoo,";
					}
					if (characterData.curses.includes("Leaky")) {
						positive += "pre-ejaculation,";
					}
				}

				// lactation (both M/F)
				let lactation = 0;
				if (characterData.curses.includes("LactationRejuvenationA")) {
					lactation += 1;
				}
				if (characterData.curses.includes("LactationRejuvenationB")) {
					lactation += 1;
				}

				if (lactation === 2) {
					positive += "milk,lactating,lactation,";
				} else if (lactation === 1) {
					positive += "dripping lactation,";
				}

				if (characterData.state.penis_size > 0) {
					positive += PENIS_SIZES[characterData.state.penis_size-1] + ",";
				}
			}
		}
	}

	positive += `${characterData.state.breastsLabel} breasts,`;

	return [positive, negative];
}

setup.comfyUI_GeneratePortraitWorkflow = async function() {
	const checkpoint = "PonyV6HassakuXLHentai.safetensors";
	const steps = 20;
	const cfg = 7.0;
	const seed = 0;
	const width = 1024;
	const height = 1024;

	const [positive, negative] = await setup.comfyUI_GeneratePositiveNegative();

	// clone workflow so it can be edited
	var workflow = JSON.parse(JSON.stringify(SIMPLE_T2I_PORTRAIT_WORKFLOW));

	workflow["5"]["inputs"]["ckpt_name"] = checkpoint
	workflow["9"]["inputs"]["text"] = positive
	workflow["10"]["inputs"]["text"] = negative
	workflow["11"]["inputs"]["steps"] = steps
	workflow["11"]["inputs"]["cfg"] = cfg
	workflow["11"]["inputs"]["seed"] = seed
	workflow["12"]["inputs"]["width"] = width
	workflow["12"]["inputs"]["height"] = height

	return workflow;
}

// http://127.0.0.1:8000/generate_image
var is_generation_busy = false;
var last_workflow = null;
setup.comfyUI_GeneratePortrait = async function() {
	const notificationElement = document.getElementById('notification');

	if (is_generation_busy) {
		console.log("generation busy");
		notificationElement.style.display = "block";
		notificationElement.textContent = "An image is already being generated.";
		return;
	}
	is_generation_busy = true;

	notificationElement.style.display = "none";

	// data to be sent to comfyui
	const url = "http://127.0.0.1:8000/generate_workflow"

	// log outputted workflow
	// console.log(workflow);

	// request to the proxy to generate the portrait
	let data = null;
	try {
		const workflow = await setup.comfyUI_GeneratePortraitWorkflow();
		// if (last_workflow == JSON.stringify(workflow)) {
		// 	is_generation_busy = false;
		// 	return; // already the same
		// }
		// workflow was updated
		last_workflow = JSON.stringify(workflow);
		data = await setup.comfyUI_InvokeGenerator(url, workflow);
	} catch (error) {
		console.error('Unable to invoke ComfyUI generator: ', error);
		is_generation_busy = false;
		notificationElement.style.display = "block";
		notificationElement.textContent = "Unable to contact the ComfyUI proxy. Make sure the Python code is running! Check the one-click installer terminal. " + error;
		return;
	}

	// console.log(data);

	// check if we actually received any images
	if (data.images == null || data.images.length == 0) {
		console.error('No images returned from server. This might be due to an issue with the Stable Diffusion model or the server.');
		is_generation_busy = false;
		notificationElement.style.display = "block";
		notificationElement.textContent = "No images were returned from the proxy! Is ComfyUI running? Check the one-click installer terminal.";
		return;
	}

	// once we receive the image, save it as the player portrait
	is_generation_busy = false;

	var storeKey = "playerPortrait";
	var b64Image = data.images[0];
	console.log("Base64 Data Length: ", b64Image.length);
	try {
		setup.storeImage(storeKey, b64Image);
		console.log('Image successfully stored.');
	} catch(error) {
		console.error('Failed to store image due to error:', error);
		notificationElement.style.display = "block";
		throw new Error('Failed to store image due to error: ' + error);
	}
}

/*
	// TODO: future update (also edit return to be the raise Error)

	setup.comfyUI_PrepareSceneData = async function(scene_id, scene_params) {
		return {'scene_id' : scene_id, 'scene_params' : scene_params}
	}

	// http://127.0.0.1:8000/generate_scene
	setup.comfyUI_GenerateCharacterScene = async function(scene_id, scene_params) {
		if (is_generation_busy) {
			return;
		}
		is_generation_busy = true;

		// notification element
		const notificationElement = document.getElementById('notification');

		// data to be sent to comfyui
		const url = "http://127.0.0.1:8000/generate_scene";

		// prepare Payload
		const payload = {'character' : setup.comfyUI_PrepareCharacterData(), 'scene' : setup.comfyUI_PrepareSceneData(scene_id, scene_params)}

		// inspect payload
		console.log(payload);

		// request to the proxy to generate the portrait
		let data = null;
		try {
			data = await setup.comfyUI_InvokeGenerator(url, {'character' : payload});
		} catch (error) {
			console.error('Unable to invoke ComfyUI generator.');
			is_generation_busy = false;
			return;
		}

		// check if we actually received any images
		if (data.images == null || data.images.length == 0) {
			console.error('No images returned from server. This might be due to an issue with the proxy server or ComfyUI!');
			notificationElement.textContent = 'Error generating image: ' + error.message + (error.response ? (await error.response.json()).error : 'No additional error information from OpenAI.');
			notificationElement.style.display = 'block';
			is_generation_busy = false;
			return;
		}

		// once we receive the images, save it under the key
		const storeKey = scene_id;
		const b64Images = data.images; // Assuming the images are returned as base64 strings
		console.log("Base64 Data Length: ", b64Images.reduce((sum, str) => sum + str.length, 0));
		setup.storeImage(storeKey, b64Images)
			.then(() => console.log('Image successfully stored.'))
			.finally(() => is_generation_busy)
			.catch((error) => console.error('Failed to store image:', error));
	}
*/
