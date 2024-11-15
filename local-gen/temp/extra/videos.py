
import os
import subprocess

def extract_video_frames(video_filepath : str, output_directory : str, fps : int = 1, nth_frame : int = 1) -> bool:
	os.makedirs(output_directory, exist_ok=True)
	output_pattern : str = os.path.join(output_directory, f"frame_%04d.png")
	command : list[str] = ['ffmpeg', '-hwaccel', 'cuda', '-i', video_filepath, '-vf', f'fps={fps},select=not(mod(n\,{nth_frame}))', output_pattern]
	try:
		# Run the FFmpeg command
		process = subprocess.run(command, check=True)
		# Check if the process was successful
		return process.returncode == 0
	except Exception as e:
		print(f"An error occurred: {e}")
		return False
