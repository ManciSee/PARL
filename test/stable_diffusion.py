import os
from decouple import config
import replicate

REPLICATE_API_TOKEN = config('REPLICATE_API_TOKEN')
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

output = replicate.run(
  "stability-ai/stable-diffusion:ac732df83cea7fff18b8472768c88ad041fa750ff7682a21affe81863cbe77e4",
  input={
    "width": 768,
    "height": 768,
    "prompt": "summer vacation plans",
    "scheduler": "K_EULER",
    "num_outputs": 1,
    "guidance_scale": 7.5,
    "num_inference_steps": 50
  }
)
print(output)