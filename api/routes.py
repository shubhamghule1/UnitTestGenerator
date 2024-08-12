from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from starlette.templating import Jinja2Templates

from services.repo_service import generate_unit_tests
from utils.file_ops import delete_file_after_send, delete_dir_after_send

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/", status_code=201)
async def generate_unit_test_from_URL(request: Request, backgroundTasks: BackgroundTasks):
    try:
        data = await request.json()
        repo_url = data.get('repo_url')
        if not repo_url:
            raise HTTPException(status_code=400, detail="Repository URL is required")

        zip_file_path, repo_dir, test_dir = generate_unit_tests(repo_url)

        # Schedule the cleanup task to run in the background
        backgroundTasks.add_task(delete_dir_after_send, repo_dir)
        backgroundTasks.add_task(delete_dir_after_send, test_dir)
        backgroundTasks.add_task(delete_file_after_send, zip_file_path)

        return FileResponse(path=zip_file_path, media_type='application/zip', filename=f"{repo_dir}_tests.zip")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
