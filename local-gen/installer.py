'''
@SPOOKEXE - GitHub

One-click ComfyUI installer and runner for Abyss Diver to install the ComfyUI Local Generator!

Installs the following:
1. ComfyUI
2. ComfyUI Manager
3. hassakuXLPony_v13BetterEyesVersion checkpoint and Dalle3_AnimeStyle_PONY Lora
4. Additional python packages in a virtual environment (x2)

To uninstall, delete the "tools" folder under this folder and optionally uninstall git as needed.
'''

from pydantic import BaseModel
from typing import Optional, Union
from pathlib import Path

import os
import platform
import re
import requests
import signal
import subprocess
import tarfile
import time
import patoolib
import logging
import threading

CUSTOM_COMMAND_LINE_ARGS_FOR_COMFYUI = []

COMFYUI_REPOSITORY_URL : str = "https://github.com/comfyanonymous/ComfyUI"
COMFYUI_API_REPOSITORY_URL : str = "https://api.github.com/repos/comfyanonymous/ComfyUI"
COMFYUI_CUSTOM_NODES : list[str] = ["https://github.com/ltdrdata/ComfyUI-Manager", "https://github.com/john-mnz/ComfyUI-Inspyrenet-Rembg"]

CIVITAI_MODELS_TO_DOWNLOAD : dict[str, str] = {"hassakuXLPony_v13BetterEyesVersion.safetensors" : "https://civitai.com/api/download/models/575495?type=Model&format=SafeTensor&size=pruned&fp=bf16"}
CIVITAI_LORAS_TO_DOWNLOAD : dict[str, str] = {"DallE3-magik.safetensors" : "https://civitai.com/api/download/models/695621?type=Model&format=SafeTensor"}

HUGGINGFACE_CHECKPOINTS_TO_DOWNLOAD : dict[str, str] = {"hassakuXLPony_v13BetterEyesVersion.safetensors" : "https://huggingface.co/FloricSpacer/AbyssDiverModels/resolve/main/hassakuXLPony_v13BetterEyesVersion.safetensors?download=true"}
HUGGINGFACE_LORAS_TO_DOWNLOAD : dict[str, str] = {"DallE3-magik.safetensors" : "https://huggingface.co/FloricSpacer/AbyssDiverModels/resolve/main/DallE3-magik.safetensors?download=true"}

WHITELISTED_OPERATION_SYSTEMS : list[str] = ["Linux", "Windows", "Darwin"]
WINDOWS_ZIP_FILENAME : str = "ComfyUI_windows_portable_nvidia.7z"
LINUX_ZIP_FILENAME : str = "source.tar.gz"

FILEPATH_FOR_7z : Optional[str] = None
COMFYUI_INSTALLATION_FOLDER : Optional[str] = None
PYTHON_COMMAND : Optional[str] = None

logger = logging.getLogger()
logger.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)

class GithubFile(BaseModel):
	name : str
	browser_download_url : str
	class Config:
		extra = 'ignore'

def request_prompt(prompt : str, allowed_responses : list[str]) -> str:
	print(prompt)
	value = input("")
	while value not in allowed_responses:
		print("Invalid response.") # github @spookexe was here
		value = input("")
	return value

def download_file(url: str, destination: str, range : bool = False) -> None:
	"""Download a file from a URL and save it to a specified destination with support for resuming."""
	print(url)
	headers = {}
	if os.path.exists(destination) and range is True:
		# Get the size of the partially downloaded file
		existing_size = os.path.getsize(destination)
		headers['Range'] = f'bytes={existing_size}-'
	else:
		existing_size = 0

	response = requests.get(url, headers=headers, stream=True)
	response.raise_for_status()

	# Get the total file size from headers
	total_size = int(response.headers.get('content-length', 0)) + existing_size
	print(f"File size: {total_size / 1_000_000:.2f} MB")

	split_amount = total_size / 10
	counter = existing_size

	# Open the file in append mode if resuming
	with open(destination, 'ab') as file:
		for data in response.iter_content(chunk_size=1024):
			size = file.write(data)
			counter += size
			if counter >= split_amount:
				print(f"{counter / 1_000_000:.2f} / {total_size / 1_000_000:.2f} MB")
				split_amount += total_size / 10

	print("Download complete.")

def run_command(command: str, shell: bool = False) -> int:
	logger.info('RUNNING COMMAND:')
	logger.info(command)
	logger.info('=' * 20)

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
					logger.log(log_level, line.strip())
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
			logger.info(f"Command succeeded: {command}")
		else:
			logger.warning(f"Command failed with code {status_code}: {command}")

		return status_code, stdout_var
	except Exception as e:
		logger.error(f"Command execution exception: {command}")
		logger.exception(f"Exception details: {e}")
		return -1, str(e)

