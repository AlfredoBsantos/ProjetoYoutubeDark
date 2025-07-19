import os
import random
import re
from moviepy.editor import *
from moviepy.audio.fx.all import audio_loop
from TTS.api import TTS
import google.generativeai as genai
import torch
import whisper
from deep_translator import GoogleTranslator

# --- 1. CONFIGURAÇÃO INICIAL ---
GOOGLE_API_KEY = 'AIzaSyC-teU44gErrUY1xWpKd5VZD00m9jbynI8' 
genai.configure(api_key=GOOGLE_API_KEY)

# --- CONFIGURAÇÃO DOS CANAIS ---
CANAIS_CONFIG = [
    {
        "tema_categoria": "Filosofia",
        "arquivo_temas": "temas_filosofia.txt"
    },
    {
        "tema_categoria": "Desenvolvimento Pessoal",
        "arquivo_temas": "temas_desenvolvimento_pessoal.txt"
    },
    {
        "tema_categoria": "Curiosidades",
        "arquivo_temas": "temas_curiosidades.txt"
    }
]

# --- CONFIGURAÇÃO DE PERSONAGENS COM PERSONALIDADES ---
PERSONAGENS = [
    {
        "nome": "Braian Griffin",
        "arquivo_voz": "amostra_BraianGriffin.wav",
        "arquivo_imagem": "personagens_img/ModeloBraianGriffin.png",
        "personalidade": "Você é um intelectual articulado, um pouco arrogante e pretensioso. Use um vocabulário complexo e fale como a voz da razão, mas com um toque de sarcasmo."
    },
    {
        "nome": "Clancy Gospel",
        "arquivo_voz": "amostra_ClancyGospel.wav",
        "arquivo_imagem": "personagens_img/modeloClancyGospel.png",
        "personalidade": "Você é um space-caster entusiasmado, curioso e filosófico. Fale de forma aberta e maravilhada, como se estivesse descobrindo o universo a cada frase."
    },
    {
        "nome": "Mae Gospel",
        "arquivo_voz": "amostra_MaeGospel.wav",
        "arquivo_imagem": "personagens_img/ModeloMaeGospel.png",
        "personalidade": "Você é uma figura materna sábia, calma e que aceita a vida e a morte. Fale com autoridade tranquila, amor e uma profunda compreensão da realidade."
    },
    {
        "nome": "Mob",
        "arquivo_voz": "amostra_mob.wav",
        "arquivo_imagem": "personagens_img/ModeloMob.png",
        "personalidade": "Você é Shigeo Kageyama (Mob). Fale de forma quieta, reservada e um pouco socialmente desajeitada. Seja simples, direto e muito empático em suas palavras."
    },
    {
        "nome": "Mordecai",
        "arquivo_voz": "amostra_Mordecai.wav",
        "arquivo_imagem": "personagens_img/ModeloMordecai.png",
        "personalidade": "Você é um jovem adulto relaxado e geralmente o mais responsável da dupla. Fale de forma casual, um pouco exasperada, como se estivesse tentando manter a calma no meio do caos."
    },
    {
        "nome": "Morty",
        "arquivo_voz": "amostra_Morty.wav",
        "arquivo_imagem": "personagens_img/ModeloMorty.png",
        "personalidade": "Você é Morty Smith. Fale de forma ansiosa, com hesitações e gaguejos ocasionais (ex: 'Ah, geez...'). Expresse dúvida e um pouco de pânico, mas com um bom coração."
    },
    {
        "nome": "Peter Griffin",
        "arquivo_voz": "amostra_PiterGriffin.wav",
        "arquivo_imagem": "personagens_img/ModeloPitterGriffin.png",
        "personalidade": "Você é Peter Griffin. Fale de forma alta, impulsiva e com uma confiança boba. Use frases curtas e diretas, como se a ideia tivesse acabado de surgir na sua cabeça."
    },
    {
        "nome": "Reigen Arataka",
        "arquivo_voz": "amostra_reigen.wav",
        "arquivo_imagem": "personagens_img/ModeloReigen.png",
        "personalidade": "Você é um mestre da persuasão, carismático e confiante. Fale de forma eloquente e com um toque de malandragem, como um grande vendedor com um coração de ouro escondido."
    },
    {
        "nome": "Rick Sanchez",
        "arquivo_voz": "amostra_Rick.wav",
        "arquivo_imagem": "personagens_img/ModeloRick.png",
        "personalidade": "Você é Rick Sanchez. Seja cínico, niilista, brilhante e arrogante. Fale rapidamente, com um tom desdenhoso, sarcasmo e pausas para arrotos ou hesitações de bêbado."
    },
    {
        "nome": "Rigby",
        "arquivo_voz": "amostra_Rigby.wav",
        "arquivo_imagem": "personagens_img/ModeloRigby.png",
        "personalidade": "Você é Rigby. Fale de forma impulsiva, um pouco preguiçosa e hiperativa. Use frases curtas e animadas, talvez um pouco choramingonas ou excessivamente empolgadas."
    },
]

