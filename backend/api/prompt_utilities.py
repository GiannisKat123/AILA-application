import base64
from openai import OpenAI
from backend.database.config.config import settings
from pypdf import PdfReader
from fastapi import UploadFile
from langchain_core.messages import HumanMessage
from backend.api.models import FileRec
import uuid,os,shutil



def guess_ext(filename: str) -> str:
    _, ext = os.path.splitext(filename or "")
    return ext.lower()

def persist_upload(f: UploadFile) -> FileRec:
    ext = guess_ext(f.filename)
    new_name = f"{uuid.uuid4().hex}{ext}"
    dest = os.path.join('uploads', new_name)
    with open(dest, "wb") as out:
        shutil.copyfileobj(f.file, out)
    return FileRec(original=f.filename or new_name, path=dest, mime=(f.content_type or "").lower())


def to_data_url(path:str, mime:str) -> str:
    with open(path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('utf-8')
    return f'data{mime};base64,{b64}'

def transcribe_audio(path:str) -> str:
    oai = OpenAI(api_key = settings.API_KEY)
    with open(path,"rb") as f:
        tr = oai.audio.transcriptions.create(model='whisper-1',file=f)
    return getattr(tr,'text',str(tr))

def extract_text_from_pdf(path:str) -> str:
    reader = PdfReader(path)
    text = '\n'.join([p.extract_text() for p in reader.pages])
    return text

def safe_read_text(path:str) -> str:
    txt = open(path,'r',errors='ignore').read()
    return txt

def build_messages(prompt_text:str, files: list[UploadFile]):
    parts = [{'type':'text','text':prompt_text}]
    evidence_lines = []

    for f in files:
        mt = (f.mime or "").lower()
        if mt.startswith('image/'):
            img_url = f.url or to_data_url(f.path,mt)
            parts.append({'type':'image_url','image_url':img_url})
            evidence_lines.append(f"-Image: {f.original}")

        elif mt.startswith('audio/'):
            transcript = transcribe_audio(f.path)
            evidence_lines.append(f" Sound {f.original} \n Recording:\n {transcript}")

        elif mt == 'application/pdf':
            txt = extract_text_from_pdf(f.path)
            evidence_lines.append(f"- PDF: {f.original}\n Text:\n {txt}")

        elif mt in ("text/plain","text/csv") or f.original.lower().endswith(".csv"):
            snippet = safe_read_text(f.path)
            evidence_lines.append(f"- Text: {f.original}\n Text:\n {snippet}")

        else:
            evidence_lines.append(f"- No supported type. {f.original} will be ignored")

    if evidence_lines:
        parts[0]['text'] += "\n\n Evidence from Uploads\n" + "\n".join(evidence_lines)

    return [HumanMessage(content=parts)]
