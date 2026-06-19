import joblib
import io
import pandas as pd
from fastapi import FastAPI,HTTPException,UploadFile,File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel,Field
app=FastAPI()

# loading model
model=joblib.load("house_model.joblib")
# features=joblib.load("house_features.joblib")

# input schema
class HouseFeature(BaseModel):
    MedInc:float=Field(gt=0,description='Median income of neighbourhood')
    HouseAge:float=Field(gt=0,description='Average age of the house')
    AveRooms:float=Field(gt=0,description='Average number of the rooms in neighbour')
    AveBedrms:float=Field(gt=0,description='Average number of the Bedrooms in neighbour')
    Population:float=Field(gt=0,description='Total Population')
    AveOccup:float=Field(gt=0,description='Average number ocuupancies in neighbour')
    Latitude:float=Field(ge=32,le=42,description='Latitude')
    Longitude:float=Field(ge=-125,le=-114,description='Longitude')
@app.get('/')
def home():
    return {'message':'California house prediction API','status':'running','endpoint':'send POST request to /predict'}
@app.get('/health')
def health():
    return{
        'status':'running',
        'model':'RandomForestRegressor',
        'avg_error':"$39,000"
    }
@app.post('/predict')
def predict(house:HouseFeature):
    try:
        input_data=pd.DataFrame([
            {
                'MedInc': house.MedInc,
                'HouseAge': house.HouseAge,
                'AveRooms': house.AveRooms,
                'AveBedrms': house.AveBedrms,
                'Population': house.Population,
                'AveOccup': house.AveOccup,
                'Latitude': house.Latitude,
                'Longitude': house.Longitude
            }
        ])
        predicted=model.predict(input_data)[0]
        price_usd=predicted*100000
        return {'predicted_price':f"${price_usd:,.0f}",
                'predicted_price_short':f"${predicted:.2f} hundred thousands",
                "fidence_range":f"${price_usd-39000:,.0f} to ${price_usd+39000:,.0f}"
                }
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"prediction faied : {str(e)}")
@app.post('/predict-file')
async def predict_file(file:UploadFile=File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400,detail="please upload csv file only")
    contents=await file.read()
    df=pd.read_csv(io.BytesIO(contents))
    required_col=['MedInc','HouseAge','AveRooms','AveBedrms','Population','AveOccup','Latitude','Longitude']
    missing_col=[col for col in required_col
                 if col not in df.columns]
    if missing_col:
        raise HTTPException(status_code=400,detail=f"This col are missing from your file {missing_col} ")
    if df.empty:
        raise HTTPException(
            status_code=400,
            detail='The uploaded file has no data'
        )
    try:
        predictions=model.predict(df[required_col])
        df['predicted_col_usd']=predictions
        df['predicted_col_usd']=df['predicted_col_usd'].apply(lambda x: f"${x:,.0f}")
        output=df.to_csv(index=False)
        return StreamingResponse(
            io.StringIO(output),
            media_type="text/csv",
            headers={"Content-Disposition":"attachment; filename=predictions.csv"}

        )
    except Exception as e:
        raise HTTPException(
           status_code =500,
           detail=f"Prediction failed:{str(e)}"
        )