def unzip_targz(filepath : str, directory : str) -> None:
	os.makedirs(directory, exist_ok=True)
	with tarfile.open(filepath, 'r:gz') as tar_ref:
			tar_ref.extractall(directory)

def get_miniconda_cmdline_filepath() -> str:
	os_platform : str = platform.system() # Windows, Linux, Darwin (MacOS)
	path = Path(os.path.expanduser("~/miniconda3/condabin/conda")).as_posix()
	if os_platform == "Windows":
		path += ".bat"
	return path

def has_miniconda_been_installed() -> bool:
	return os.path.exists(get_miniconda_cmdline_filepath())

def get_windows_miniconda_envs_folder() -> str:
	return Path(os.path.expanduser("~/miniconda3/envs")).as_posix()

def install_miniconda_for_os() -> None:
	os_platform : str = platform.system() # Windows, Linux, Darwin (MacOS)
	logger.info(f"Installing miniconda for OS: {os_platform}")
	logger.info(f"If the install process fails to install, install it manually from the link printed below:")
	if os_platform == "Windows":
		logger.info("Downloading miniconda.exe")
		windows_download_url = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
		try:
			download_file(windows_download_url, "miniconda.exe")
		except Exception as e:
			print('Failed to download Miniconda!')
			print(e)
			print('Please download manually and place in the local-gen folder and rename it to "miniconda.exe".')
			print(windows_download_url)
			print('Press enter to continue...')
			input("")
		logger.info("Installing miniconda.sh")
		print(run_command("miniconda.exe /S", shell=True))
		t1 = Path(os.path.expanduser("~/miniconda3")).as_posix()
		assert os.path.exists(t1), "Miniconda failed to install - please install manually by running the `miniconda.sh` and install under the name minconda3 in the user directory."
	elif os_platform == "Linux":
		logger.info("Downloading miniconda.sh")
		linux_download_url = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
		try:
			download_file(linux_download_url, "miniconda.exe")
		except Exception as e:
			print('Failed to download Miniconda!')
			print(e)
			print('Please download manually and place in the local-gen folder and rename it to "miniconda.sh".')
			print(linux_download_url)
			print('Press enter to continue...')
			input("")
		logger.info("Installing miniconda.sh")
		t1 = Path(os.path.expanduser("~/miniconda3")).as_posix()
		print(run_command(f"bash miniconda.sh -b -u -p {t1}", shell=True))
		assert os.path.exists(t1), "Miniconda failed to install - please install manually by running the `miniconda.sh` and install under the name minconda3 in the user directory."
	elif os_platform == "Darwin":
		logger.info("Downloading miniconda.sh")

		mac_download_url = "https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh"
		try:
			download_file(mac_download_url, "miniconda.sh")
		except Exception as e:
			print('Failed to download Miniconda!')
			print(e)
			print('Please download manually and place in the local-gen folder and rename it to "miniconda.sh".')
			print(mac_download_url)
			print('Press enter to continue...')
			input("")
		logger.info("Installing miniconda.sh")
		t1 = Path(os.path.expanduser("~/miniconda3")).as_posix()
		print(run_command(f"bash miniconda.sh -b -u -p {t1}", shell=True))
		assert os.path.exists(t1), "Miniconda failed to install - please install manually by running the `miniconda.sh` and install under the name minconda3 in the user directory."
	else:
		print(f"Unknown OS {os_platform} - cannot get conda version.")
		exit()

	logger.info("Finished installing miniconda")

def does_conda_env_exist() -> bool:
	return os.path.exists(Path(os.path.join(get_windows_miniconda_envs_folder(), "py3_10_9")).as_posix())

def get_conda_env_directory() -> str:
	return Path(os.path.join(get_windows_miniconda_envs_folder(), "py3_10_9")).as_posix()

def create_update_conda_env_var() -> None:
	logger.info("Initializing Conda before install.")
	print(run_command(f"{get_miniconda_cmdline_filepath()} init", shell=True))

	# create a new virtual environment for python 3.10.9 called "py3_10_9"
	if os.path.exists(Path(os.path.join(get_miniconda_cmdline_filepath(), "envs", "py3_10_9")).as_posix()) is False:
		logger.info("Creating new environment.")
		print('The python conda environment will take about 2.8GB in total on disk.')
		print('Press enter to install the python 3.10.9 conda environment. The command displayed below will not run until you do so, and will wait until finished.')
		print('THE BELOW COMMAND WILL BE RUNNING IN THE BACKGROUND! PLEASE WAIT FOR IT TO FINISH!')

		if platform.platform() == "Windows":
			command = "call " + command
		command = f"{get_miniconda_cmdline_filepath()} create -n py3_10_9 python=3.10.9 anaconda --yes"
		print(run_command(command, shell=True))

	logger.info("Listing current environments.")
	print(run_command(f"{get_miniconda_cmdline_filepath()} env list", shell=True))

	logger.info("Initializing Conda after install.")
	print(run_command(f"{get_miniconda_cmdline_filepath()} init", shell=True))

	logger.info("Activating python 3.10.9 environment.")
	print(run_command(f"{get_miniconda_cmdline_filepath()} activate py3_10_9", shell=True))

