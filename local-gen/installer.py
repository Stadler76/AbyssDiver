
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
from typing import Optional

import os
import platform
import subprocess
import threading
import logging
import time
import re

def get_python_and_version() -> tuple[str, str]:
	for cmd in ["python3.10", "python3.11", "python3", "python", "py"]:
		try:
			result = subprocess.run([cmd, "--version"], capture_output=True, text=True, check=True)
			print(f"Command: {cmd}")
			print(f"Output: {result.stdout.strip()}")
			version = re.search(r"Python (\d+\.\d+\.\d+)", result.stdout)
			if version:
				print(f"Extracted Version: {version.group(1)}")
				if version.group(1).startswith("3.10") or version.group(1).startswith("3.11"):
					return cmd, version.group(1)
			else:
				print("No version match found.")
		except Exception as e:
			print(f"Command '{cmd}' failed: {e}")
			continue
	raise Exception("No suitable Python version is installed - please install Python 3.10.X or 3.11.X.")

def get_installed_python() -> str:
	cmd, _ = get_python_and_version()
	return cmd

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
COMFY_UI_AMD_GPU_REPOSITORY_URL : str = "https://github.com/patientx/ComfyUI-Zluda"

COMFYUI_CUSTOM_NODES : list[str] = ["https://github.com/ltdrdata/ComfyUI-Manager", "https://github.com/john-mnz/ComfyUI-Inspyrenet-Rembg"]

HUGGINGFACE_CHECKPOINTS_TO_DOWNLOAD : dict[str, Optional[str]] = {
	# SD1.5
	"hassakuHentaiModel_v13.safetensors" : None,
	# PonyXL
	"hassakuXLPony_v13BetterEyesVersion.safetensors" : "https://huggingface.co/FloricSpacer/AbyssDiverModels/resolve/main/hassakuXLPony_v13BetterEyesVersion.safetensors?download=true"
}
HUGGINGFACE_LORAS_TO_DOWNLOAD : dict[str, Optional[str]] = {
	# SD1.5
	"midjourneyanime.safetensors" : None,
	# PonyXL
	"DallE3-magik.safetensors" : "https://huggingface.co/FloricSpacer/AbyssDiverModels/resolve/main/DallE3-magik.safetensors?download=true"
}

CUSTOM_COMMAND_LINE_ARGS_FOR_COMFYUI : list[str] = [] # custom arguments to pass to comfyui

# IS_AMD_WINDOWS_MODE : bool = False

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

