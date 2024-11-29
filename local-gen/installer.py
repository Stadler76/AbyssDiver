
'''
Windows:
1. git clone ComfyUI
2. Python venv
3. Install requirements
4. Download custom_nodes
5. Install custom_nodes requirements to python_embeded
6. Download Checkpoints to models/checkpoints & models/loras
7. Run

Linux/Mac:
1. Install MiniConda
2. Create anaconda environment for Python 3.11 (torch-directml)
3. git clone ComfyUI
4. Install requirements.txt
5. Download custom_nodes
6. Install custom_nodes requirements.txt
7. Download Checkpoints to models/checkpoints & models/loras
8. Run

Note:
NVIDIA Cuda uses ComfyUI base
AMD RomC uses repository 'patientx/ComfyUI-Zluda'
'''

from pathlib import Path

import os
import platform
import subprocess
import threading
import logging
import time

def get_installed_python() -> str:
	status = os.system("py --version")
	if status == 0:
		return "py"
	status = os.system("python --version")
	if status == 0:
		return "python"
	status = os.system("python3 --version")
	if status == 0:
		return "python3"
	raise Exception("No python version is installed - please install python. Prefer version 3.10.X or 3.11.X.")

restart_script : bool = False

try:
	import requests
except:
	print("requests is not installed!")
	os.system(f"{get_installed_python()} -m pip install requests")
	restart_script = True

try:
	from tqdm import tqdm
except:
	print("tqdm is not installed!")
	os.system(f"{get_installed_python()} -m pip install tqdm")
	restart_script = True

if restart_script is True:
	print("The script needs to be restarted as new packages were installed.")
	print("Press enter to continue...")
	input("")
	exit()

COMFY_UI_DEFAULT_REPOSITORY_URL = "https://github.com/comfyanonymous/ComfyUI"

COMFYUI_CUSTOM_NODES : list[str] = ["https://github.com/ltdrdata/ComfyUI-Manager", "https://github.com/john-mnz/ComfyUI-Inspyrenet-Rembg"]
# CIVITAI_CHECKPOINTS_TO_DOWNLOAD : dict[str, str] = {"hassakuHentaiModel_v13.safetensors" : "https://civitai.com/api/download/models/106922?type=Model&format=SafeTensor&size=pruned&fp=fp16"}
# CIVITAI_LORAS_TO_DOWNLOAD : dict[str, str] = {"midjourneyanime.safetensors" : "https://civitai.com/api/download/models/361041?type=Model&format=SafeTensor"}
HUGGINGFACE_CHECKPOINTS_TO_DOWNLOAD : dict[str, str] = {"hassakuXLPony_v13BetterEyesVersion.safetensors" : "https://huggingface.co/FloricSpacer/AbyssDiverModels/resolve/main/hassakuXLPony_v13BetterEyesVersion.safetensors?download=true"}
HUGGINGFACE_LORAS_TO_DOWNLOAD : dict[str, str] = {"DallE3-magik.safetensors" : "https://huggingface.co/FloricSpacer/AbyssDiverModels/resolve/main/DallE3-magik.safetensors?download=true"}

CUSTOM_COMMAND_LINE_ARGS_FOR_COMFYUI : list[str] = [] # custom arguments to pass to comfyui

def assert_path_length_limit() -> None:
	"""Check how long the path is for the local-gen folder."""
	current_path : str = Path(os.path.abspath(os.getcwd())).as_posix()
	path_length : int = len(current_path) + 70 # 70 being approx submodules of ComfyUI
	print(f"Current path: {current_path}")
	print(f"Path length: {path_length} characters")
	if path_length > 260:
		print("Warning: Path length exceeds the Windows path limit of 260 characters. Please move the abyss diver game folder elsewhere.")
		print("Press enter to continue...")
		input("")
		exit()
	if path_length > 240:
		print("Warning: Path length is close to the Windows path limit. Please move the abyss diver game folder elsewhere.")
		print("Press enter to continue...")
		input("")
		exit()
	print("Path length is within safe limits. The installer will continue.")

def download_file(url: str, filepath: str, chunk_size: int = 64) -> None:
	response = requests.get(url, stream=True) # type: ignore
	response.raise_for_status()  # Raise an error for bad status codes
	total_size = int(response.headers.get('content-length', 0))
	progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, desc=filepath.split('/')[-1]) # type: ignore
	with open(filepath, 'wb') as file:
		for chunk in response.iter_content(chunk_size=chunk_size * 1024):
			file.write(chunk)
			progress_bar.update(len(chunk))
	progress_bar.close()
	print(f"File downloaded to {filepath}")