def get_python_version() -> tuple[Union[str, None], Union[str, None]]:
	"""Find the python version that is installed."""
	pattern = r"Python (.+)"
	# check 'python' command
	status, output = run_command("python --version", shell=True)
	if status == 0:
		return "python", re.match(pattern, output).group(1)
	# check 'py' command
	status, output = run_command("py --version", shell=True)
	if status == 0:
		return "py", re.match(pattern, output).group(1)
	# check 'python3' command
	status, output = run_command("python3 --version", shell=True)
	if status == 0:
		return "python3", re.match(pattern, output).group(1)
	# no python available
	return None, None

def download_git_portal_windows() -> None:
	status, _ = run_command("git --version", shell=True)
	if status == 0:
		return

	print("You are required to install git to download ComfyUI nodes on Windows.")
	# print("Please install by visiting https://git-scm.com/downloads and installing the Windows 64-bit version.")
	# print("Note: for most options, you can press next, if you aren't sure, press next.")
	# print("Press enter to continue once git is installed... ")

	print("You will be prompted to install git.")
	print("You can skip through the installation by pressing next.")
	print("This is using winget so if you don't have that you will need to manually install git.")
	print("To manually install, visit 'https://git-scm.com/downloads' and run this script again.")

	print(run_command("winget install --id Git.Git -e --source winget", shell=True))

	status, _ = run_command("git --version", shell=True)
	assert status == 0, "Could not locate the 'git' package which is required. You may need to restart the shell for the terminal to know the installed git exists, otherwise install it manually and restart the shell."

def download_git_portal_linux() -> None:
	status, _ = run_command("git --version", shell=True)
	if status == 0:
		return

	if platform.platform() == "Darwin":
		print('You must install Linux manually on Mac devices.')
		print('Please head to https://github.com/git-guides/install-git and install following the "Install Git on Mac" section.')
		print('Press enter when you have installed git.')
		input("")
	else:
		print("You are required to install git to download ComfyUI on Linux.")
		print("You will be prompted now to install it.")
		run_command("sudo apt update && sudo apt install -y git", shell=True)

	status, _ = run_command("git --version", shell=True)
	assert status == 0, "Could not locate the 'git' package which is required. You may need to restart the shell for the terminal to know the installed git exists."

def get_github_repository_latest_release_files(api_url : str) -> list[GithubFile]:
	"""Get the latest release files of the target github repository"""
	response = requests.get(api_url, allow_redirects=True)
	response.raise_for_status()
	data : dict = response.json()
	assets : list[GithubFile] = []
	assets.append(GithubFile(name="source.zip", browser_download_url=data['zipball_url']))
	assets.append(GithubFile(name="source.tar.gz", browser_download_url=data['tarball_url']))
	assets.extend([GithubFile(**asset) for asset in data['assets']])
	return assets

def get_comfyui_latest_release_files() -> list[GithubFile]:
	"""Get the comfyui latest release files"""
	return get_github_repository_latest_release_files(f'{COMFYUI_API_REPOSITORY_URL}/releases/latest')

def find_github_file_of_name(files : list[GithubFile], name : str) -> Optional[GithubFile]:
	"""Search the list of files for the target filename."""
	for item in files:
		if item.name == name:
			return item
	return None