# --- CONFIGURAÇÃO DE PASTAS ---
PASTA_VIDEOS = "videos_parkour"
PASTA_MUSICAS = "musicas"
PASTA_SAIDA = "videos_gerados"
PASTA_IMAGENS_PERSONAGENS = "personagens_img"

os.makedirs(PASTA_SAIDA, exist_ok=True)
os.makedirs(PASTA_IMAGENS_PERSONAGENS, exist_ok=True)


# --- 2. FUNÇÕES AUXILIARES ---

def get_random_file(folder_path):
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    if not files: raise ValueError(f"A pasta está vazia: {folder_path}")
    return os.path.join(folder_path, random.choice(files))

def get_random_theme(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        themes = f.readlines()
    if not themes: raise ValueError(f"O arquivo de temas está vazio: {file_path}")
    return random.choice(themes).strip()

# --- FUNÇÃO DE SCRIPT MODIFICADA ---
def generate_script(theme, personagem):
    """Gera um roteiro usando a API do Gemini com a personalidade do personagem."""
    print(f"\nGerando roteiro para o tema: '{theme}' com a personalidade de {personagem['nome']}")
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Prompt dinâmico que inclui a personalidade
    prompt = f"""
    Aja como o personagem a seguir e crie um monólogo curto e impactante de até 45 segundos sobre o tema proposto.
    O texto final deve ser limpo, sem formatação, sem asteriscos, sem parênteses e sem nome de personagem, apenas o diálogo puro.

    PERSONAGEM: {personagem['nome']}
    PERSONALIDADE: {personagem['personalidade']}
    TEMA: '{theme}'

    Monólogo:
    """
    
    response = model.generate_content(prompt)
    
    # Limpeza final do roteiro para remover caracteres indesejados
    texto_limpo = response.text.strip()
    texto_limpo = re.sub(r'[\*()\[\]]', '', texto_limpo) # Remove *, (), []
    texto_limpo = texto_limpo.replace('"', '') # Remove aspas
    
    print("Roteiro gerado e limpo com sucesso!")
    return texto_limpo

def translate_script(text, target_language):
    if target_language == 'pt': return text
    print(f"Traduzindo roteiro para o idioma: {target_language}...")
    try:
        return GoogleTranslator(source='auto', target=target_language).translate(text)
    except Exception as e:
        print(f"Erro na tradução: {e}")
        return text

def generate_audio(script_text, sample_voice_path, language, output_path):
    print(f"Gerando áudio em '{language}' com a voz de referência: {sample_voice_path}")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False).to(device)
    tts.tts_to_file(text=script_text, file_path=output_path, speaker_wav=sample_voice_path, language=language)
    print(f"Áudio clonado salvo em: {output_path}")

def generate_synced_captions(audio_path):
    print("Carregando modelo Whisper...")
    model = whisper.load_model("base")
    print("Transcrevendo áudio para gerar timestamps...")
    result = model.transcribe(audio_path, word_timestamps=False)
    print("Legendas e timestamps gerados.")
    return result['segments']


