
from tqdm import tqdm

import subprocess
import requests

def is_ffmpeg_gpu_available() -> bool:
	try:
		result = subprocess.run(
			['ffmpeg', '-hwaccels'],
			capture_output=True,
			text=True,
			check=True
		)
		if result.stdout.strip():
			print("GPU-accelerated FFmpeg is available:")
			print(result.stdout)
			return True
		else:
			print("No GPU acceleration support found.")
			return False
	except subprocess.CalledProcessError as e:
		print("FFmpeg is not installed or not accessible.")
		print("Error message:", e.stderr)
		return False

def download_file(url: str, dest: str, chunk_size : int = 256) -> None:
	response = requests.get(url, stream=True)
	response.raise_for_status()
	total_size = int(response.headers.get('content-length', 0))
	with open(dest, 'wb') as file:
		progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, desc=dest)
		for data in response.iter_content(chunk_size=chunk_size):
			file.write(data)
			progress_bar.update(len(data))
		progress_bar.close()