def run_command(command: str, shell: bool = False) -> tuple[int, str]:
	print('RUNNING COMMAND:')
	print(command)
	print('=' * 10)

	try:
		process = subprocess.Popen(
			command,
			shell=shell,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			text=True,
			bufsize=1
		)

		stdout_var : str = ""

		def stream_reader(pipe, log_level):
			nonlocal stdout_var
			"""Reads from a pipe and logs each line at the given log level."""
			with pipe:
				for line in iter(pipe.readline, ''):
					print(log_level, line.strip())
					stdout_var += line.strip()

		# Use threads to prevent blocking
		stdout_thread = threading.Thread(target=stream_reader, args=(process.stdout, logging.INFO))
		stderr_thread = threading.Thread(target=stream_reader, args=(process.stderr, logging.ERROR))

		stdout_thread.start()
		stderr_thread.start()

		# Wait for the process and threads to complete
		process.wait()
		stdout_thread.join()
		stderr_thread.join()

		status_code = process.returncode
		if status_code == 0:
			print(f"Command succeeded: {command}")
		else:
			print(f"Command failed with code {status_code}: {command}")

		return status_code, stdout_var
	except Exception as e:
		print(f"Command execution exception: {command}")
		print(f"Exception details: {e}")
		return -1, str(e)

def ask_user_for_gpu_device() -> int:
	if input("Are you using a NVIDIA graphics card? (y/n)") == "y":
		return 1 # NVIDIA cuda

	if input("Are you using a AMD graphics card? (y/n)") == "y":
		print("AMD is not supported at the moment. Using CPU instead.")
		return 0 # AMD

	if input("Are you using a Intel graphics card? (y/n)") == "y":
		print("Intel is not supported at the moment. Using CPU instead.")
		return 0 # Intel

	print("Due to no device being supported, CPU will automatically be selected.")
	return 0

