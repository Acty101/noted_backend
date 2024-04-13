import noted
import google.generativeai as genai


def predict_audio(filepath, audio_prompt, model):
    prompt = audio_prompt
    audio_file = genai.upload_file(path=filepath)
    response = model.generate_content([prompt, audio_file])
    return response.text
