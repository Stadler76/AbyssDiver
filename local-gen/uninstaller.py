
from pathlib import Path

import shutil
import os

def get_directory_size(directory : str) -> int:
	total_size : int = 0
	for dirpath, _, filenames in os.walk(directory):
		for filename in filenames:
			filepath = os.path.join(dirpath, filename)
			if not os.path.islink(filepath):
				total_size += os.path.getsize(filepath)
	return total_size

def query_directory(directory : str) -> None:
	print("="*10)
	print("Found the following directory:")
	print(directory)
	print("Getting directory total size:")
	total_size : int = get_directory_size(directory)
	mb_size : float = total_size/(1024**2)
	gb_size : float = total_size/(1024**3)
	print(f"Total directory size: {gb_size:,.0f}GB ({mb_size:,.0f}MB)")
	if input("Do you want to delete this directory? (y/n)") == "y":
		print("Deleting....")
		shutil.rmtree(directory)
		print("Finished")

def query_file(filepath : str) -> None:
	print("="*10)
	print("Found the following file:")
	print(filepath)
	print("Getting file total size:")
	total_size : int = os.path.getsize(filepath)
	mb_size : float = total_size/(1024**2)
	print(f"Total file size: {mb_size:,.0f}MB")
	if input("Do you want to delete this file? (y/n)") == "y":
		os.remove(filepath)

def uninstall_process() -> None:
	print("Starting uninstallation.")

	batch_file_directory : str = Path(os.path.join(os.path.dirname(os.path.abspath(__file__)))).as_posix()

	tools_directory = Path(os.path.join(batch_file_directory, "tools")).as_posix()
	if os.path.exists(tools_directory):
		query_directory(tools_directory)

	print("Uninstallation has finished.")
	print("Press enter to close.")
	input("")

def main() -> None:
	print("This is the uninstaller program for the ComfyUI Local Generation.")
	print("")
	print("This will not uninstall python or git, but will uninstall ComfyUI.")
	print("")
	print("You will be asked before it deletes any directories with the total directory size provided.")
	print("")
	print("To proceed with the uninstallation, first make sure the one-click-comfyui terminals are closed.")
	print("Once you have done so, press enter to continue.")
	print("")
	input("")
	uninstall_process()

if __name__ == '__main__':
	main()