def run_command(args: list[str] | str, shell: bool = False) -> tuple[int, str]:
	print(f'RUNNING COMMAND: {str(args)}')
	print('=' * 10)
	try:
		process = subprocess.Popen(
			args,
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
			print(f"Command succeeded: {str(args)}")
		else:
			print(f"Command failed with code {status_code}: {str(args)}")
		return status_code, stdout_var
	except Exception as e:
		print(f"Command execution exception: {str(args)}")
		print(f"Exception details: {e}")
		return -1, str(e)

def ask_user_for_gpu_device() -> int:
	if input("Are you using a NVIDIA graphics card? (y/n)") == "y":
		return 1 # NVIDIA cuda

	print("Due to no device being supported, CPU will automatically be selected.")
	return 0

def check_for_proxy_and_comfyui_responses() -> None:
	try:
		import requests
	except:
		print("Cannot import requests package - skipping proxy/comfyui response checks.")
		return

	time.sleep(20) # more wait time lolz (first load takes a minute)

	proxy_ip : str = "http://127.0.0.1:12500/echo"
	try:
		r = requests.get(proxy_ip)
		if r.status_code != 200: raise
	except:
		print(f"Cannot connect to the proxy on {proxy_ip}! The proxy may have not started in time or failed to startup!")

	comfyui_ip = "http://127.0.0.1:8188"
	try:
		r = requests.get(comfyui_ip)
		if r.status_code != 200: raise
	except:
		print(f"Cannot connect to ComfyUI on {comfyui_ip}! ComfyUI may not have started or failed to startup!")

	print("Successfully connected to both ComfyUI and the Proxy!")
	print("Head to Abyss Diver and open the AI Portrait page!")
	print("")

def clone_custom_nodes_to_folder(custom_nodes_folder : str) -> None:
	previous_directory = os.getcwd()
	os.chdir(custom_nodes_folder)
	for node_repository_url in COMFYUI_CUSTOM_NODES:
		print(f'Cloning: {node_repository_url}')
		_ = os.system(f"git clone {node_repository_url}")
	os.chdir(previous_directory)

def comfy_ui_experimental_amd_windows(storage_directory : str) -> None:
	raise NotImplementedError

def download_checkpoints_to_subfolder(models_folder : str) -> None:
	for filename, checkpoint_url in HUGGINGFACE_CHECKPOINTS_TO_DOWNLOAD.items():
		if checkpoint_url is None:
			print(filename, 'checkpoint has no download set yet.')
			continue
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

def download_loras_to_subfolder(models_folder : str) -> None:
	for filename, lora_url in HUGGINGFACE_LORAS_TO_DOWNLOAD.items():
		if lora_url is None:
			print(filename, 'lora has no download set yet.')
			continue
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

def comfy_ui_windows(storage_directory : str) -> None:
	"""Install ComfyUI on Windows"""

	# clone ComfyUI
	comfyui_directory = Path(os.path.join(storage_directory, "ComfyUI")).as_posix()
	print(f'ComfyUI install directory: {comfyui_directory}')
	if os.path.exists(comfyui_directory) is False:
		print("Attempting to clone ComfyUI to the directory.")
		repository_url = COMFY_UI_DEFAULT_REPOSITORY_URL
		previous_directory = os.getcwd()
		os.chdir(storage_directory)
		status = os.system(f"git clone {repository_url}") # ignore: type
		assert status == 0, "git clone has failed - check if you have git installed."
		os.chdir(previous_directory)

	assert os.path.exists(comfyui_directory), "ComfyUI failed to be cloned."

	# Setup the virtual environment
	venv_directory : str = Path(os.path.join(comfyui_directory, "venv")).as_posix()
	python_filepath : str = Path(os.path.join(venv_directory, "Scripts", "python.exe")).as_posix()
	if os.path.exists(python_filepath) is False:
		print(f'No virtual enviornment python located at: {python_filepath}')
		print(f"{get_installed_python()} -m venv \"{venv_directory}\"")
		status = os.system(f"{get_installed_python()} -m venv \"{venv_directory}\"")
		assert status == 0, "Failed to create a virtual environment in the ComfyUI folder."

	# Activate the venv enviornment once for a test
	status = os.system(f"\"{python_filepath}\" --version")
	assert status == 0, "Failed to activate the virtual environment."

	# install proxy requirements
	print('Installing proxy requirements.')
	packages = ["tqdm", "requests", "fastapi", "pydantic", "pillow", "websocket-client", "aiohttp", "uvicorn", "websockets"]
	subprocess.run([python_filepath, "-m", "pip", "install"] + packages, check=True)

	# install ComfyUI/requirements.txt
	print('Installing ComfyUI requirements.')
	requirements_file = Path(os.path.join(comfyui_directory, "requirements.txt")).as_posix()
	subprocess.run([python_filepath, "-m", "pip", "install", "-r", str(requirements_file)], check=True)

	# git clone custom_nodes
	print('Cloning all custom nodes.')
	custom_nodes_folder = Path(os.path.join(comfyui_directory, "custom_nodes")).as_posix()
	clone_custom_nodes_to_folder(custom_nodes_folder)

	# pip install custom_nodes requirements.txt
	print('Installing custom nodes requirements.')
	for folder_name in os.listdir(custom_nodes_folder):
		if os.path.isdir(Path(os.path.join(custom_nodes_folder, folder_name)).as_posix()) is False:
			continue # not a folder
		folder_requirements = Path(os.path.join(custom_nodes_folder, folder_name, "requirements.txt")).as_posix()
		print(folder_requirements)
		if os.path.exists(folder_requirements) is False:
			continue # cannot find requirements.txt
		print(f'Installing {folder_name} requirements.')
		subprocess.run([python_filepath, "-m", "pip", "install", "-r", str(folder_requirements)], check=True)

	# download all checkpoint models
	models_folder = Path(os.path.join(comfyui_directory, "models")).as_posix()
	download_checkpoints_to_subfolder(models_folder)

	# download all lora models
	models_folder = Path(os.path.join(comfyui_directory, "models")).as_posix()
	download_loras_to_subfolder(models_folder)

	arguments = ["--windows-standalone-build", "--disable-auto-launch"]

	print('Asking user for GPU device.')
	device_n = ask_user_for_gpu_device()
	if device_n == 0:
		arguments.append("--cpu")
	elif device_n == 1:
		try:
			process = subprocess.run([python_filepath, "-c" "import torch; assert torch.cuda.is_available(), \'cuda not available\'"], check=True)
			assert process.returncode == 0, "Torch failed to import."
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
				print("Unknown CUDA! Defaulting to CUDA 12.4 (latest).")
				index_url = "https://download.pytorch.org/whl/cu124"
			_ = subprocess.run([python_filepath, "-m", "pip", "install", "--upgrade", "torch", "torchaudio", "torchvision", "--index-url", index_url], check=True)
			print(f"Installed {index_url} cuda acceleration for torch.")
		arguments.append("--lowvram") # for the sake of compatability across all devices

	# start comfyui
	main_py = Path(os.path.join(comfyui_directory, "main.py")).as_posix()
	command1_args = [python_filepath, main_py] + arguments
	print("Running ComfyUI with the following commands:")
	print(command1_args)

	proxy_py : str = Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "proxy.py")).as_posix()
	command2_args = [python_filepath, proxy_py]
	print("Running Proxy with the following commands:")
	print(command2_args)

	print("Starting both ComfyUI and Proxy scripts.")

	thread1 = threading.Thread(target=lambda : run_command(command1_args))
	thread2 = threading.Thread(target=lambda : run_command(command2_args))
	thread3 = threading.Thread(target=check_for_proxy_and_comfyui_responses)
	thread1.start()
	thread2.start()
	thread3.start()
	thread1.join()
	thread2.join()
	thread3.join()
	print("Both ComfyUI and Proxy scripts have finished.")