def install_comfyui_nodes(custom_nodes_folder : str) -> None:
	print("Installing ComfyUI Custom Nodes")
	before_cwd : str = os.getcwd()
	os.chdir(custom_nodes_folder)
	for url in COMFYUI_CUSTOM_NODES:
		run_command(f"git clone {url}", shell=True)
	os.chdir(before_cwd)
	py_exe = Path(os.path.join(COMFYUI_INSTALLATION_FOLDER, "..", "python_embeded", "python.exe")).as_posix()

	if platform.platform() == "Darwin":
		print("You are required to have CMAKE installed for the transparent background node to install properly.")
		print("You will need to accept the xcodebuild license of building apps on your device using CMAKE.")
		print("You will first be prompted to accept the license, then you will be prompted for the CMAKE installation.")
		print("This build process for cmake may take a period of time with opencv-python's package when it starts building.")
		s1, e1 = run_command('sudo xcodebuild -license accept', shell=True)
		assert s1, e1
		print("\n"*2)
		print('Press enter to run the command below after it has been displayed in the terminal.')
		s2, e2 = run_command('brew install cmake', shell=True)
		assert s2, e2

	if os.path.exists(py_exe):
		site_pckge_folder = Path(os.path.join(COMFYUI_INSTALLATION_FOLDER, "..", "python_embeded", "Lib", "site-packages")).as_posix()
		run_command(f"\"{py_exe}\" -m pip install --no-user --target \"{site_pckge_folder}\" pydantic --verbose ", shell=True)
	else:
		target_site_packages = Path(os.path.join(get_conda_env_directory(), "lib", "python3.10", "site-packages")).as_posix()
		run_command(f"\"{PYTHON_COMMAND}\" -m pip install pydantic --verbose --target {target_site_packages}", shell=True)

	for folder_name in os.listdir(custom_nodes_folder):
		if os.path.isdir(Path(os.path.join(custom_nodes_folder, folder_name)).as_posix()) is False:
			continue
		req_txtfile = Path(os.path.join(custom_nodes_folder, folder_name, "requirements.txt")).as_posix()
		if os.path.exists(req_txtfile):
			print(f'Installing requirements for: {folder_name} {req_txtfile}')
			print('This may take a minute.')
			if os.path.exists(py_exe):
				print('ComfyUI Embeded Python')
				site_pckge_folder = Path(os.path.join(COMFYUI_INSTALLATION_FOLDER, "..", "python_embeded", "Lib", "site-packages")).as_posix()
				run_command(f"\"{py_exe}\" -m pip install --no-user --target \"{site_pckge_folder}\" -r \"{Path(req_txtfile).as_posix()}\"", shell=True)
			else:
				print('System Python')
				target_site_packages = Path(os.path.join(get_conda_env_directory(), "lib", "python3.10", "site-packages")).as_posix()
				run_command(f"\"{PYTHON_COMMAND}\" -m pip install -r \"{Path(req_txtfile).as_posix()}\" --verbose --target \"{target_site_packages}\"", shell=True)

	print("Installed ComfyUI Custom Nodes")

def prompt_safetensor_file_install(folder : str, filename : str, download_url : str) -> None:
	if os.path.exists(Path(os.path.join(folder, filename)).as_posix()) is True:
		print(filename, "already exists.")
		return
	while True:
		print("Press enter to continue once downloaded... ")
		input("")
		if os.path.exists(Path(os.path.join(folder, filename)).as_posix()) is True:
			break
		print(f"You have not renamed the safetensors file or placed it in the directory {folder}!")
		print(f"Make sure to rename the downloaded file {download_url} to {filename} and place it in the directory specified above.")

def install_comfyui_checkpoints(checkpoints_folder : str) -> None:
	index = 0
	for filename, download_url in CIVITAI_MODELS_TO_DOWNLOAD.items():
		if os.path.exists(Path(os.path.join(checkpoints_folder, filename)).as_posix()) is True:
			index += 1
			continue
		print(index, '/', len(CIVITAI_MODELS_TO_DOWNLOAD.values()))
		print("Due to age restrictions you have to download models manually.")
		print(f"Download the following model: {download_url}")
		print(f"Place the model in the folder: {checkpoints_folder}")
		print(f"Rename the file to {filename}.")
		run_command(f"start '{download_url}'")
		run_command(f"explorer {checkpoints_folder}")
		prompt_safetensor_file_install(checkpoints_folder, filename, download_url)
		index += 1

def install_comfyui_loras(loras_folder : str) -> None:
	index = 0
	for filename, download_url in CIVITAI_LORAS_TO_DOWNLOAD.items():
		if os.path.exists(Path(os.path.join(loras_folder, filename)).as_posix()) is True:
			index += 1
			continue
		print(index, '/', len(CIVITAI_LORAS_TO_DOWNLOAD.values()))
		print("Due to age restrictions you have to download LORAs manually.")
		print(f"Download the following lora: {download_url}")
		print(f"Place the lora in the folder: {loras_folder}")
		print(f"Rename the file to {filename}.")
		run_command(f"start '{download_url}'")
		run_command(f"explorer {loras_folder}")
		prompt_safetensor_file_install(loras_folder, filename, download_url)
		index += 1

