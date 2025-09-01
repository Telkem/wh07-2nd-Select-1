import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
# models.py에서 DataManager 클래스를 임포트 (기존 코드 유지)
from models import DataManager
from pydantic import BaseModel
import bcrypt

# json 필터를 사용하기 위한 라이브러리 임포트
from jinja2.ext import Extension
from markupsafe import Markup
import json
from datetime import datetime
from fastapi import Query

app = FastAPI()
templates = Jinja2Templates(directory="C:\\githome\\project_2nd\\html\\project_2nd")
data_manager = DataManager()

# Pydantic 모델을 사용하여 유효성 검사
class User(BaseModel):
    username: str
    password: str
    nickname: str
    birth: str
    gender: str

class LoginUser(BaseModel):
    username: str
    password: str

# 정적 파일(이미지) 제공을 위한 설정
# 'C:\githome\project_2nd\html\project_2nd\img' 디렉토리를 '/img' URL로 접근 가능하게 함
app.mount("/img", StaticFiles(directory="C:\\githome\\project_2nd\\html\\project_2nd\\img"), name="img")
app.mount("/room_img", StaticFiles(directory="C:\\githome\\project_2nd\\scraped_data\\img"), name="room_img")

@app.get("/")
def get_select_purpose_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
@app.get("/index.html")
def get_select_purpose_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 각 HTML 페이지로 이동하기 위한 라우팅 추가
@app.get("/select_purpose.html")
def get_select_purpose_page(request: Request):
    return templates.TemplateResponse("select_purpose.html", {"request": request})

@app.get("/radius_search.html")
def get_radius_search_page(request: Request):
    return templates.TemplateResponse("radius_search.html", {"request": request})

@app.get("/like_dong.html")
def get_like_dong_page(request: Request):
    return templates.TemplateResponse("like_dong.html", {"request": request})

@app.get("/login.html")
def get_login_page(request: Request):
    items, imgs, users = data_manager.get_all_items()
    return templates.TemplateResponse("login.html", {"request": request, "users": users})

@app.get("/signup.html")
def get_signup_page(request: Request):
    items, imgs, users = data_manager.get_all_items()
    return templates.TemplateResponse("signup.html", {"request": request, "users": users})

@app.get("/filter1.html")
def get_signup_page(request: Request):
    return templates.TemplateResponse("filter1.html", {"request": request})

@app.get("/filter2.html")
def get_signup_page(request: Request):
    return templates.TemplateResponse("filter2.html", {"request": request})

@app.get("/agent_detail.html")
def get_signup_page(request: Request):
    return templates.TemplateResponse("agent_detail.html", {"request": request})

@app.get("/search_result.html")
def get_index(request: Request):
    """
    사용자 요청을 받아 데이터를 가져와 화면에 표시하는 컨트롤러
    """
    # 1. 모델에서 데이터를 가져옵니다. (해당 프로젝트에 필요한 경우)
    items, imgs, users = data_manager.get_all_items()
    
    # 2. 뷰에 데이터를 전달해 화면을 렌더링합니다.
    return templates.TemplateResponse("search_result.html", {"request": request, "items": items})

@app.get("/property_detail.html")
def get_index(request: Request, item_index: int = Query(None)):
    """
    사용자 요청을 받아 데이터를 가져와 화면에 표시하는 컨트롤러
    """
    # 1. 모델에서 데이터를 가져옵니다. (해당 프로젝트에 필요한 경우)
    items, all_imgs, users  = data_manager.get_all_items()
    # URL 쿼리 파라미터에서 넘어온 item_id에 해당하는 items를 찾습니다.
    selected_item = next((item for item in items if item['id'] == item_index + 1), None)
    
    # 해당 매물에 속하는 이미지들만 필터링합니다.
    filtered_imgs = [img for img in all_imgs if img['property_id'] == item_index + 1]
    
    # 뷰에 데이터를 전달하여 화면을 렌더링합니다.
    return templates.TemplateResponse(
        "property_detail.html",
        {
            "request": request,
            "items": items, # 전체 아이템 리스트는 사이드바에 필요하므로 유지
            "selected_item": selected_item, # 상세 정보 표시를 위한 단일 아이템
            "imgs": filtered_imgs # 필터링된 이미지 리스트
        }
    )

@app.post("/signup")
async def signup(user: User):
    """
    회원가입 요청을 처리하는 엔드포인트
    """
    # 아이디 중복 확인
    if data_manager.get_user_by_username(user.username):
        return {"error": "이미 존재하는 아이디입니다."}
    
    # 비밀번호 해싱
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    
    # 데이터베이스에 사용자 정보 추가
    success = data_manager.add_user(
        username=user.username,
        password=hashed_password.decode('utf-8'),
        nickname=user.nickname,
        birth=user.birth,
        gender=user.gender
    )

    if success:
        return {"message": "회원가입 성공!"}
    else:
        return {"error": "회원가입 중 오류가 발생했습니다."}

@app.post("/login")
async def login(user: LoginUser):
    """
    로그인 요청을 처리하는 엔드포인트
    """
    db_user = data_manager.get_user_by_username(user.username)

    if not db_user:
        return {"error": "아이디가 존재하지 않습니다."}

    if not bcrypt.checkpw(user.password.encode('utf-8'), db_user['password'].encode('utf-8')):
        return {"error": "비밀번호가 일치하지 않습니다."}
    
    return {"message": "로그인 성공!"}


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# 커스텀 필터 함수 정의
def human_readable_money(value):
    """
    숫자를 '만원' 또는 '억' 단위로 변환하는 필터
    """
    value = int(value)
    if value >= 100000000:
        # 1억 이상일 경우
        return f"{value // 100000000}억 {value % 100000000 // 10000}만원" if value % 100000000 != 0 else f"{value // 100000000}억"
    elif value >= 10000:
        # 만원 이상일 경우
        return f"{value // 10000}만원"
    else:
        # 만원 미만일 경우
        return f"{value}원"

template_path = "C:\\githome\\project_2nd\\html\\project_2nd"

# tojson 필터 정의 (FastAPI의 tojson 필터를 직접 사용)
def tojson_filter(value):
    return Markup(json.dumps(value, cls=CustomJSONEncoder))

# Jinja2 환경을 직접 설정하고 tojson 필터 등록
env = Environment(loader=FileSystemLoader(template_path))
env.filters['money'] = human_readable_money
env.filters['tojson'] = tojson_filter

# FastAPI의 Jinja2Templates 객체에 커스텀 환경을 연결
templates = Jinja2Templates(directory=template_path)
templates.env = env



if __name__ == "__main__":
    # 서버를 0.0.0.0 주소에 바인딩하여 동일 네트워크의 다른 기기에서도 접속 가능하게 함
    uvicorn.run(app, host="0.0.0.0", port=8000)
