# FastAPI 예제

## 실행

Uvicorn
```shell
APP_ENV=local uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload --proxy-headers
```

Gunicorn
```shell
APP_ENV=local gunicorn src.app.main:app -k uvicorn.workers.UvicornWorker -w 1 --threads 2 -b 0.0.0.0:8000
```
