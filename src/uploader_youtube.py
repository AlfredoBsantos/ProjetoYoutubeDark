# src/uploader_youtube.py

import os
import pickle
import sys
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Adiciona o diretório raiz ao path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- CONFIGURAÇÕES DE PASTAS E ARQUIVOS (COM CAMINHOS CORRIGIDOS) ---
PASTA_CREDENCIAIS = os.path.join(BASE_DIR, "credentials")
PASTA_VIDEOS_GERADOS = os.path.join(BASE_DIR, "output", "videos_gerados")
CLIENT_SECRETS_FILE = os.path.join(PASTA_CREDENCIAIS, "client_secrets.json")

# --- CONFIGURAÇÕES DA API ---
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

def get_authenticated_service(channel_id):
    """Autentica o usuário e retorna um objeto de serviço do YouTube."""
    token_file = os.path.join(PASTA_CREDENCIAIS, f'token_{channel_id}.pickle')
    creds = None

    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
            print(f"Token de acesso salvo para o canal {channel_id} em {token_file}")

    return build(API_SERVICE_NAME, API_VERSION, credentials=creds)

def upload_video(youtube, file_path, title, description, tags, category_id="20", privacy_status="private"):
    """Faz o upload de um arquivo de vídeo para o YouTube."""
    try:
        body = {
            "snippet": { "title": title, "description": description, "tags": tags, "categoryId": category_id },
            "status": { "privacyStatus": privacy_status }
        }

        media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
        request = youtube.videos().insert(part=",".join(body.keys()), body=body, media_body=media)

        print(f"Iniciando o upload do vídeo: {title}...")
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Enviado {int(status.progress() * 100)}%")
        
        print(f"✅ Upload concluído! ID do vídeo: {response.get('id')}")
        return response.get('id')

    except Exception as e:
        print(f"❌ Ocorreu um erro durante o upload: {e}")
        return None

# --- FUNÇÃO PRINCIPAL PARA TESTE ---
if __name__ == '__main__':
    print("--- INICIANDO UPLOAD DE TESTE ---")
    
    ID_DO_CANAL_PARA_AUTORIZAR = "faisca_filosofica_pt"
    youtube_service = get_authenticated_service(ID_DO_CANAL_PARA_AUTORIZAR)
    
    # Exemplo de como pegar um vídeo para teste
    nome_video_teste = "Filosofia_PT_O_estoicismo_é_a_res.mp4" # Mude para um nome de vídeo que exista
    caminho_do_video = os.path.join(PASTA_VIDEOS_GERADOS, nome_video_teste)
    
    titulo_do_video = "O Estoicismo é a Resposta? | Diálogo Filosófico"
    descricao_do_video = "Uma conversa filosófica sobre o estoicismo.\n\n#filosofia #estoicismo #shorts"
    tags_do_video = ["filosofia", "estoicismo", "shorts"]

    if os.path.exists(caminho_do_video):
        upload_video(youtube_service, caminho_do_video, titulo_do_video, descricao_do_video, tags_do_video)
    else:
        print(f"ERRO: O arquivo de vídeo de teste não foi encontrado em '{caminho_do_video}'.")

    print("\n--- TESTE DE UPLOAD CONCLUÍDO ---")