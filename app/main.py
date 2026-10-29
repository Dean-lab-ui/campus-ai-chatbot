from io import BytesIO
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from app.ai_provider import OpenAIProvider
from app.pdf_documents import MAX_PDF_BYTES, MAX_PDF_PAGES, store_pdf


STATIC_DIRECTORY = Path(__file__).resolve().parent / "static"


app = FastAPI(title="Campus AI Chatbot")

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIRECTORY),
    name="static",
)


ai_provider = OpenAIProvider()


class ChatRequest(BaseModel):
    user_id: str
    message: str


class ChatResponse(BaseModel):
    response: str


class PdfUploadResponse(BaseModel):
    filename: str
    pages: int
    message: str


@app.get("/")
def show_chat_interface():
    return FileResponse(STATIC_DIRECTORY / "index.html")


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/documents/pdf", response_model=PdfUploadResponse)
async def upload_pdf(
    user_id: str = Form(...),
    pdf_file: UploadFile = File(...),
):
    filename = pdf_file.filename or ""

    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF file.",
        )

    content = await pdf_file.read(MAX_PDF_BYTES + 1)

    if len(content) > MAX_PDF_BYTES:
        raise HTTPException(
            status_code=413,
            detail="PDF files must be 10 MB or smaller.",
        )

    try:
        reader = PdfReader(BytesIO(content))

        if reader.is_encrypted and not reader.decrypt(""):
            raise HTTPException(
                status_code=400,
                detail="Password-protected PDFs are not supported.",
            )

        if len(reader.pages) > MAX_PDF_PAGES:
            raise HTTPException(
                status_code=400,
                detail=f"PDF files must have {MAX_PDF_PAGES} pages or fewer.",
            )

        pages = [
            page.extract_text() or ""
            for page in reader.pages
        ]
    except PdfReadError as error:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file could not be read as a PDF.",
        ) from error

    try:
        document = store_pdf(
            user_id=user_id,
            filename=filename,
            pages=pages,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=(
                "No selectable text was found in the PDF. "
                "Scanned PDFs need OCR before they can be searched."
            ),
        ) from error

    return PdfUploadResponse(
        filename=document["filename"],
        pages=document["pages"],
        message="PDF uploaded and ready to search.",
    )


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        reply = ai_provider.generate_reply(
            message=request.message,
            user_id=request.user_id,
        )

        return ChatResponse(response=reply)

    except Exception as error:
        print(f"AI request failed: {error}")

        raise HTTPException(
            status_code=502,
            detail="The AI provider request failed.",
        ) from error