def comfyui_download_mac_linux_shared(storage_directory : str) -> None:
	"""Shared code between Linux and Mac for downloading ComfyUI"""

	# clone ComfyUI
	comfyui_directory = Path(os.path.join(storage_directory, "ComfyUI")).as_posix()
	print(f'ComfyUI install directory: {comfyui_directory}')
	if os.path.exists(comfyui_directory) is False:
		print("Attempting to clone ComfyUI to the directory.")
		repository_url = COMFY_UI_DEFAULT_REPOSITORY_URL
		previous_directory = os.getcwd()
		os.chdir(storage_directory)
		status = os.system(f"git clone {repository_url}")
		assert status == 0, "git clone has failed - check if you have git installed."
		os.chdir(previous_directory)

	assert os.path.exists(comfyui_directory), "ComfyUI failed to be cloned."

	# Setup the virtual environment
	venv_directory : str = Path(os.path.join(comfyui_directory, "venv")).as_posix()
	python_filepath : str = Path(os.path.join(venv_directory, "bin", "python")).as_posix()
	if os.path.exists(python_filepath) is False:
		status = os.system(f"{get_installed_python()} -m venv \"{venv_directory}\"")
		assert status == 0, "Failed to create a virtual environment in the ComfyUI folder."

		print('Giving the venv python file the permissions needed to execute.')
		os.system(f'chmod +x \"{python_filepath}\"')

	# Activate the venv enviornment once for a test
	status = os.system(f"{python_filepath} --version")
	assert status == 0, "Failed to activate the virtual environment (permission error)."

	# install proxy requirements
	os.system(f"{python_filepath} -m pip install tqdm requests fastapi pydantic pillow websocket-client aiohttp uvicorn websockets")

	# install ComfyUI/requirements.txt
	print('Installing ComfyUI requirements')
	requirements_file = Path(os.path.join(comfyui_directory, "requirements.txt")).as_posix()
	os.system(f"{python_filepath} -m pip install -r \"{requirements_file}\"")

	# git clone custom_nodes
	custom_nodes_folder = Path(os.path.join(comfyui_directory, "custom_nodes")).as_posix()
	clone_custom_nodes_to_folder(custom_nodes_folder)

	# pip install custom_nodes requirements.txt
	for folder_name in os.listdir(custom_nodes_folder):
		if os.path.isdir(Path(os.path.join(custom_nodes_folder, folder_name)).as_posix()) is False:
			continue # not a folder
		folder_requirements = Path(os.path.join(custom_nodes_folder, folder_name, "requirements.txt")).as_posix()
		print(folder_requirements)
		if os.path.exists(folder_requirements) is False:
			continue # cannot find requirements.txt
		print(f'Installing {folder_name} custom_node requirements')
		os.system(f"{python_filepath} -m pip install -r \"{folder_requirements}\"")

	# download all checkpoint models
	models_folder = Path(os.path.join(comfyui_directory, "models")).as_posix()
	download_checkpoints_to_subfolder(models_folder)

	# download all lora models
	models_folder = Path(os.path.join(comfyui_directory, "models")).as_posix()
	download_loras_to_subfolder(models_folder)

