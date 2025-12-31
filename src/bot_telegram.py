# src/bot_telegram.py

import logging
import asyncio
import sys
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ConversationHandler, ContextTypes, filters

# Adiciona o diretório raiz ao path para importar nossos outros módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
try:
    import gerador_de_ideias
    import criar_video
except ImportError:
    print("ERRO: Certifique-se que os arquivos 'gerador_de_ideias.py' e 'criar_video.py' estão na mesma pasta 'src'.")
    sys.exit(1)


# --- CONFIGURAÇÕES ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
CHOOSING_THEME, TYPING_IDEA = range(2)
THEME_FILES = {canal['tema_categoria']: canal['arquivo_temas'] for canal in config.CANAIS_CONFIG}
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_TEMAS = os.path.join(BASE_DIR, "assets", "themes")

# --- FUNÇÕES DO BOT (/adicionarideia) ---
async def start_add_idea(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [[InlineKeyboardButton(theme_name, callback_data=theme_name)] for theme_name in THEME_FILES.keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Para qual categoria de tema é a sua nova ideia?', reply_markup=reply_markup)
    return CHOOSING_THEME

async def choose_theme(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    theme_choice = query.data
    context.user_data['chosen_theme'] = theme_choice
    await query.edit_message_text(text=f"Ótimo! Categoria: *{theme_choice}*.\n\nAgora, por favor, envie a sua ideia de vídeo.", parse_mode='Markdown')
    return TYPING_IDEA

async def receive_idea(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    idea_text = update.message.text
    chosen_theme = context.user_data['chosen_theme']
    file_name = THEME_FILES[chosen_theme]
    full_path = os.path.join(PASTA_TEMAS, file_name)
    try:
        with open(full_path, 'a', encoding='utf-8') as f:
            f.write(f'\n{idea_text}')
        await update.message.reply_text(f"✅ Ideia salva com sucesso em *{chosen_theme}*!", parse_mode='Markdown')
        logger.info(f"Ideia '{idea_text}' salva em {full_path}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ocorreu um erro ao salvar a ideia: {e}")
        logger.error(f"Erro ao salvar ideia em {full_path}: {e}")
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Operação cancelada.')
    context.user_data.clear()
    return ConversationHandler.END

# --- COMANDOS PRINCIPAIS DA FÁBRICA ---
async def gerar_ideias_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("🤖 Entendido! Iniciando a busca por novas ideias. Isso pode levar um minuto...")
    loop = asyncio.get_running_loop()
    try:
        await loop.run_in_executor(None, gerador_de_ideias.main)
        await update.message.reply_text("✅ Busca de ideias concluída! Novos temas foram salvos.")
    except Exception as e:
        await update.message.reply_text(f"❌ Ocorreu um erro durante a busca por ideias: {e}")

async def criar_teste_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text="🚀 Entendido! Iniciando a criação de 1 vídeo de teste. Por favor aguarde...")
    loop = asyncio.get_running_loop()
    try:
        caminhos_dos_videos = await loop.run_in_executor(None, lambda: criar_video.main(modo_teste=True))
        if caminhos_dos_videos:
            await context.bot.send_message(chat_id=chat_id, text="✅ Vídeo de teste gerado! Enviando o arquivo...")
            with open(caminhos_dos_videos[0], 'rb') as video_file:
                await context.bot.send_video(chat_id=chat_id, video=video_file, caption="Vídeo de teste pronto!")
        else:
            await context.bot.send_message(chat_id=chat_id, text="⚠️ A criação do vídeo de teste falhou ou não havia temas. Verifique o log no terminal.")
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Ocorreu um erro geral durante a criação do vídeo de teste: {e}")

async def criar_remessa_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "🏭 ATENÇÃO: Iniciando o ciclo de produção completo (9 vídeos).\n\n"
            "Este processo é MUITO demorado. Avisarei quando a remessa estiver pronta. "
            "Acompanhe o progresso pelo terminal."
        )
    )
    loop = asyncio.get_running_loop()
    try:
        caminhos_dos_videos = await loop.run_in_executor(None, lambda: criar_video.main(modo_teste=False))
        if caminhos_dos_videos:
            await context.bot.send_message(chat_id=chat_id, text=f"🎉 Produção concluída! Enviando os {len(caminhos_dos_videos)} vídeos gerados...")
            for video_path in caminhos_dos_videos:
                with open(video_path, 'rb') as video_file:
                    await context.bot.send_video(chat_id=chat_id, video=video_file, caption=os.path.basename(video_path))
        else:
            await context.bot.send_message(chat_id=chat_id, text="⚠️ A produção da remessa falhou ou não havia temas. Verifique o log no terminal.")
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Ocorreu um erro geral durante a produção da remessa: {e}")

async def upar_remessa_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("🚧 A função de upload automático ainda está em desenvolvimento.")

def main() -> None:
    """Inicia o bot e configura todos os comandos."""
    # Define timeouts mais longos diretamente no builder
    application = Application.builder().token(config.TELEGRAM_TOKEN).read_timeout(30).write_timeout(600).build()
    
    # Conversa para /adicionarideia
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('adicionarideia', start_add_idea)],
        states={
            CHOOSING_THEME: [CallbackQueryHandler(choose_theme)],
            TYPING_IDEA: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_idea)],
        },
        fallbacks=[CommandHandler('cancelar', cancel)],
    )
    
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("gerarideias", gerar_ideias_command))
    application.add_handler(CommandHandler("criarteste", criar_teste_command))
    application.add_handler(CommandHandler("criarremessa", criar_remessa_command))
    application.add_handler(CommandHandler("uparremessa", upar_remessa_command))
    
    print("Bot 'Maestro' iniciado! Controle sua fábrica de conteúdo pelo Telegram. Pressione Ctrl+C para parar.")
    application.run_polling()

if __name__ == '__main__':
    main()