# --- 3. FUNÇÃO PRINCIPAL DE MONTAGEM ---
def create_video(tema_categoria, tema_escolhido, roteiro_base_pt, idioma, personagem_escolhido):
    try:
        print(f"\n--- INICIANDO CRIAÇÃO DO VÍDEO ---")
        print(f"| Categoria: {tema_categoria}")
        print(f"| Idioma: {idioma.upper()}")
        print(f"| Personagem: {personagem_escolhido['nome']}")
        
        roteiro_traduzido = translate_script(roteiro_base_pt, idioma)
        
        caminho_audio_narracao = os.path.join(PASTA_SAIDA, f"narracao_{idioma}.wav")
        generate_audio(roteiro_traduzido, personagem_escolhido['arquivo_voz'], idioma, caminho_audio_narracao)
        
        segments = generate_synced_captions(caminho_audio_narracao)
        caminho_video_bg = get_random_file(PASTA_VIDEOS)
        caminho_musica_bg = get_random_file(PASTA_MUSICAS)
        
        print("Iniciando montagem do vídeo...")
        video_clip = VideoFileClip(caminho_video_bg)
        narracao_clip = AudioFileClip(caminho_audio_narracao)
        musica_clip = AudioFileClip(caminho_musica_bg).volumex(0.1)

        video_clip = video_clip.subclip(0, narracao_clip.duration)
        final_music = audio_loop(musica_clip, duration=narracao_clip.duration)
        audio_final = CompositeAudioClip([narracao_clip, final_music])
        video_com_audio = video_clip.set_audio(audio_final)

        imagem_personagem_clip = (ImageClip(personagem_escolhido['arquivo_imagem'])
                                  .set_duration(video_com_audio.duration)
                                  .resize(height=video_com_audio.h * 0.25)
                                  .set_position(("right", "top")))

        caption_clips = []
        for segment in segments:
            start_time, end_time, text = segment['start'], segment['end'], segment['text'].strip().upper()
            caption = TextClip(text, fontsize=32, color='yellow', font='Calibri-Bold', stroke_color='black', stroke_width=2, size=(video_com_audio.w*0.8, None), method='caption')
            caption = caption.set_start(start_time).set_duration(end_time - start_time)
            caption = caption.set_position(('center', 0.75), relative=True)
            caption_clips.append(caption)

        video_final = CompositeVideoClip([video_com_audio, imagem_personagem_clip] + caption_clips)
        
        safe_theme_name = re.sub(r'[\\/*?:"<>|]', '', tema_escolhido)[:20].replace(' ', '_')
        nome_personagem_safe = personagem_escolhido['nome'].replace(' ','')
        nome_arquivo_saida = f"{tema_categoria}_{idioma.upper()}_{nome_personagem_safe}_{safe_theme_name}.mp4"
        caminho_arquivo_saida = os.path.join(PASTA_SAIDA, nome_arquivo_saida)
        
        video_final.write_videofile(caminho_arquivo_saida, codec='libx264', audio_codec='aac')
        
        print(f"✅ VÍDEO GERADO COM SUCESSO: {caminho_arquivo_saida}")

    except Exception as e:
        print(f"❌ Ocorreu um erro ao criar o vídeo para o idioma '{idioma}': {e}")


# --- 4. EXECUTAR O SCRIPT ---
if __name__ == '__main__':

    # --- MODO DE PRODUÇÃO (gera 9 vídeos) ---
    # Quando quiser gerar todos os vídeos, apague o "Modo de Teste" abaixo
    # e remova os comentários deste bloco.
    
    # for canal in CANAIS_CONFIG:
    #     tema_base = get_random_theme(canal['arquivo_temas'])
    #     personagem_do_tema = random.choice(PERSONAGENS)
    #     roteiro_base_pt = generate_script(tema_base, personagem_do_tema)
        
    #     for idioma in ['pt', 'en', 'es']:
    #         create_video(
    #             tema_categoria=canal['tema_categoria'],
    #             tema_escolhido=tema_base,
    #             roteiro=roteiro_base_pt, # ERRO CORRIGIDO AQUI
    #             idioma=idioma,
    #             personagem_escolhido=personagem_do_tema
    #         )
            
    # print("\n🎉 Ciclo de produção concluído!")


    # --- MODO DE TESTE (gera 1 vídeo) ---
    # Use este bloco para testes rápidos.
    print("--- RODANDO EM MODO DE TESTE (1 VÍDEO) ---")

    # 1. Escolha os parâmetros para o teste (você pode mudar os números e o idioma)
    canal_teste = CANAIS_CONFIG[0]           # Pega o primeiro canal da lista (Filosofia)
    personagem_teste = PERSONAGENS[8]        # Pega o Rick Sanchez da lista (o nono item, índice 8)
    idioma_teste = 'pt'                      # Define o idioma para o teste

    # 2. Gera o conteúdo para o teste
    tema_teste = get_random_theme(canal_teste['arquivo_temas'])
    roteiro_teste = generate_script(tema_teste, personagem_teste)

    # 3. Chama a função de criar vídeo apenas uma vez
    create_video(
        tema_categoria=canal_teste['tema_categoria'],
        tema_escolhido=tema_teste,
        roteiro_base_pt=roteiro_teste, # Passa o roteiro gerado
        idioma=idioma_teste,
        personagem_escolhido=personagem_teste
    )
    
    print("\n--- MODO DE TESTE CONCLUÍDO ---")

