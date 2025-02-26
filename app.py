import streamlit as st
import requests
import json
from urllib.parse import urlencode
import os
from dotenv import load_dotenv
import jwt
load_dotenv()
# LINE Login 配置
LINE_LOGIN_CLIENT_ID = os.getenv('LINE_LOGIN_CLIENT_ID')  # 從 LINE Developer Console 取得
LINE_LOGIN_CLIENT_SECRET = os.getenv('LINE_LOGIN_CLIENT_SECRET') # 從 LINE Developer Console 取得
REDIRECT_URI = os.getenv('REDIRECT_URI')  # Streamlit 預設端口
LINE_AUTH_URL = "https://access.line.me/oauth2/v2.1/authorize"
LINE_TOKEN_URL = "https://api.line.me/oauth2/v2.1/token"
LINE_PROFILE_URL = "https://api.line.me/v2/profile"
def get_login_url():
    params = {
        "response_type": "code",
        "client_id": LINE_LOGIN_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "profile openid email",  # 確保包含 email
        "state": "random_state_string"
    }
    return f"{LINE_AUTH_URL}?{urlencode(params)}"

def get_access_token(code):
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": LINE_LOGIN_CLIENT_ID,
        "client_secret": LINE_LOGIN_CLIENT_SECRET
    }
    response = requests.post(LINE_TOKEN_URL, data=data)
    return response.json()

def get_user_profile(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(LINE_PROFILE_URL, headers=headers)
    return response.json()

def get_email_from_id_token(id_token):
    # 解碼 ID Token（不驗證簽名，僅用於展示；生產環境應驗證）
    decoded_token = jwt.decode(id_token, options={"verify_signature": False})
    return decoded_token.get("email")

def main():
    st.title("LINE Login Demo")

    query_params = st.query_params #因為streamlit是單頁網站 用這個模擬參數傳遞
    code = query_params.get("code", None)

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_info = None
        st.session_state.email = None

    if not st.session_state.logged_in:
        if not code:
            login_url = get_login_url()
            st.markdown(f"[使用 LINE 登入]({login_url})")
        else:
            token_response = get_access_token(code)
            if "access_token" in token_response and "id_token" in token_response:
                access_token = token_response["access_token"]
                id_token = token_response["id_token"]
                
                profile = get_user_profile(access_token)
                email = get_email_from_id_token(id_token)
                
                st.session_state.logged_in = True
                st.session_state.user_info = profile
                st.session_state.email = email
                
                st.success("登入成功！")
                st.write("使用者資訊：")
                st.json(profile)
                st.write("電子郵件：")
                st.write(email if email else "使用者未提供 email")
            else:
                st.error("登入失敗，請重試")
    else:
        st.write("歡迎回來！")
        st.write("你的資訊：")
        st.json(st.session_state.user_info)
        st.write("電子郵件：")
        st.write(st.session_state.email if st.session_state.email else "使用者未提供 email")
        
        if st.button("登出"):
            st.session_state.logged_in = False
            st.session_state.user_info = None
            st.session_state.email = None
            st.query_params.clear()
            st.rerun()

if __name__ == "__main__":
    main()
