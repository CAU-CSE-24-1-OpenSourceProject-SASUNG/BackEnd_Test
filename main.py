from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import openai
import os
from database import Database
from dotenv import load_dotenv
#from database import *

# 여기에openai 키 작성(띄어쓰기 사이에 . 추가)
openai.api_key = os.environ.get('OPENAI_API_KEY')

app = FastAPI()

################################### DB instructions ##############################

# 데이터베이스 연결 정보
load_dotenv(dotenv_path="db.env")
host_name = os.getenv("DB_HOST")
user_name = os.getenv("DB_USER")
user_password = os.getenv("DB_PASS")
db_name = os.getenv("DB_NAME")

# Database 인스턴스 생성
db = Database(host_name, user_name, user_password, db_name)

# 데이터베이스에 연결
db.connect()

@app.get("/DB/")
def read_root():
    query = "select * from user_inf"
    users = db.execute_read_query(query)
    return {"users": users}

####################################################################################




#################################### Chat ##########################################

templates = Jinja2Templates(directory="templates")
conversation_history = []

# 대화 시작
@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "converstation":conversation_history})

# 사용자 입력 처리 -> ChatGPT 응답 생성
@app.post("/submit/")
async def submit_form(request: Request, user_input: str = Form(...)):
    # 사용자 입력을 대화 기록에 추가
    conversation_history.append({"speaker": "You", "message": user_input})
    
    # ChatGPT에 대화 기록을 포함하여 챗봇 응답 생성
    chat_response = generate_chat_response(conversation_history, user_input)
    
    # 챗봇 응답을 대화 기록에 추가
    conversation_history.append({"speaker": "ChatGPT", "message": chat_response})
    
    return templates.TemplateResponse("index.html", {"request": request, "conversation": conversation_history})

# 챗봇 응답을 생성하는 함수
def generate_chat_response(conversation_history, user_input):
    
    # 대화 기록을 ChatGPT의 입력으로 변환
    chat_prompt = "\n".join([f"{turn['speaker']}: {turn['message']}" for turn in conversation_history])
    
    # ChatGPT API를 사용하여 챗봇 응답 생성
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # GPT-3.5 엔진 사용
            messages=[
                {"role": "system", "content": chat_prompt},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print("Error: ", e)
        return "챗봇 응답 생성 중 오류가 발생했습니다."

##############################################################################################