
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

const SIMPLE_T2I_PORTRAIT_WORKFLOW_REMOVE_BACKGROUND = {
	"5": {
		"inputs": {
			"ckpt_name": "hassakuXLPony_v13BetterEyesVersion.safetensors"
		},
		"class_type": "CheckpointLoaderSimple",
		"_meta": {
			"title": "Load Checkpoint"
		}
	},
	"9": {
		"inputs": {
			"text": "",
			"clip": [
				"5",
				1
			]
		},
		"class_type": "CLIPTextEncode",
		"_meta": {
			"title": "Positive Prompt"
		}
	},
	"10": {
		"inputs": {
			"text": "",
			"clip": [
				"5",
				1
			]
		},
		"class_type": "CLIPTextEncode",
		"_meta": {
			"title": "Negative Prompt"
		}
	},
	"11": {
		"inputs": {
			"seed": -1,
			"steps": 35,
			"cfg": 7,
			"sampler_name": "euler",
			"scheduler": "normal",
			"denoise": 1,
			"model": [
				"5",
				0
			],
			"positive": [
				"9",
				0
			],
			"negative": [
				"10",
				0
			],
			"latent_image": [
				"12",
				0
			]
		},
		"class_type": "KSampler",
		"_meta": {
			"title": "KSampler"
		}
	},
	"12": {
		"inputs": {
			"width": 1024,
			"height": 1024,
			"batch_size": 1
		},
		"class_type": "EmptyLatentImage",
		"_meta": {
			"title": "Empty Latent Image"
		}
	},
	"15": {
		"inputs": {
			"samples": [
				"11",
				0
			],
			"vae": [
				"5",
				2
			]
		},
		"class_type": "VAEDecode",
		"_meta": {
			"title": "VAE Decode"
		}
	},
	"17": {
		"inputs": {
			"threshold": 0.5,
			"torchscript_jit": "default",
			"image": [
				"15",
				0
			]
		},
		"class_type": "InspyrenetRembgAdvanced",
		"_meta": {
			"title": "Inspyrenet Rembg Advanced"
		}
	},
	"18": {
		"inputs": {
			"filename_prefix": "TRANSPARENT_",
			"images": [
				"17",
				0
			]
		},
		"class_type": "SaveImage",
		"_meta": {
			"title": "Save Image"
		}
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
	if (mc.hasCurse("Gooey")) description += "A slime person, translucent slime-skinned. ";
	if (mc.hasCurse("Crossdress Your Heart")) description += "Crossdressing as the opposite gender. ";
	if (mc.hasCurse("Lingual Leviathan")) description += "A very long tongue sticking out. ";
	if (mc.hasCurse("Massacre Manicure")) description += "Abnormally sharp and long fingernails. ";
	if (mc.hasCurse("Flower Power")) description += "Covered in flowers. ";
	if (mc.hasCurse("Cellulose")) description += "Made of living plant matter, like a dryad. ";
	if (mc.hasCurse("Wriggly Antennae")) description += "Wriggly insect antennae on forehead. ";
	if (mc.hasCurse("Carapacian")) description += "Covered in an insect-like carapace. ";
	if (mc.hasCurse("Creature of the Night")) description += "A vampire, with vampire fangs. ";
	if (mc.hasCurse("Minish-ish")) description += `Very tiny, only a few inches tall. `;
	if (mc.hasCurse("Colossal-able")) description += `Enormous, absolutely giant. `;
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
	const storeKey = "generatedImage";
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
	var prompt = staticPrompt + characterDescription;

	if (setup.customPromptPrefix != null) {
		prompt = setup.customPromptPrefix + "," + prompt
	}

	if (setup.customPromptSuffix != null) {
		prompt = prompt + "," + setup.customPromptSuffix
	}

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

setup.DEFAULT_CHECKPOINT = "hassakuXLPony_v13BetterEyesVersion";
setup.DEFAULT_LORAS = ["DallE3-magik"]
setup.DEFAULT_POSITIVE_TAGGING = ["score_9_up", "score_8_up", "score_7_up", "cowboy shot", "1girl", "solo", "source_anime", "front view"]
setup.DEFAULT_NEGATIVE_TAGGING = ["score_5_up", "score_4_up", "score_3_up", "pony", "ugly", "ugly face", "poorly drawn face", "blurry", "blurry face", "(3d)", "realistic", "muscular", "long torso", "blurry eyes", "poorly drawn eyes", "patreon", "artist name", "sd", "super deformed"]

// https://civitai.com/articles/5473/pony-cheatsheet-v2

// https://civitai.com/articles/6349/280-pony-diffusion-xl-recognized-clothing-list-booru-tags-sfw
// https://civitai.com/articles/6888/320-pony-diffusion-xl-character-hairstyles-ears-wings-and-tails-booru-tags-sfw
// https://civitai.com/articles/7579/480-pony-diffusion-xl-hats-masks-and-more-props-list-booru-tags-sfw

setup.AVAILABLE_MODELS = ["hassakuXLPony_v13BetterEyesVersion"];
setup.AVAILABLE_LORAS = ["DallE3-magik"];

setup.POSITIVE_CATEGORICAL_TAGGING = {
	"Pony Scores" : [
		"score_9_up", "score_8_up", "score_7_up", "score_6_up", "score_5_up", "score_4_up"
	],

	"Image Quality" : [
		"best_quality", "masterpiece", "hd", "4k", "8k", "extremely detailed", "intricate details", "ultra-detailed",
		"illustration", "detailed light", "hdr", "best quality", "amazing quality", "very aesthetic", "absurdres",
		"extremely detailed CG unity 8k wallpaper", "highres", "highly detailed", "soft shadow", "hard shadow",
		"strong shadow", "depth of field", "an extremely delicate and beautiful"
	],

	"Pony Source" : [
		"source_anime", "source_cartoon", "source_pony", "source_furry"
	],

	"Ratings" : [
		"rating_explicit", "rating_questionable", "rating_safe"
	],

	"Camera Angles" : [
		"top down", "birds eye view", "high angleshot", "above shot", "slightly above", "straight on", "front view",
		"hero view", "cowboy shot", "low view", "worms eye view"
	],

	"Camera Location" : [
		"extreme long shot", "long shot", "medium long shot", "medium shot", "medium close up", "close up",
		"extreme close up", "facing towards viewer", "facing away from viewer"
	],

	"Quantity" : [
		"solo", "1girl", "2girls", "3girls", "4girls", "1 girl", "2 girls", "3 girls", "4 girls",
		"multiple_girls", "1boy", "2boys", "3boys", "4boys", "1 boy", "2 boys", "3 boys", "4 boys",
		"multiple_boys"
	],

	"NSFW" : [
		"bra", "panties", "nude", "naked"
	],

	"Censor" : [
		"censored", "mosaic censorship", "out-of-frame censoring", "bar censor",
		"heart censor", "glitch censor", "shadow censor", "tape censor", "blue censor", "tail censor", "ribbon censor",
		"smoke censor", "feather censor", "soap censor", "one finger selfie challenge", "light censor"
	],

	"Curses" : [
		// TODO: hook to game curses -> in the prompt code it will output the curse prompt -> append that to the custom tagging
	],
}

setup.NEGATIVE_CATEGORICAL_TAGGING = {
	"Pony Scores" : ["score_3_up", "score_4_up", "score_5_up"],

	"Image Quality" : [
		"flat color", "lowres", "bad hands", "bad fingers", "missing fingers", "extra digit", "fewer digits",
		"worst quality", "normal quality", "jpeg artifacts", "signature", "watermark", "username", "bad feet",
		"three legs", "wrong hand", "wrong feet", "wrong fingers", "deformed leg", "abnormal", "malformed",
		"bad art", "deformed", "disfigured", "mutation", "mutated", "extra limbs", "inaccurate limb",
		"missing limb", "floating limbs", "disconnected limbs", "long neck", "long body", "mutated skeleton",
		"long skeleton", "bad proportions", "mutated hands and fingers", "poorly drawn hands", "malformed hands",
		"poorly drawn face", "poorly drawn asymmetrical eyes", "mutated face", "low quality", "distorted light",
		"low quality illustration", "blurry", "bad anatomy"
	]
}

setup.comfyUI_ClearAdvanced = function() {
	SugarCube.State.variables.advancedMenuCheckpoint = setup.DEFAULT_CHECKPOINT;
	SugarCube.State.variables.advancedMenuLORAs = new Set();
	SugarCube.State.variables.advancedMenuPositive = new Set();
	SugarCube.State.variables.advancedMenuNegative = new Set();
}

setup.comfyUI_GenerateAdvancedParameters = function() {
	var checkpoint = SugarCube.State.variables.advancedMenuCheckpoint;
	var steps = 20;
	var cfg = 7.0;
	var width = 1024;
	var height = 1024;
	var seed = (SugarCube.State.prng.seed | Math.round(Math.random() * 10_000));

	// positive
	let positive = "";

	for (let [tag, value] of Object.entries(SugarCube.State.variables.advancedMenuLORAs)) {
		if (value) {
			let lora_tag = "<lora:" + tag + ":1> ";
			positive += lora_tag;
		}
	}

	for (let [tag, value] of Object.entries(SugarCube.State.variables.advancedMenuPositive)) {
		if (value) {
			positive += tag + ",";
		}
	}

	// negative
	let negative = "";
	for (let [tag, value] of Object.entries(SugarCube.State.variables.advancedMenuNegative)) {
		if (value) {
			negative += tag + ",";
		}
	}

	// if curses is enabled, append that
	if (SugarCube.State.variables.UseMixedGameComfyUIPrompt == true) {
		const [curses_positive, curses_negative] = setup.comfyUI_GenerateCurseParameters();
		positive += "," + curses_positive
		negative += "," + curses_negative
	}

	return [positive, negative, checkpoint, steps, cfg, seed, width, height]
}

setup.comfyUI_ResetAdvanced = function() {
	// set default model
	SugarCube.State.variables.advancedMenuCheckpoint = setup.DEFAULT_CHECKPOINT;

	// set default loras
	SugarCube.State.variables.advancedMenuLORAs = new Set();
	for (let tag of Object.values(setup.DEFAULT_LORAS)) {
		SugarCube.State.variables.advancedMenuLORAs.add(tag);
	}

	SugarCube.State.variables.advancedMenuPositive = new Set();
	for (let tag of Object.values(setup.DEFAULT_POSITIVE_TAGGING)) {
		SugarCube.State.variables.advancedMenuPositive.add(tag);
	}

	SugarCube.State.variables.advancedMenuNegative = new Set();
	for (let tag of Object.values(setup.DEFAULT_NEGATIVE_TAGGING)) {
		SugarCube.State.variables.advancedMenuNegative.add(tag);
	}
}

setup.ComfyUI_GenerateAdvancedHTMLPage = function() {
	var html_text = "";

	// if it hasn't been set yet, set them all to the defaults
	if (SugarCube.State.variables.advancedMenuCheckpoint == "" || SugarCube.State.variables.advancedMenuCheckpoint == null) {
		setup.comfyUI_ResetAdvanced();
	}

	// checkpoints
	html_text += "<h2>Checkpoints</h2>";
	for (let tag of Object.values(setup.AVAILABLE_MODELS)) {
		let current_value = (SugarCube.State.variables.advancedMenuCheckpoint == tag);
		html_text += tag + ": <<checkbox \"$advancedMenuCheckpoint\" null " + tag + " " + (current_value ? "checked" : "autocheck") + ">> ";
	}
	html_text += "\n";

	// loras
	html_text += "<h2>LORAs</h2>";
	for (let tag of Object.values(setup.AVAILABLE_LORAS)) {
		let current_value = SugarCube.State.variables.advancedMenuLORAs.has(tag) == true;
		html_text += tag + ": <<checkbox \"$advancedMenuLORAs[\'" + tag + "\']\" false true " + (current_value ? "checked" : "autocheck") + ">> ";
	}
	html_text += "\n";

	// positive prompt
	html_text += "<h2>Positive Prompt</h2>";
	for (let [category, array_of_tags] of Object.entries(setup.POSITIVE_CATEGORICAL_TAGGING)) {
		html_text += "<h4>" + category + "</h4>";
		for (let tag of Object.values(array_of_tags)) {
			let current_value = SugarCube.State.variables.advancedMenuPositive.has(tag) == true;
			html_text += tag + ": <<checkbox \"$advancedMenuPositive[\'" + tag + "\']\" false true " + (current_value ? "checked" : "autocheck") + ">> ";
		}
		html_text += "\n";
	}
	html_text += "\n"

	// negative prompt
	html_text += "<h2>Negative Prompt</h2>";
	for (let [category, array_of_tags] of Object.entries(setup.NEGATIVE_CATEGORICAL_TAGGING)) {
		html_text += "<h4>" + category + "</h4>";
		for (let tag of Object.values(array_of_tags)) {
			let current_value = SugarCube.State.variables.advancedMenuNegative.has(tag) == true;
			html_text += tag + ": <<checkbox \"$advancedMenuNegative[\'" + tag + "\']\" false true " + (current_value ? "checked" : "autocheck") + ">> ";
		}
		html_text += "\n";
	}

	// curses

	return html_text;
}

const PROXY_BASE_URL = "http://127.0.0.1:12500";

setup.updateComfyUIStatus = async function() {
	const url = PROXY_BASE_URL + "/echo";

	var is_running = false;

	try {
		await fetch(url, {method: 'GET', headers: {'Origin' : 'AbyssDiver.html', 'Content-Type': 'application/json'}});
		is_running = true;
		// try display any image if any are available
		// setup.displaySavedImage().catch(() => null)
		setup.displayRecentGeneratedImage().catch(() => null)
	} catch (error) {}

	const notificationElement = document.getElementById('comfyui-enabled');
	notificationElement.textContent = is_running ? "ComfyUI is currently running." : "ComfyUI is NOT currently running."
	notificationElement.style.color = is_running ? "green" : "red"
}

setup.comfyUI_InvokeGenerator = async function(url, payload) {
	// console.log(url, JSON.stringify(payload));

	var response = null;
	try {
		response = await fetch(url, {
			method: 'POST',
			headers: {'Origin' : 'AbyssDiver.html', 'Content-Type': 'application/json'},
			body: JSON.stringify(payload)
		});
	} catch (error) {
		throw new Error('Failed to connect to Proxy. Please check your Proxy and ensure the server is running.');
	}

	if (!response.ok) {
		throw new Error('Failed to connect to Proxy. Please check your Proxy and ensure the server is running.');
	}

	const data = await response.json();
	// Debugging: Inspect the structure of the response
	// console.log(data);
	// Return the data for further processing
	return data;
}

setup.comfyUI_PrepareCharacterData = function() {
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
	delete mc_internal_state_clone.events; // don't need the events to be sent
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

setup.comfyUI_GenerateCurseParameters = function() {
	const characterData = setup.comfyUI_PrepareCharacterData();

	let positive = "";
	let negative = "";

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

	if (characterData.state.sex === "female" && !characterData.curses.includes("ClothingRestrictionA")) {
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

	positive += `${characterData.state.breastsLabel} breasts,`; // TODO: change to relative sizes (flat, small, large, huge, enormous)

	return [positive, negative];
}

// TODO: ItsTheTwin is doing this (temporary code)
setup.comfyUI_GenerateStandardParameters = function() {
	let [positive, negative] = setup.comfyUI_GenerateCurseParameters();

	positive += PREFIX_POSITIVE_PROMPT + " ,solo,portrait,upper_body,plain dark background," + positive;
	negative = PREFIX_NEGATIVE_PROMPT + negative;

	let checkpoint = "hassakuXLPony_v13BetterEyesVersion.safetensors";
	let steps = 20;
	let cfg = 7.0;
	let seed = (SugarCube.State.prng.seed | Math.round(Math.random() * 10_000));
	let width = 1024;
	let height = 1024;
	return [positive, negative, checkpoint, steps, cfg, seed, width, height];
}

setup.comfyUI_GeneratePortraitWorkflow = async function() {

	if (SugarCube.State.variables.UseAdvancedComfyUIPrompt == true) {
		var [positive, negative, checkpoint, steps, cfg, seed, width, height] = setup.comfyUI_GenerateAdvancedParameters();
	} else {
		var [positive, negative, checkpoint, steps, cfg, seed, width, height] = setup.comfyUI_GenerateStandardParameters();
	}


	// clone workflow so it can be edited
	var workflow = null;
	if (SugarCube.State.variables.DisableTransparentPortraitBackground == true) {
		workflow = JSON.parse(JSON.stringify(SIMPLE_T2I_PORTRAIT_WORKFLOW));
	} else {
		workflow = JSON.parse(JSON.stringify(SIMPLE_T2I_PORTRAIT_WORKFLOW_REMOVE_BACKGROUND));
	}

	if (setup.customPromptPrefix != null) {
		positive = setup.customPromptPrefix + "," + positive
	}

	if (setup.customPromptSuffix != null) {
		positive = positive + "," + setup.customPromptSuffix
	}

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

// PROXY_BASE_URL/generate_image
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
	const url = PROXY_BASE_URL + "/generate_workflow"

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

	var storeKey = "generatedImage";
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
