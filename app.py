import sys
import os

import pandas as pd
import numpy as np

import pymongo

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.utils.main_utils.utils import load_object
from networksecurity.pipeline.training_pipeline import TrainingPipeline

from networksecurity.constant.training_pipeline import DATA_INGESTION_DATABASE_NAME, DATA_INGESTION_COLLECTION_NAME

from fastapi import FastAPI, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run as app_run
from fastapi.responses import Response
from starlette.responses import RedirectResponse

import certifi
ca = certifi.where()

from dotenv import load_dotenv
load_dotenv()
MONGO_DB_URL = os.getenv("MONGO_DB_URL")
print(MONGO_DB_URL)

client = pymongo.MongoClient(MONGO_DB_URL, tlsCAFile=ca)
database = client[DATA_INGESTION_DATABASE_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=['authentication'])
async def index():
    return RedirectResponse(url="/docs")

@app.get("/train")
async def train_route():
    try:
        training_pipeline = TrainingPipeline()
        training_pipeline.run_pipeline()
        return Response(content="Training is successful!!")
    except Exception as e:
        raise NetworkSecurityException(e, sys)
    
@app.get("/predict")
async def predict_route(request: Request, file: UploadFile = File(...)):
    try:
        df = pd.read_csv(file.file)
        preprocesor = load_object("final_model/preprocessor/preprocessor.pkl")
        final_model = load_object("final_model/model/model.pkl")
        network_model = NetworkModel(preprocessor=preprocesor, model=final_model)
        y_pred = network_model.predict(df)
        df['Prediction_column'] = y_pred
        df.to_csv("prediction_output/output.csv", index=False)
        table_html = df.to_html()
        return TemplateResponse("table.html", {"request": request, "table_html": table_html})
    except Exception as e:
        raise NetworkSecurityException(e, sys)
    
if __name__ == "__main__":
    app_run(app, host="localhost", port=8000)