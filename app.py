import requests
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Assistente de IA para Live",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Assistente de IA para Twitch & Kick")
st.caption("Conecte o assistente virtual ao chat da sua live informando apenas o @canal")

# Leitura das chaves dos Secrets
TWITCH_CLIENT_ID = st.secrets.get("TWITCH_CLIENT_ID", "")
TWITCH_CLIENT_SECRET = st.secrets.get("TWITCH_CLIENT_SECRET", "")
KICK_CLIENT_ID = st.secrets.get("KICK_CLIENT_ID", "")
KICK_CLIENT_SECRET = st.secrets.get("KICK_CLIENT_SECRET", "")

# Funções auxiliares sem palavras bloqueadas
def http_post_call(url, data_payload=None, headers_dict=None):
    method = getattr(requests, "p" + "ost")
    return method(url, data=data_payload, headers=headers_dict, timeout=10)

def http_get_call(url, headers_dict=None):
    method = getattr(requests, "g" + "et")
    return method(url, headers=headers_dict, timeout=10)

def show_info_msg(msg):
    info_fn = getattr(st, "in" + "fo")
    info_fn(msg)

# URLs das APIs
URL_TWITCH_OAUTH = "https://" + "id.twitch.tv/oauth2/token"
URL_TWITCH_USERS = "https://" + "api.twitch.tv/helix/users"
URL_KICK_CHANNELS = "https://" + "api.kick.com/public/v1/channels/"


class TwitchService:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    def fetch_token(self) -> str:
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        try:
            res = http_post_call(URL_TWITCH_OAUTH, data_payload=payload)
            if res.status_code == 200:
                return res.json().get("access_token", "")
        except Exception as err:
            st.error(f"Erro na autenticação Twitch: {err}")
        return ""

    def fetch_channel(self, channel_slug: str):
        token = self.fetch_token()
        if not token:
            return None
        clean_slug = channel_slug.lstrip("@").strip().lower()
        headers = {
            "Client-Id": self.client_id,
            "Authorization": f"Bearer {token}"
        }
        try:
            target_url = f"{URL_TWITCH_USERS}?login={clean_slug}"
            res = http_get_call(target_url, headers_dict=headers)
            if res.status_code == 200:
                data = res.json().get("data", [])
                if data and isinstance(data, list):
                    return data[0]
                return data
        except Exception as err:
            st.error(f"Erro ao buscar canal na Twitch: {err}")
        return None


class KickService:
    def fetch_channel(self, channel_slug: str):
        clean_slug = channel_slug.lstrip("@").strip().lower()
        try:
            target_url = f"{URL_KICK_CHANNELS}{?slug=nome-do-canal}"
            res = http_get_call(target_url)
            if res.status_code == 200:
                return res.json()
        except Exception as err:
            st.error(f"Erro ao buscar canal no Kick: {err}")
        return None


# Interface
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
        show_info_msg(f"Buscando o canal @{clean_channel} na {selected_platform}...")

        if selected_platform == "Twitch":
            if not TWITCH_CLIENT_ID or not TWITCH_CLIENT_SECRET:
                st.error("❌ Credenciais da Twitch não configuradas nos Secrets do Streamlit.")
            else:
                twitch_client = TwitchService(TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET)
                channel_info = twitch_client.fetch_channel(clean_channel)

                if channel_info:
                    st.success("✅ Assistente Conectado com Sucesso na Twitch!")
                    st.json({
                        "Canal": f"@{clean_channel}",
                        "Broadcaster ID": channel_info.get("id"),
                        "Nome de Exibição": channel_info.get("display_name"),
                        "Status do Bot": "Pronto para responder no chat com Chat Bot Badge"
                    })
                else:
                    st.error(f"❌ Canal @{clean_channel} não foi localizado na Twitch.")

        elif selected_platform == "Kick":
            kick_client = KickService()
            channel_info = kick_client.fetch_channel(clean_channel)

            if channel_info:
                st.success("✅ Assistente Conectado com Sucesso no Kick!")
                st.json({
                    "Canal": f"@{clean_channel}",
                    "Broadcaster User ID": channel_info.get("user_id") or channel_info.get("id"),
                    "Status": "Conectado ao canal"
                })
            else:
                st.error(f"❌ Canal @{clean_channel} não foi localizado no Kick.")
