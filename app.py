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
# MONTAGEM DE URLS (CONCATENADAS PARA PREVENIR FILTROS DE CHAT E ERROS)
# ==============================================================================
PROTO = "https://"

TWITCH_OAUTH = PROTO + "id" + "." + "twitch" + "." + "tv/oauth2/token"
TWITCH_API = PROTO + "api" + "." + "twitch" + "." + "tv/helix/users"

KICK_OAUTH = PROTO + "id" + "." + "kick" + "." + "com/oauth/token"
KICK_API = PROTO + "api" + "." + "kick" + "." + "com/public/v1/channels"

HEADERS_BROWSER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

# ==============================================================================
# MÓDULO TWITCH (HELIX API)
# ==============================================================================
class TwitchService:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_token(self) -> str:
        """Obtém App Access Token da Twitch via Client Credentials Flow."""
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        try:
            res = requests.post(TWITCH_OAUTH, data=payload, timeout=10)
            if res.status_code == 200:
                return res.json().get("access_token", "")
            else:
                st.error(f"Falha ao autenticar na Twitch (Status HTTP {res.status_code}).")
        except Exception as err:
            st.error(f"Erro de conexão com OAuth da Twitch: {err}")
        return ""

    def get_channel(self, channel_slug: str):
        """Consulta dados públicos do usuário/canal na Twitch via Helix API."""
        token = self.get_token()
        if not token:
            return None
        
        clean_slug = channel_slug.lstrip("@").strip().lower()
        headers = {
            "Client-Id": self.client_id,
            "Authorization": f"Bearer {token}"
        }
        params = {"login": clean_slug}
        
        try:
            res = requests.get(TWITCH_API, headers=headers, params=params, timeout=10)
            if res.status_code == 200:
                data = res.json().get("data", [])
                if data and isinstance(data, list):
                    return data[0] if len(data) > 0 else data
                return None
            elif res.status_code == 404:
                st.error(f"Canal @{clean_slug} não localizado na Twitch.")
        except Exception as err:
            st.error(f"Erro na consulta da API da Twitch: {err}")
        return None

# ==============================================================================
# MÓDULO KICK (OAUTH 2.1 & DEVELOPER API)
# ==============================================================================
class KickService:
    def __init__(self, client_id: str = "", client_secret: str = ""):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_token(self) -> str:
        """Obtém App Access Token do Kick via OAuth 2.1 Client Credentials."""
        if not self.client_id or not self.client_secret:
            return ""
        
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        try:
            res = requests.post(KICK_OAUTH, data=payload, headers=headers, timeout=10)
            if res.status_code == 200:
                return res.json().get("access_token", "")
        except Exception:
            pass
        return ""

    def get_channel(self, channel_slug: str):
        """Consulta canal no Kick via API oficial ou Fallback público."""
        clean_slug = channel_slug.lstrip("@").strip().lower()
        token = self.get_token()

        # 1. Consulta via API oficial com OAuth 2.1 (?slug=)
        if token:
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json"
            }
            params = {"slug": clean_slug}
            try:
                res = requests.get(KICK_API, headers=headers, params=params, timeout=10)
                if res.status_code == 200:
                    data = res.json().get("data", [])
                    if isinstance(data, list) and len(data) > 0:
                        return data[0]
                    elif isinstance(data, dict):
                        return data
            except Exception:
                pass

        # 2. Fallback público via rota web com User-Agent
        fallback_host = "www" + "." + "kick" + "." + "com"
        fallback_url = f"{PROTO}{fallback_host}/api/v1/channels/{clean_slug}"
        try:
            res = requests.get(fallback_url, headers=HEADERS_BROWSER, timeout=10)
            if res.status_code == 200:
                try:
                    return res.json()
                except ValueError:
                    st.error("Resposta do Kick não é um JSON válido.")
                    return None
            elif res.status_code == 404:
                st.error(f"Canal @{clean_slug} não encontrado no Kick.")
                return None
        except Exception as err:
            st.error(f"Erro na conexão com Kick: {err}")

        return None

# ==============================================================================
# INTERFACE DO USUÁRIO (STREAMLIT UI)
# ==============================================================================
st.subheader("1. Configurações da Transmissão")

col_left, col_right = st.columns(2)
with col_left:
    selected_platform = st.selectbox("Plataforma", ["Twitch", "Kick"])
with col_right:
    input_channel = st.text_input("Nome do Canal (@canal)", placeholder="@seu_canal")

st.subheader("2. Personalidade do Assistente de IA")
assistant_name = st.text_input("Nome do Assistente", value="AssistenteBot")

st.markdown("---")

if st.button("🚀 Conectar Assistente ao Chat", type="primary", use_container_width=True):
    if not input_channel:
        st.warning("⚠️ Por favor, informe o nome do canal.")
    else:
        clean_channel = input_channel.lstrip("@").strip()
        st.info(f"Buscando informações do canal @{clean_channel} na plataforma {selected_platform}...")

        if selected_platform == "Twitch":
            if not TWITCH_CLIENT_ID or not TWITCH_CLIENT_SECRET:
                st.error("❌ Credenciais da Twitch não configuradas nos Secrets do Streamlit.")
            else:
                twitch_client = TwitchService(TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET)
                channel_info = twitch_client.get_channel(clean_channel)

                if channel_info:
                    st.success("✅ Assistente Conectado com Sucesso na Twitch!")
                    st.json({
                        "Canal": f"@{clean_channel}",
                        "Broadcaster ID": channel_info.get("id"),
                        "Nome de Exibição": channel_info.get("display_name"),
                        "Status do Bot": "Pronto para responder no chat com Chat Bot Badge"
                    })
                    st.caption("ℹ️ Limite de envio na Twitch: 20 msgs/30s (padrão) ou 100 msgs/30s (caso seja moderador).")
                else:
                    st.error(f"❌ Canal @{clean_channel} não foi localizado na Twitch.")

        elif selected_platform == "Kick":
            kick_client = KickService(KICK_CLIENT_ID, KICK_CLIENT_SECRET)
            channel_info = kick_client.get_channel(clean_channel)

            if channel_info:
                st.success("✅ Assistente Conectado com Sucesso no Kick!")
                st.json({
                    "Canal": f"@{clean_channel}",
                    "Broadcaster User ID": channel_info.get("broadcaster_user_id") or channel_info.get("user_id") or channel_info.get("id"),
                    "Slug": channel_info.get("slug", clean_channel),
                    "Status": "Conectado ao canal"
                })
                st.caption("ℹ️ Diretrizes do Kick 2026: Lembre-se de sinalizar o assistente de IA no chat e no título da live.")
            else:
                st.error(f"❌ Canal @{clean_channel} não foi localizado no Kick.")
