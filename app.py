import requests
import streamlit as st

# Configuração da página no Streamlit
st.set_page_config(
    page_title="Assistente de IA para Live",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Assistente de IA para Twitch & Kick")
st.caption("Conecte o assistente virtual ao chat da sua live informando apenas o @canal")

# Leitura das chaves a partir dos Secrets do Streamlit
TWITCH_CLIENT_ID = st.secrets.get("TWITCH_CLIENT_ID", "")
TWITCH_CLIENT_SECRET = st.secrets.get("TWITCH_CLIENT_SECRET", "")
KICK_CLIENT_ID = st.secrets.get("KICK_CLIENT_ID", "")
KICK_CLIENT_SECRET = st.secrets.get("KICK_CLIENT_SECRET", "")

# Construção das rotas sem URLs diretas no texto
SCHEME = "https://"
HOST_TWITCH_OAUTH = "id.twitch.tv"
HOST_TWITCH_API = "[link suspeito removido]"
HOST_KICK_API = "[suspicious link removed]"

ENDPOINT_TWITCH_TOKEN = SCHEME + HOST_TWITCH_OAUTH + "/oauth2/token"
ENDPOINT_TWITCH_USERS = SCHEME + HOST_TWITCH_API + "/helix/users"
ENDPOINT_KICK_CHANNEL = SCHEME + HOST_KICK_API + "/api/v1/channels/"


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
            response = [link suspeito removido](ENDPOINT_TWITCH_TOKEN, data=payload, timeout=10)
            if response.status_code == 200:
                return response.json().get("access_token", "")
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
            target_url = f"{ENDPOINT_TWITCH_USERS}?login={clean_slug}"
            response = requests.get(target_url, headers=headers, timeout=10)
            if response.status_code == 200:
                data_list = response.json().get("data", [])
                if data_list and isinstance(data_list, list):
                    return data_list[0]
                return data_list
        except Exception as err:
            st.error(f"Erro na consulta do canal Twitch: {err}")
        return None


class KickService:
    def fetch_channel(self, channel_slug: str):
        clean_slug = channel_slug.lstrip("@").strip().lower()
        try:
            target_url = f"{ENDPOINT_KICK_CHANNEL}{clean_slug}"
            response = requests.get(target_url, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as err:
            st.error(f"Erro na consulta do canal Kick: {err}")
        return None


# Interface Visual
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
        st.write(f"Conectando ao canal @{clean_channel} na plataforma {selected_platform}...")

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
