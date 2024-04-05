from fastapi import FastAPI, Form, Request, HTTPException, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from database import Database
from dotenv import load_dotenv
import openai
import os
import uuid

# 여기에openai 키 작성(띄어쓰기 사이에 . 추가)
openai.api_key = os.environ.get('OPENAI_API_KEY')

app = FastAPI()

templates = Jinja2Templates(directory="templates")

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


######################################## Log in ##########################################

# 사용자 세션 관리
session = {}

# 로그인 화면
@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# 로그인 시도
@app.post("/")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    query=f"select * from id_db where ID='{username}'"
    result = db.execute_read_query(query)
    if result:
        if result[0][1] == password:
            session_id = str(uuid.uuid4())
            session[session_id] = {"username": username}
            response = RedirectResponse(url="/start/", status_code=302)
            response.set_cookie(key="session_id", value=session_id)
            return response
        else:
            error_message = "아이디와 비밀번호가 일치하지 않습니다. 다시 입력해주세요."
            return templates.TemplateResponse("login.html", {"request": request, "error_message": error_message})
    else:
        if len(password) >= 7 and len(password) <= 10 and len(username) >= 4 and len(username) <= 10:
            query=f"insert into id_db values('{username}', '{password}')"
            db.execute_query(query)
            session_id = str(uuid.uuid4())
            session[session_id] = {"username": username}
            response = RedirectResponse(url="/start/", status_code=302)
            response.set_cookie(key="session_id", value=session_id)
            return response
        else:
            error_message = "아이디 길이를 4~10글자, 비밀번호 길이를 7~10글자로 맞춰주세요."
            return templates.TemplateResponse("login.html", {"request": request, "error_message": error_message})
        
##########################################################################################

#################################### Chat ##################################################################3


conversation_history = []

# 대화 시작
@app.get("/start/", response_class=HTMLResponse)
async def read_item(request: Request, session_id: str = Cookie(None)):
    if session_id in session:
        return templates.TemplateResponse("index.html", {"request": request, "converstation":conversation_history})
    else:
        return RedirectResponse(url="/", status_code=302)

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

###############################################################################################################