def is_huggingface_models_available() -> bool:
	for name, url in HUGGINGFACE_CHECKPOINTS_TO_DOWNLOAD.items():
		if requests.get(url, stream=True).status_code != 200:
			print(f"Model {name} is unavailable on huggingface!")
			return False
	for name, url in HUGGINGFACE_LORAS_TO_DOWNLOAD.items():
		if requests.get(url, stream=True).status_code != 200:
			print(f"Model {name} is unavailable on huggingface!")
			return False
	return True

def has_all_required_comfyui_models() -> bool:
	if COMFYUI_INSTALLATION_FOLDER is None or os.path.exists(Path(COMFYUI_INSTALLATION_FOLDER).as_posix()) is False:
		print("Missing ComfyUI.")
		return False
	checkpoints_folder : str = Path(os.path.join(COMFYUI_INSTALLATION_FOLDER, "models", "checkpoints")).as_posix()
	for name, _ in HUGGINGFACE_CHECKPOINTS_TO_DOWNLOAD.items():
		if os.path.exists(Path(os.path.join(checkpoints_folder, name)).as_posix()) is False:
			print(f"Missing Checkpoint: {Path(os.path.join(checkpoints_folder, name)).as_posix()}")
			return False
	loras_folder : str = Path(os.path.join(COMFYUI_INSTALLATION_FOLDER, "models", "loras")).as_posix()
	for name, _ in HUGGINGFACE_LORAS_TO_DOWNLOAD.items():
		if os.path.exists(Path(os.path.join(loras_folder, name)).as_posix()) is False:
			print(f"Missing LORA: {Path(os.path.join(loras_folder, name)).as_posix()}")
			return False
	return True

def install_comfyui_models_from_hugginface() -> None:
	checkpoints_folder : str = Path(os.path.join(COMFYUI_INSTALLATION_FOLDER, "models", "checkpoints")).as_posix()
	for name, url in HUGGINGFACE_CHECKPOINTS_TO_DOWNLOAD.items():
		print("Downloading:", name)
		try:
			download_file(url, Path(os.path.join(checkpoints_folder, name)).as_posix(), range=True)
		except Exception as e:
			print("Failed to download model file:")
			print(e)
			exit()

	loras_folder : str = Path(os.path.join(COMFYUI_INSTALLATION_FOLDER, "models", "loras")).as_posix()
	for name, url in HUGGINGFACE_LORAS_TO_DOWNLOAD.items():
		print("Downloading:", name)
		try:
			download_file(url, Path(os.path.join(loras_folder, name)).as_posix(), range=True)
		except Exception as e:
			print("Failed to download model file:")
			print(e)
			exit()

def download_comfyui_latest(filename : str, directory : str) -> None:
	"""Download the latest release."""
	os.makedirs(directory, exist_ok=True)

	filepath : str = Path(os.path.join(directory, filename)).as_posix()
	if os.path.exists(filepath) is True:
		print(f"File {filename} has already been downloaded. Delete for it to be re-downloaded.")
		return

	latest_files : list[str] = get_comfyui_latest_release_files()

	target_file : Optional[GithubFile] = find_github_file_of_name(latest_files, filename)
	if target_file is None:
		raise ValueError(f"Unable to find latest release file for ComfyUI: {filename}")

	download_file(target_file.browser_download_url, filepath, range=True)

def install_comfyui_and_models_process(install_directory : str) -> None:
	global COMFYUI_INSTALLATION_FOLDER

	COMFYUI_INSTALLATION_FOLDER = Path(os.path.abspath(install_directory)).as_posix() # install_directory

	if has_all_required_comfyui_models() is False:
		print("="*20)
		print("Note: The total file size required for Conda will add up over 2.2GB.")
		print("Note: The total file size required for ComfyUI will add up over 9GB.")
		print("Note: The total file size required for the Abyss Diver content will add up to 7.1GB")
		print("You will need a total of at least 19.3GBs available.")
		print("Press enter to continue...")
		input("")

	print("ComfyUI is located at: ", Path(os.path.abspath(install_directory)).as_posix()) # install_directory)
	install_comfyui_nodes(Path(os.path.join(COMFYUI_INSTALLATION_FOLDER, "custom_nodes")).as_posix())

	print("="*20)

	if has_all_required_comfyui_models():
		print("All models are already downloaded - skipping step.")
		return

	if is_huggingface_models_available():
		print("HuggingFace resource is available - automatically downloading models.")
		install_comfyui_models_from_hugginface()
	else:
		print("HuggingFace resource unavailable - manual installation needed.")
		print("For this section you will be manually installing and placing safetensor (AI Model) files in the given directories.")
		print("Both the directory and the download will automatically open/start when you proceed.")
		print("This is REQUIRED to run the local generation.")
		print(f"You will need to download a total of {len(CIVITAI_MODELS_TO_DOWNLOAD.values()) + len(CIVITAI_LORAS_TO_DOWNLOAD.values())} files.")
		print("Press enter to continue...")
		input("")

		install_comfyui_checkpoints(Path(os.path.join(COMFYUI_INSTALLATION_FOLDER, "models", "checkpoints")).as_posix())
		install_comfyui_loras(Path(os.path.join(COMFYUI_INSTALLATION_FOLDER, "models", "loras")).as_posix())

