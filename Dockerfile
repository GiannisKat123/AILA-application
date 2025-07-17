# # ------ Build React App ------
# FROM node:20 AS frontend-builder

# WORKDIR /app

# COPY frontend/package.json frontend/package-lock.json ./

# RUN npm install 

# COPY frontend/ ./

# # COPY frontend/.env.production .env

# RUN npm run build 

# # ------ Build FastAPI App ------
# FROM python:3.11-slim

# WORKDIR /app

# # COPY .env .env

# COPY backend/requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY backend/ ./backend/
# COPY --from=frontend-builder /app/dist ./frontend/dist 

# RUN pip install uvicorn
# EXPOSE 8080
# CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]




# ------ Build React App ------
FROM node:20 AS frontend-builder

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./

RUN npm install

COPY frontend/ ./

COPY frontend/.env.production .env

RUN npm run build

# ------ Build FastAPI App ------
FROM python:3.11-slim

WORKDIR /app

COPY .env .env

COPY backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/

# ----------------------------------

COPY --from=frontend-builder /app/dist ./frontend/dist

EXPOSE 8080

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "backend.main:app", "-b", "0.0.0.0:8080"]