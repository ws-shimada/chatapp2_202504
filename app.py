import streamlit as st
from streamlit_chat import message
from langchain_openai.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts.chat import (
    ChatPromptTemplate,
    MessagesPlaceholder, 
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

# 時間管理
from time import sleep
import datetime
import pytz # タイムゾーンに直せるやつ
global now # PCから現在時刻
now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))

# firebase
import firebase_admin
from google.oauth2 import service_account
from google.cloud import firestore
import json

# モデルのインスタンス生成
chat = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=0,
    api_key= st.secrets.openai_api_key
)

if not "memory" in st.session_state:
    st.session_state.memory = ConversationBufferWindowMemory(k=8, return_messages=True)

# システムプロンプトを読み込み
fname = "prompt.txt"
with open(fname, 'r', encoding='utf-8') as f:
    systemprompt = f.read()

# プロンプト設定
template = systemprompt
st.session_state.prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(template),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{input}")
])

# チェインを設定
conversation = ConversationChain(llm=chat, memory=st.session_state.memory, prompt=st.session_state.prompt)

# Firebase 設定の読み込み
key_dict = json.loads(st.secrets["firebase"]["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
project_id = key_dict["project_id"]
db = firestore.Client(credentials=creds, project=project_id)

# 何かクエリを返す


# ID入力
def input_id():
    if not "user_id" in st.session_state:
        st.session_state.user_id = "hogehoge"
    with st.form("id_form", enter_to_submit=False):
        user_id = st.text_input('idを入力してください')
        submit_id = st.form_submit_button(
            label="送信",
            type="primary")
    if submit_id:
        st.session_state.user_id = user_id
        st.session_state.state = 2
        st.rerun()

# 入力時の動作
def click_to_submit():
    # 待機中にも履歴を表示
    chat_placeholder = st.empty()
    with chat_placeholder.container():
        for msg in st.session_state.log:
            if msg["role"] == "user":
                message(msg["content"], is_user=True, avatar_style="adventurer", seed="Nala")
            else:
                message(msg["content"], is_user=False, avatar_style="micah")
    with st.spinner("相手の返信を待っています…。"):
        st.session_state.send_time = str(datetime.datetime.now(pytz.timezone('Asia/Tokyo')))
        st.session_state.response = conversation.predict(input=st.session_state.user_input)
        # st.session_state.memory.save_context({"input": st.session_state.user_input}, {"output": st.session_state.response})
        st.session_state.log.append({"role": "AI", "content": st.session_state.response})
        sleep(5)
        st.session_state.return_time = str(datetime.datetime.now(pytz.timezone('Asia/Tokyo')))
        doc_ref = db.collection(str(st.session_state.user_id)).document(str(st.session_state.talktime))
        doc_ref.set({
            "Human": st.session_state.user_input,
            "AI_": st.session_state.response,
            "Human_meg_sended": st.session_state.send_time,
            "AI_meg_returned": st.session_state.return_time,
        })
        st.session_state.talktime += 1
        st.session_state.state = 2
        st.rerun()

# チャット画面
def chat_page():
    if not "talktime" in st.session_state:
        st.session_state.talktime = 0
    if not "log" in st.session_state:
        st.session_state.log = []
    chat_placeholder = st.empty()
    with chat_placeholder.container():
        for msg in st.session_state.log:
            if msg["role"] == "user":
                message(msg["content"], is_user=True, avatar_style="adventurer", seed="Nala")
            else:
                message(msg["content"], is_user=False, avatar_style="micah")
    if st.session_state.talktime < 5:
        if not "user_input" in st.session_state:
            st.session_state.user_input = "hogehoge"
        with st.container():
            with st.form("chat_form", clear_on_submit=True, enter_to_submit=False):
                user_input = st.text_area('意見を入力して下さい')
                submit_msg = st.form_submit_button(
                    label="送信",
                    type="primary")
            if submit_msg:
                st.session_state.user_input = user_input
                st.session_state.log.append({"role": "user", "content": st.session_state.user_input})
                st.session_state.state = 3
                st.rerun()
    elif st.session_state.talktime == 5:
        url = "https://www.nagoya-u.ac.jp/"
        # url = "https://survey.qualtrics.com/jfe/form/SV_123456789?ソース=Facebook&Campaign=モバイル"
        st.markdown(
            f"""
            会話は終了しました。以下のリンクをクリックしてアンケートに回答してください。  
            <a href="{url}" target="_blank">こちら</a>
            """,
            unsafe_allow_html=True
        )

def main():
    hide_streamlit_style = """
                <style>
                div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 0%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
    if not "state" in st.session_state:
        st.session_state.state = 1
    if st.session_state.state == 1:
        input_id()
    elif st.session_state.state == 2:
        chat_page()
    elif st.session_state.state == 3:
        click_to_submit()

if __name__ == "__main__":
    st.title('チャットボット')
    main()