def start_comfyui_linux_mac_shared(comfyui_directory : str, arguments : list[str]) -> None:
	# start comfyui
	venv_directory : str = Path(os.path.join(comfyui_directory, "venv")).as_posix()
	python_filepath : str = Path(os.path.join(venv_directory, "bin", "python")).as_posix()

	main_py = Path(os.path.join(comfyui_directory, "main.py")).as_posix()

	command1_args = [python_filepath, main_py] + arguments
	print("Running ComfyUI with the following commands:")
	print(command1_args)

	proxy_py : str = Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "proxy.py")).as_posix()
	command2_args = [python_filepath, proxy_py]
	print("Running Proxy with the following commands:")
	print(command2_args)

	print("Starting both ComfyUI and Proxy scripts.")

	thread1 = threading.Thread(target=lambda : run_command(command1_args))
	thread2 = threading.Thread(target=lambda : run_command(command2_args))
	thread3 = threading.Thread(target=check_for_proxy_and_comfyui_responses)
	thread1.start()
	thread2.start()
	thread3.start()
	thread1.join()
	thread2.join()
	thread3.join()

	print("Both ComfyUI and Proxy scripts have finished.")

def comfy_ui_linux(storage_directory : str) -> None:
	"""Install ComfyUI on Linux"""
	comfyui_download_mac_linux_shared(storage_directory)
	comfyui_directory = Path(os.path.join(storage_directory, "ComfyUI")).as_posix()

	arguments = ["--disable-auto-launch"]

	print("At the current moment, only CPU support is made for Linux.")
	arguments.append("--cpu")

	start_comfyui_linux_mac_shared(comfyui_directory, arguments)

def comfy_ui_mac(storage_directory : str) -> None:
	"""Install ComfyUI on Mac"""
	comfyui_download_mac_linux_shared(storage_directory)
	comfyui_directory = Path(os.path.join(storage_directory, "ComfyUI")).as_posix()

	arguments = ["--disable-auto-launch"]

	print("At the current moment, only CPU support is made for Mac.")
	arguments.append("--cpu")

	start_comfyui_linux_mac_shared(comfyui_directory, arguments)

def update_python_pip() -> None:
	python_cmd, version = get_python_and_version()
	assert ("3.10" in version) or ("3.11" in version), "You must have python versions 3.10.X or 3.11.X. Please reinstall python."
	status = os.system(f"{python_cmd} -m pip install --upgrade pip")
	assert status == 0, "'pip' failed to update. Try running again."

def main() -> None:
	assert_path_length_limit()
	update_python_pip()

	tools_directory : str = Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools")).as_posix()
	os.makedirs(tools_directory, exist_ok=True)

	if platform.system() == "Windows":
		print('Running Windows.')
		# if input("Do you have an AMD GPU and want to try the experimental AMD-Accelerated ComfyUI version? (y/n)") == "y":
		# 	comfy_ui_experimental_amd_windows(tools_directory)
		# else:
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
