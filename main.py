from fastapi import FastAPI, Path,HTTPException,Query
import json
import pandas as pd

app = FastAPI()

def load_data():
    with open('patients.json','r') as f:
        data= json.load(f)
    return data

@app.get("/")
def hello():
    return {"message": "This is patient record management system API"}

@app.get("/about")
def hello_2():
    return {"message": "Fully function API to manage your patient records"}

@app.get("/view")
def view():
    return load_data()

@app.get("/view/{patient_id}")
def view_with_patient_id(patient_id: str= Path(...,description="ID of the patient",example="1")):
    df = load_data()

    if patient_id in df["patients"]:
        return df["patients"][patient_id]
    raise HTTPException(status_code=404, detail="Patient not found")

from fastapi import Query

@app.get("/sort")
def sort_patient(
    sort_by: str = Query(..., description="Sort on the basis of age"),
    order_by: str = Query("asc", description="Order of sorting: asc or desc")
):
    sort_by_list = ['age']
    order_by_list = ['asc', 'desc']

    if sort_by not in sort_by_list:
        raise HTTPException(status_code=404, detail="Sort by value is not correct")

    if order_by not in order_by_list:
        raise HTTPException(status_code=404, detail="Order by value is not correct")

    order_by_value = True if order_by == 'asc' else False

    df = load_data()

    df = pd.DataFrame.from_dict(df["patients"], orient="index")
    df.index.name = "patient_id"
    df.reset_index(inplace=True)

    df = df.sort_values(by=sort_by, ascending=order_by_value)

    return df.to_dict(orient="records")