def comfyui_windows_installer() -> None:
	"""Install the ComfyUI portable on Windows."""
	directory : str = "tools"

	# unzip the file if not already done
	install_directory : str = Path(os.path.join(directory, "ComfyUI_windows_portable", "ComfyUI")).as_posix()

	if os.path.isdir(Path(install_directory).as_posix()) is False:
		download_git_portal_windows()

		download_comfyui_latest(WINDOWS_ZIP_FILENAME, directory)

		print("Extracting the 7zip file using patool.")
		before_cwd = os.getcwd()
		os.chdir(Path(os.path.abspath(directory)).as_posix())
		try:
			print(Path(os.path.abspath(directory)).as_posix())
			print(os.listdir())
			patoolib.extract_archive("ComfyUI_windows_portable_nvidia.7z", outdir=".")
		except Exception as e:
			print("Failed to extract ComfyUI_windows_portable_nvidia.7z.")
			print("You may just need to restart the terminal if 'patool' was just installed as the terminal needs to update for the executables to be present.")
			print("Try restart the terminal first before manually unpacking it.")
			print("To manually unpack it, please install 7zip. https://7-zip.org/download.html")
			print("Unpack it into the tools folder, and make sure the folder directory is:")
			print("tools")
			print("-- ComfyUI_windows_portable")
			print("---- ComfyUI")
			print("---- python_embeded")
			print("---- update")
			print(e)
			exit()
		os.chdir(before_cwd)
	else:
		print("ComfyUI is already downloaded - skipping unpacking and release download.")

	install_comfyui_and_models_process(install_directory)

def comfyui_linux_installer() -> None:
	"""Install ComfyUI on Linux"""
	directory : str = "tools"

	# install directory

	install_directory = Path(os.path.abspath(os.path.join(directory, "ComfyUI"))).as_posix()
	if os.path.exists(Path(install_directory).as_posix()) is False:
		download_git_portal_linux() # make sure git is installed

		os.chdir(directory)

		status, message = run_command(f"git clone {COMFYUI_REPOSITORY_URL}", shell=True)
		if "already exists" not in message:
			assert status == 0, f"Failed to clone repository {COMFYUI_REPOSITORY_URL}: {message}"

		os.chdir('..')

	install_comfyui_and_models_process(install_directory)

def ask_windows_gpu_cpu() -> int:
	is_gpu_mode : str = request_prompt("Will you be running image generation on your graphics card? (y/n)", ["y", "n"])
	if is_gpu_mode == "n": return 0

	print('Due to issues only nvidia is available on Windows.')
	print('If you do not have a NVIDIA graphics card, you will be running on the CPU.')

	is_nvidia_gpu : str = request_prompt("Is your graphics card a NVIDIA one? (y/n)", ["y", "n"])
	if is_nvidia_gpu == "y": return 1

	# is_amd_gpu : str = request_prompt("Is your graphics card a AMD one? (y/n)", ["y", "n"])
	# if is_amd_gpu == "y":
	# 	print("Warning: AMD cards can only run with DirectML which is slower on Windows.")
	# 	return 2

	# is_intel_gpu : str = request_prompt("Is your graphics card a Intel one? (y/n)", ["y", "n"])
	# if is_intel_gpu == "y":
	# 	print("WARNING: Please follow the steps on 'https://github.com/comfyanonymous/ComfyUI' to install Intel GPU support before continuing.")
	# 	print("Press enter to continue...")
	# 	input("")
	# 	return 3

	# is_directml_mode : str = request_prompt("Do you want to run in DirectML (for unsupported GPUs you can try use this)? (y/n)", ["y", "n"])
	# if is_directml_mode == "y":
	# 	return 4

	print("Unfortunately the card you provided is not supported on Windows.")
	print("Image generation will be running on the CPU, unless you restart this file and utilize DirectML.")
	return 0

def ask_linux_gpu_cpu() -> int:
	is_gpu_mode : str = request_prompt("Will you be running image generation on your graphics card? (y/n)", ["y", "n"])
	if is_gpu_mode == "n":
		return 0

	is_mac : str =  request_prompt("Are you on a MAC device? (y/n)", ["y", "n"])
	if is_mac == "y":
		return 3

	is_nvidia_gpu : str = request_prompt("Is your graphics card a NVIDIA one? (y/n)", ["y", "n"])
	if is_nvidia_gpu == "y":
		return 1

	is_amd_linux : str =  request_prompt("Is your graphics card a AMD one? (y/n)", ["y", "n"])
	if is_amd_linux == "y":
		return 2

	print("You have a unsupported graphics card - will default to CPU mode.")
	return 0

