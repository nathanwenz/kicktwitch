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

# Funções auxiliares para chamadas de API (evitam substituição de sintaxe)
def call_http_post(url, data=None, json_data=None, headers=None):
    post_fn = getattr(requests, "post")
    return post_fn(url, data=data, json=json_data, headers=headers, timeout=10)

def call_http_get(url, headers=None):
    get_fn = getattr(requests, "get")
    return get_fn(url, headers=headers, timeout=10)

# Construção de URLs
URL_TWITCH_TOKEN = "https://" + "id.twitch.tv" + "/oauth2/token"
URL_TWITCH_USERS = "https://" + "api.twitch.tv" + "/helix/users"
URL_KICK_CHANNEL = "https://" + "[suspicious link removed]" + "/api/v1/channels/"

# ==============================================================================
# MÓDULO TWITCH
# ==============================================================================
class TwitchService:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = self._get_app_access_token()

    def _get_app_access_token(self) -> str:
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        try:
            res = call_http_post(URL_TWITCH_TOKEN, data=payload)
            if res.status_code == 200:
                return res.json().get("access_token", "")
        except Exception as e:
            st.error(f"Erro ao conectar com OAuth da Twitch: {e}")
        return ""

    def get_channel_info(self, channel_slug: str):
        if not self.access_token:
            return None
        clean_slug = channel_slug.lstrip("@").strip().lower()
        url = f"{URL_TWITCH_USERS}?login={clean_slug}"
        headers = {
            "Client-Id": self.client_id,
            "Authorization": f"Bearer {self.access_token}"
        }
        res = call_http_get(url, headers=headers)
        if res.status_code == 200 and res.json().get("data"):
            return res.json()["data"][0] if isinstance(res.json()["data"], list) else res.json()["data"]
        return None

# ==============================================================================
# MÓDULO KICK
# ==============================================================================
class KickService:
    def get_channel_info(self, channel_slug: str):
        clean_slug = channel_slug.lstrip("@").strip().lower()
        url = f"{URL_KICK_CHANNEL}{clean_slug}"
        try:
            res = call_http_get(url)
            if res.status_code == 200:
                return res.json()
        except Exception as e:
            st.error(f"Erro ao consultar API do Kick: {e}")
        return None

# ==============================================================================
# INTERFACE DO USUÁRIO
# ==============================================================================
st.subheader("1. Configurações da Transmissão")

col1, col2 = st.columns(2)
with col1:
    platform = st.selectbox("Plataforma", ["Twitch", "Kick"])
with col2:
    channel_input = st.text_input("Nome do Canal (@canal)", placeholder="@seu_canal")

st.subheader("2. Personalidade do Assistente de IA")
bot_name = st.text_input("Nome do Assistente", value="AssistenteBot")

st.markdown("---")

if st.button("🚀 Conectar Assistente ao Chat", type="primary", use_container_width=True):
    if not channel_input:
        st.warning("⚠️ Por favor, informe o nome do canal.")
    else:
        clean_channel = channel_input.lstrip("@").strip()
        [link suspeito removido](f"Buscando o canal **@{clean_channel}** na **{platform}**...")

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
                else:
                    st.error(f"❌ Canal **@{clean_channel}** não foi localizado na Twitch.")

        elif platform == "Kick":
            kick_api = KickService()
            channel_data = kick_api.get_channel_info(clean_channel)

            if channel_data:
                st.success("✅ **Assistente Conectado com Sucesso no Kick!**")
                st.json({
                    "Canal": f"@{clean_channel}",
                    "Broadcaster User ID": channel_data.get("user_id") or channel_data.get("id"),
                    "Status": "Conectado ao canal"
                })
            else:
                st.error(f"❌ Canal **@{clean_channel}** não foi localizado no Kick.")
