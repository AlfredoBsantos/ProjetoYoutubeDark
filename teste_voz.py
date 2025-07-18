from TTS.api import TTS
import torch

# Verifica se uma GPU está disponível e define o dispositivo
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Usando dispositivo: {device}")

# Inicializa o TTS com um modelo pré-treinado em português
# A primeira vez que rodar, ele vai baixar o modelo. Pode demorar um pouco.
print("Carregando modelo TTS... (Isso pode levar alguns minutos na primeira vez)")
tts = TTS(model_name="tts_models/pt/cv/vits", progress_bar=True).to(device)
print("Modelo carregado.")

# Texto para ser transformado em áudio
texto_narracao = "Finalmente, o teste definitivo. Se você está ouvindo esta voz, significa que a instalação local foi um sucesso e a base para a automação de vídeos está pronta."

# Gera e salva o arquivo de áudio
print("Gerando áudio...")
tts.tts_to_file(text=texto_narracao, file_path="narracao_teste.wav")
print("Arquivo 'narracao_teste.wav' salvo com sucesso na sua pasta!")