def get_last_device() -> Optional[int]:
	if os.path.exists('device') is False:
		return None
	try:
		with open("device", "r") as file:
			return int(file.read())
	except:
		return None

def write_last_device(device : int) -> None:
	with open("device", "w") as file:
		file.write(str(device))

def comfyui_windows_runner() -> subprocess.Popen:
	"""Run the ComfyUI portable on Windows."""
	assert COMFYUI_INSTALLATION_FOLDER, "COMFYUI_INSTALLATION_FOLDER is not set to anything - exiting."

	print("Running ComfyUI.")

	device : int = ask_windows_gpu_cpu() # 0:cpu, 1:cuda, 2:amd, 3:intel, 4:direct(not available)

	embeded_py_filepath = Path(os.path.abspath(f"{COMFYUI_INSTALLATION_FOLDER}/../python_embeded/python.exe")).as_posix()
	target_site_packages = Path(os.path.join(COMFYUI_INSTALLATION_FOLDER, "python_embeded", "Lib", "site-packages")).as_posix()

	process : subprocess.Popen = None
	args = [embeded_py_filepath, "-s", "main.py", "--windows-standalone-build", '--disable-auto-launch'] + CUSTOM_COMMAND_LINE_ARGS_FOR_COMFYUI

	if device == 0:
		# cpu
		args.append("--cpu")
	elif device == 1:
		args.append('--lowvram')
	elif device == 2:
		args.append("--cpu")
	elif device == 3:
		args.append("--cpu")
	elif device == 4:
	# 	# amd/DirectML
	# 	print('Installing Torch DirectML. Please wait a moment.')
	# 	print(run_command(f'{embeded_py_filepath} -m pip install torch_directml --target {target_site_packages}', shell=True))
	# 	args.append("--directml")
		args.append("--cpu")
	else:
		# unknown
		print('Unknown device.')
		args.append("--cpu")

	print("Running the comfyui process.")
	process = subprocess.Popen(args, cwd=COMFYUI_INSTALLATION_FOLDER, shell=False)
	return process

def comfyui_linux_mac_runner() -> None:
	"""Run ComfyUI on Linux"""
	assert COMFYUI_INSTALLATION_FOLDER, "COMFYUI_INSTALLATION_FOLDER is not set to anything - exiting."

	# 0:cpu, 1:cuda, 2:romc
	last_device : Optional[int] = get_last_device()
	device : int = ask_linux_gpu_cpu()

	target_site_packages = Path(os.path.join(get_conda_env_directory(), "lib", "python3.10", "site-packages")).as_posix()

	# remove torch for it to be reinstalled for GPU
	if device != 0 and (last_device is None or last_device != device):
		print('Uninstalling old torch.')
		run_command(f"{PYTHON_COMMAND} -m pip uninstall torch --target {target_site_packages}", shell=True)

	if device == 0:
		# CPU
		print('Installing CPU')
		run_command(f"{PYTHON_COMMAND} -m pip install torch torchvision torchaudio --target {target_site_packages}", shell=True)
	elif device == 1:
		# NVIDIA (CUDA)
		print('Installing Torch CUDA, please wait a moment.')
		run_command(f"{PYTHON_COMMAND} -m pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu124 --target {target_site_packages}", shell=True)
	elif device == 2:
		# AMD (ROCM)
		print('Installing Torch AMD ROCM, please wait a moment.')
		run_command(f"{PYTHON_COMMAND} -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.1 --target {target_site_packages}", shell=True)
	elif device ==3:
		# Mac
		print('Installing Metal CPU')

		print("Building PyTorch with MPS support requires Xcode 13.3.1 or later.")
		print("You can download the latest public Xcode release on the Mac App Store OR the latest beta release on the Mac App Store / Apple Developer website.")
		print("App Store: https://apps.apple.com/us/app/xcode/id497799835?mt=12")
		print("Developer Website: https://developer.apple.com/download/applications/")
		print("Press enter to continue...")
		input("")

		print('Installing Torch with MPS enabled.')
		print(run_command(f"export USE_MPS=1 && {PYTHON_COMMAND} -m pip install --pre torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/nightly/cpu --target {target_site_packages}", shell=True))

	write_last_device(device)

	print('Installing ComfyUI requirements')
	requirements_abs = Path(os.path.abspath(os.path.join(COMFYUI_INSTALLATION_FOLDER, "requirements.txt"))).as_posix()
	run_command(f"{PYTHON_COMMAND} -m pip install -r {requirements_abs} --target {target_site_packages}", shell=True)

	main_py_filepath = Path(os.path.abspath(os.path.join(COMFYUI_INSTALLATION_FOLDER, "main.py"))).as_posix()

	process : subprocess.Popen = None
	args = [PYTHON_COMMAND, "-s", main_py_filepath, '--disable-auto-launch'] + CUSTOM_COMMAND_LINE_ARGS_FOR_COMFYUI

	if device != 0:
		args.append('--lowvram')

	if device == 0:
		# cpu
		print('Added CPU argument')
		args.append("--cpu --force-fp16")
	elif device == 1:
		print("Check Cuda Malloc")
		if request_prompt("Are any of your currently plugged-in GPUs older than the 1060 series (but not including the 1060)? (y/n): ", ["y", "n"]) == "y":
			args.append("--disable-cuda-malloc")
	elif device == 3:
		# mac
		print('No Mac Options needed.')

	print("Running the ComfyUI process.")
	print(args, COMFYUI_INSTALLATION_FOLDER)
	process = subprocess.Popen(args, cwd=COMFYUI_INSTALLATION_FOLDER, shell=False)
	return process

