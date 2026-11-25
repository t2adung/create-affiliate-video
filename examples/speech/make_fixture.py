"""Create a synthetic input track for the fixture speech provider."""
import subprocess
import sys

subprocess.run(
    ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
     "anullsrc=r=16000:cl=mono", "-t", "2.5", sys.argv[1]],
    check=True,
)
