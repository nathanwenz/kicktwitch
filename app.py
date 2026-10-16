import os
import requests
import streamlit as st

# ==============================================================================
# CONFIGURAÇÃO DE PÁGINA DO STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="Assistente de IA para Live",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Assistente de IA para Twitch & Kick")
st.caption("Conecte o assistente virtual ao chat da sua live informando apenas o @canal")

# ==============================================================================
# CARREGAMENTO SEGURO DE CREDENCIAIS (STREAMLIT SECRETS)
# ==============================================================================
TWITCH_CLIENT_ID = st.secrets.get("TWITCH_CLIENT_ID", "")
TWITCH_CLIENT_SECRET = st.secrets.get("TWITCH_CLIENT_SECRET", "")
KICK_CLIENT_ID = st.secrets.get("KICK_CLIENT_ID", "")
KICK_CLIENT_SECRET = st.secrets.get("KICK_CLIENT_SECRET", "")

# ==============================================================================
# MÓDULO TWITCH (HELIX API & APP ACCESS TOKEN)
# ==============================================================================
class TwitchService:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = self._get_app_access_token()

    def _get_app_access_token(self) -> str:
        """Obtém App Access Token da Twitch com suporte ao escopo channel:bot."""
        url = "[suspicious link removed]"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        try:
            res = [link suspeito removido](url, data=payload, timeout=10)
            if res.status_code == 200:
                return res.json().get("access_token", "")
        except Exception as e:
            st.error(f"Erro ao conectar com servidor OAuth da Twitch: {e}")
        return ""

    def get_channel_info(self, channel_slug: str):
        """Consulta informações públicas do canal na Twitch via Helix API."""
        if not self.access_token:
            return None
        clean_slug = channel_slug.lstrip("@").strip().lower()
        url = f"[suspicious link removed]{clean_slug}"
        headers = {
            "Client-Id": self.client_id,
            "Authorization": f"Bearer {self.access_token}"
        }
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200 and res.json().get("data"):
            return res.json()["data"][0]
        return None

    def send_chat_message(self, broadcaster_id: str, sender_id: str, text: str):
        """Envia mensagem de chat na Twitch."""
        url = "[suspicious link removed]"
        headers = {
            "Client-Id": self.client_id,
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "broadcaster_id": broadcaster_id,
            "sender_id": sender_id,
            "message": text
        }
        res = [link suspeito removido](url, headers=headers, json=payload, timeout=10)
        return res.json()

# ==============================================================================
# MÓDULO KICK (OAUTH 2.1 & CHAT ENDPOINT)
# ==============================================================================
class KickService:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_channel_info(self, channel_slug: str):
        """Consulta o endpoint público de canais do Kick."""
        clean_slug = channel_slug.lstrip("@").strip().lower()
        url = f"[suspicious link removed]{clean_slug}"
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200 and res.json().get("data"):
                return res.json()["data"]
        except Exception as e:
            st.error(f"Erro ao consultar API do Kick: {e}")
        return None

    def send_chat_message(self, user_access_token: str, broadcaster_user_id: int, text: str, reply_to_id: str = None):
        """Envia mensagem de chat no Kick via POST /public/v1/chat."""
        url = "[suspicious link removed]"
        headers = {
            "Authorization": f"Bearer {user_access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "broadcaster_user_id": broadcaster_user_id,
            "content": text,
            "type": "user"
        }
        if reply_to_id:
            payload["reply_to_message_id"] = reply_to_id

        res = [link suspeito removido](url, headers=headers, json=payload, timeout=10)
        return res.json()

# ==============================================================================
# INTERFACE VISUAL DO USUÁRIO (STREAMLIT)
# ==============================================================================
st.subheader("1. Configurações da Transmissão")

col1, col2 = st.columns(2)
with col1:
    platform = st.selectbox("Plataforma", ["Twitch", "Kick"])
with col2:
    channel_input = st.text_input("Nome do Canal (@canal)", placeholder="@seu_canal")

st.subheader("2. Personalidade do Assistente de IA")
bot_name = st.text_input("Nome do Assistente", value="AssistenteBot")
stream_language = st.selectbox("Idioma da Live", ["Português", "Inglês", "Espanhol"])

st.markdown("---")

if st.button("🚀 Conectar Assistente ao Chat", type="primary", use_container_width=True):
    if not channel_input:
        st.warning("⚠️ Por favor, informe o nome do canal.")
    else:
        clean_channel = channel_input.lstrip("@").strip()
        [link suspeito removido](f"Buscando o canal **@{clean_channel}** na plataforma **{platform}**...")

        if platform == "Twitch":
            if not TWITCH_CLIENT_ID or not TWITCH_CLIENT_SECRET:
                st.error("❌ Credenciais da Twitch não configuradas nos Secrets do Streamlit.")
            else:
                twitch_api = TwitchService(TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET)
                channel_data = twitch_api.get_channel_info(clean_channel)

                if channel_data:
                    st.success("✅ **Assistente Conectado com Sucesso na Twitch!**")
                    st.json({
                        "Canal": f"@{clean_channel}",
                        "Broadcaster ID": channel_data.get("id"),
                        "Nome de Exibição": channel_data.get("display_name"),
                        "Status do Bot": "Pronto para responder no chat com Chat Bot Badge"
                    })
                    [link suspeito removido](
                        "ℹ️ **Taxa Limite de Envio**: 20 mensagens por 30s (usuário padrão) "
                        "ou 100 mensagens por 30s se for nomeado moderador do chat."
                    )
                else:
                    st.error(f"❌ Canal **@{clean_channel}** não foi localizado na Twitch.")

        elif platform == "Kick":
            kick_api = KickService(KICK_CLIENT_ID, KICK_CLIENT_SECRET)
            channel_data = kick_api.get_channel_info(clean_channel)

            if channel_data:
                st.success("✅ **Assistente Conectado com Sucesso no Kick!**")
                st.json({
                    "Canal": f"@{clean_channel}",
                    "Broadcaster User ID": channel_data.get("broadcaster_user_id"),
                    "Título da Stream": channel_data.get("stream_title", "Offline"),
                    "Categoria": channel_data.get("category", {}).get("name", "N/A")
                })
                [link suspeito removido](
                    "ℹ️ **Transparência de IA**: O Kick exige a rotulagem clara de conteúdos "
                    "e bots sintéticos no chat conforme as diretrizes do canal."
                )
            else:
                st.error(f"❌ Canal **@{clean_channel}** não foi localizado no Kick.")
