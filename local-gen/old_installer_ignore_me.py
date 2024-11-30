
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
		run_command(f"\"{PYTHON_COMMAND}\" -m pip uninstall torch --target \"{target_site_packages}\"", shell=True)

	if device == 0:
		# CPU
		print('Installing CPU')
		run_command(f"\"{PYTHON_COMMAND}\" -m pip install torch torchvision torchaudio --target \"{target_site_packages}\"", shell=True)
	elif device == 1:
		# NVIDIA (CUDA)
		print('Installing Torch CUDA, please wait a moment.')
		run_command(f"\"{PYTHON_COMMAND}\" -m pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu124 --target {target_site_packages}", shell=True)
	elif device == 2:
		# AMD (ROCM)
		print('Installing Torch AMD ROCM, please wait a moment.')
		run_command(f"\"{PYTHON_COMMAND}\" -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.1 --target {target_site_packages}", shell=True)
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
		print(run_command(f"export USE_MPS=1 && \"{PYTHON_COMMAND}\" -m pip install --pre torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/nightly/cpu --target {target_site_packages}", shell=True))

	write_last_device(device)

	print('Installing ComfyUI requirements')
	requirements_abs = Path(os.path.abspath(os.path.join(COMFYUI_INSTALLATION_FOLDER, "requirements.txt"))).as_posix()
	run_command(f"\"{PYTHON_COMMAND}\" -m pip install -r {requirements_abs} --target \"{target_site_packages}\"", shell=True)

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
