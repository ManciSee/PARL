
from llama_cpp import Llama

# Put the location of to the GGUF model that you've downloaded from HuggingFace here
model_path = "/home/salvo/Scrivania/llama-2-7b-chat.Q4_K_M.gguf"

# Create a llama model
model = Llama(model_path=model_path)

user_message = "Generate a list of 5 funny dog names, write only the name, not other text. Start writing Cavallo pazzo and next the name of the dogs"

prompt = f"""<s>[INST] <<SYS>>
<</SYS>>
{user_message} [/INST]"""

prompt = f"{user_message}"

# Model parameters
max_tokens = 100

# Run the model
output = model(prompt, max_tokens=max_tokens, echo=True)
generated_text = output['choices'][0]['text']

# Remove user's message from the generated text

# Print the model output
print(generated_text)

# Save the model output to a text file
output_file_path = "output.txt"
with open(output_file_path, "w", encoding="utf-8") as output_file:
    output_file.write(generated_text)

print(f"Model output saved to: {output_file_path}")
