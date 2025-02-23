from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
import pdfplumber
import aiofiles
import docx
import pandas as pd
from io import StringIO
from langchain_openai import ChatOpenAI
from langchain_experimental.agents import create_pandas_dataframe_agent
from app.core.config import settings

async def extract_text_from_file(index: int, file: UploadFile):
    if file.filename.endswith(".txt"):
        content = await file.read()
        content = content.decode("utf-8")

    elif file.filename.endswith(".pdf"):
        content = ""
        async with aiofiles.tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            await temp_pdf.write(await file.read())
            temp_pdf_path = temp_pdf.name

        with pdfplumber.open(temp_pdf_path) as pdf:
            for page in pdf.pages:
                content += page.extract_text() + "\n"
                
    elif file.filename.endswith(".docx"):
        async with aiofiles.tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_docx:
            await temp_docx.write(await file.read())
            temp_docx_path = temp_docx.name

        doc = docx.Document(temp_docx_path)
        content = "\n".join([para.text for para in doc.paragraphs])
    
    elif file.filename.endswith(".csv"):
        csv_data = await file.read()
        csv_text = csv_data.decode("utf-8")
        df = pd.read_csv(StringIO(csv_text))

        llm = ChatOpenAI(
            model_name=settings.openai_model, 
            temperature=0,
            openai_api_key=settings.openai_api_key
        )
        agent = create_pandas_dataframe_agent(llm, df, verbose=True, allow_dangerous_code=True)
        content = agent.run("このファイルにはどのようなデータが含まれているのか教えてください。また、データの行数と列数、各列の平均値・最大値を教えてください")
    
    elif file.filename.endswith(".py"):
        code_data = await file.read()
        code_text = code_data.decode("utf-8")
        content = f"Python code:\n{code_text}"      

    else:
        raise HTTPException(status_code=400, detail="現在、この種類のファイルの処理には対応しておりません")
    content = f"これは第{index}番目のファイルの内容: \n" + content
    return content
    
    