def proxy_runner() -> subprocess.Popen:
	print(f'Using {PYTHON_COMMAND} to open python/main.py')
	return subprocess.Popen([PYTHON_COMMAND, 'python/main.py'], shell=False)

def get_miniconda_python_exe_path() -> str:
	os_platform : str = platform.system() # Windows, Linux, Darwin (MacOS)
	py_cmd = ""
	if os_platform == "Windows":
		py_cmd = Path(os.path.join(get_conda_env_directory(), "python.exe")).as_posix()
	elif os_platform == "Darwin":
		py_cmd = Path(os.path.join(get_conda_env_directory(), "bin", "python3.10")).as_posix()
	elif os_platform == "Linux":
		py_cmd = Path(os.path.join(get_conda_env_directory(), "bin", "python3.10")).as_posix()
	return py_cmd

def main() -> None:
	os_platform : str = platform.system() # Windows, Linux, Darwin (MacOS)

	available_ops : str = ", ".join(WHITELISTED_OPERATION_SYSTEMS)
	assert os_platform in WHITELISTED_OPERATION_SYSTEMS, f"Operating System {os_platform} is unsupported! Available platforms are: {available_ops}"

	print(f'Running one-click-comfyui on operating system {os_platform}.')

	print("Checking conda.")
	install_conda_for_python()

	get_windows_miniconda_envs_folder()

	py_cmd = get_miniconda_python_exe_path()
	version = "3.10.9"

	print(py_cmd)
	assert os.path.exists(py_cmd), "Conda failed to install."

	print(py_cmd, version)

	global PYTHON_COMMAND
	PYTHON_COMMAND = py_cmd

	print(f"Found python ({py_cmd}) of version {version}.")

	print(run_command(f"\"{PYTHON_COMMAND}\" -m pip install -r requirements.txt", shell=True))

	process_proxy : subprocess.Popen
	process_comfyui : subprocess.Popen

	if os_platform == "Windows":
		print('Installing for Windows!')
		comfyui_windows_installer()
		process_proxy = proxy_runner()
		time.sleep(3) # let proxy output its message first
		process_comfyui = comfyui_windows_runner()
	elif os_platform == "Linux" or os_platform == "Darwin":
		print(f'Installing for {os_platform}!')
		comfyui_linux_installer()
		print('Running proxy.')
		process_proxy = proxy_runner()
		time.sleep(3) # let proxy output its message first
		print('Running main.')
		process_comfyui = comfyui_linux_mac_runner()
	else:
		exit()

	try:
		process_proxy.wait() # wait for process to terminate
		process_comfyui.wait() # wait for comfyui to terminate
	except KeyboardInterrupt: # CTRL+C
		os.kill(process_proxy.pid, signal.SIGTERM)
		os.kill(process_comfyui.pid, signal.SIGTERM)

def install_conda_for_python() -> None:
	if has_miniconda_been_installed() is False:
		print('Installing miniconda.')
		install_miniconda_for_os()
	assert has_miniconda_been_installed(), "Miniconda is not installed. You may need to restart the terminal if you just installed it for the terminal to know its there."
	print("Miniconda is installed.")
	print("Creating/Updating Conda Environment.")
	create_update_conda_env_var()
	assert os.path.exists(get_conda_env_directory()), "Conda Environment does not exist."
	print("Conda Environment exists.")

if __name__ == '__main__':
	main()