def comfy_ui_windows(storage_directory : str) -> None:
	"""Install ComfyUI on Windows"""

	# git clone ComfyUI if not found
	comfyui_directory = Path(os.path.join(storage_directory, "ComfyUI")).as_posix()
	print(f'ComfyUI install directory: {comfyui_directory}')
	if os.path.exists(comfyui_directory) is False:
		print("Attempting to clone ComfyUI to the directory.")
		previous_directory = os.getcwd()
		os.chdir(storage_directory)
		status = os.system("git clone https://github.com/comfyanonymous/ComfyUI")
		assert status == 0, "git clone has failed - check if you have git installed."
		os.chdir(previous_directory)

	assert os.path.exists(comfyui_directory), "ComfyUI failed to be cloned."

	# Setup the virtual environment
	python_command : str = get_installed_python()
	venv_directory : str = Path(os.path.join(comfyui_directory, "venv")).as_posix()
	activate_bat_filepath : str = Path(os.path.join(venv_directory, "Scripts", "activate.bat")).as_posix()
	if os.path.exists(activate_bat_filepath) is False:
		status = os.system(f"{python_command} -m venv \"{venv_directory}\"")
		assert status == 0, "Failed to create a virtual environment in the ComfyUI folder."

	# Activate the venv enviornment once for a test
	status = os.system(f"call \"{activate_bat_filepath}\"")
	assert status == 0, "Failed to activate the virtual environment."

	# install ComfyUI/requirements.txt
	requirements_file = Path(os.path.join(comfyui_directory, "requirements.txt")).as_posix()
	status = os.system(f"call \"{activate_bat_filepath}\" && {python_command} -m pip install -r \"{requirements_file}\"")
	assert status == 0, "Failed to install the ComfyUI packages."

	# git clone custom_nodes
	custom_nodes_folder = Path(os.path.join(comfyui_directory, "custom_nodes")).as_posix()
	previous_directory = os.getcwd()
	os.chdir(custom_nodes_folder)
	for node_repository_url in COMFYUI_CUSTOM_NODES:
		print(f'Cloning: {node_repository_url}')
		_ = os.system(f"git clone {node_repository_url}")
	os.chdir(previous_directory)

	# pip install custom_nodes requirements.txt
	for folder_name in os.listdir(custom_nodes_folder):
		if os.path.isdir(Path(os.path.join(custom_nodes_folder, folder_name)).as_posix()) is False:
			continue # not a folder
		folder_requirements = Path(os.path.join(custom_nodes_folder, folder_name, "requirements.txt")).as_posix()
		print(folder_requirements)
		if os.path.exists(folder_requirements) is False:
			continue # cannot find requirements.txt
		status = os.system(f"call \"{activate_bat_filepath}\" && {python_command} -m pip install -r \"{folder_requirements}\"")
		assert status == 0, f"Failed to install the {folder_name} packages."

	# download all checkpoint models
	models_folder = Path(os.path.join(comfyui_directory, "models")).as_posix()
	for filename, checkpoint_url in HUGGINGFACE_CHECKPOINTS_TO_DOWNLOAD.items():
		checkpoint_filepath = Path(os.path.join(models_folder, "checkpoints", filename)).as_posix()
		if os.path.exists(checkpoint_filepath) is True:
			print(f"Checkpoint {filename} is already installed.")
			continue
		try:
			download_file(checkpoint_url, checkpoint_filepath)
		except Exception as e:
			print(f'Failed to download checkpoint {filename}.')
			print(e)
			assert False, f"Failed to download the {filename} checkpoint file."

	# download all lora models
	models_folder = Path(os.path.join(comfyui_directory, "models")).as_posix()
	for filename, lora_url in HUGGINGFACE_LORAS_TO_DOWNLOAD.items():
		lora_filepath = Path(os.path.join(models_folder, "loras", filename)).as_posix()
		if os.path.exists(lora_filepath) is True:
			print(f"Checkpoint {filename} is already installed.")
			continue
		try:
			download_file(lora_url, lora_filepath)
		except Exception as e:
			print(f'Failed to download lora {filename}.')
			print(e)
			assert False, f"Failed to download the {filename} lora file."

	arguments = ["--windows-standalone-build", "--disable-auto-launch"]

	# TODO: AMD / INTEL
	device_n = ask_user_for_gpu_device()
	if device_n == 0:
		arguments.append("--cpu")
	elif device_n == 1:
		try:
			import torch
			assert torch.cuda.is_available(), "Cuda is not available."
		except:
			print("Installing torch torchaudio and torchvision with CUDA acceleration.")
			print("Please open a new terminal, type 'nvidia-smi' and find the CUDA Version: XX.X.")
			print("If nvidia-smi is not a valid command, please install a NVIDIA graphics driver and restart the terminal.")
			if input("Are you using CUDA 11.8? (y/n)") == "y":
				index_url = "https://download.pytorch.org/whl/cu118"
			elif input("Are you using CUDA 12.1? (y/n)") == "y":
				index_url = "https://download.pytorch.org/whl/cu121"
			elif input("Are you using CUDA 12.4? (y/n)") == "y":
				index_url = "https://download.pytorch.org/whl/cu124"
			else:
				print("Unknown CUDA! Defaulting to CUDA 12.4.")
				index_url = "https://download.pytorch.org/whl/cu124"
			command = f"{python_command} -m pip install --upgrade torch torchaudio torchvision --index-url {index_url}"
			print(f"Install command for torch: {command}")
			_ = os.system(f"call \"{activate_bat_filepath}\" && {command}")
			print(f"Failed to install torch packages with cuda acceleration of url {index_url}.")
			print(f"Installed {index_url} cuda acceleration for torch.")
		arguments.append("--lowvram") # for the sake of compatability across all devices

	# start comfyui
	main_py = Path(os.path.join(comfyui_directory, "main.py")).as_posix()
	command1 = f'cmd.exe /c "call \"{activate_bat_filepath}\" && {python_command} \"{main_py}\" ' + " ".join(arguments) + '"'
	print("Running ComfyUI with the following commands:")
	print(command1)

	proxy_py : str = Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "proxy.py")).as_posix()
	command2 = f"{python_command} \"{proxy_py}\""
	print("Running Proxy with the following commands:")
	print(command2)

	print("Starting both ComfyUI and Proxy scripts.")

	def delay_print() -> None:
		try:
			import requests
		except:
			print("Cannot import requests - skipping check.")
			return

		time.sleep(5)

		proxy_ip : str = "http://127.0.0.1:12500/echo"
		r = requests.get(proxy_ip)
		if r.status_code == 200:
			print(f"Cannot connect to the proxy on {proxy_ip}! The proxy failed to startup!")

		comfyui_ip = "http://127.0.0.1:8188"
		r = requests.get(comfyui_ip)
		if r.status_code == 200:
			print(f"Cannot connect to ComfyUI on {comfyui_ip}! ComfyUI failed to startup!")

		print("Head to Abyss Diver and open the AI Portrait page!")

	thread1 = threading.Thread(target=lambda : run_command(command1))
	thread2 = threading.Thread(target=lambda : run_command(command2))
	thread3 = threading.Thread(target=delay_print)
	thread1.start()
	thread2.start()
	thread3.start()
	thread1.join()
	thread2.join()
	thread3.join()
	print("Both ComfyUI and Proxy scripts have finished.")

def comfy_ui_linux(storage_directory : str) -> None:
	"""Install ComfyUI on Linux"""
	raise NotImplementedError

def comfy_ui_mac(storage_directory : str) -> None:
	"""Install ComfyUI on Mac"""
	raise NotImplementedError

def update_python_pip() -> None:
	python_cmd = get_installed_python()
	status = os.system(f"{python_cmd} -m ensurepip")
	assert status == 0, "'pip' is not installed with python! You will need to install pip."
	status = os.system(f"{python_cmd} -m pip install --upgrade pip")
	assert status == 0, "'pip' failed to update. Try running again."

def main() -> None:
	assert_path_length_limit()
	update_python_pip()

	tools_directory : str = Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools")).as_posix()
	os.makedirs(tools_directory, exist_ok=True)

	if platform.system() == "Windows":
		print('Running Windows.')
		comfy_ui_windows(tools_directory)
	elif platform.system() == "Linux":
		print('Running Linux.')
		comfy_ui_linux(tools_directory)
	elif platform.system() == "Darwin":
		# mac
		print('Running Mac.')
		comfy_ui_mac(tools_directory)

	print("Exiting main().")

if __name__ == '__main__':
	main()
