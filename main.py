# -------------------------------------------------------------
# Patient Record Management System API
#
# This FastAPI application provides endpoints to manage and
# retrieve patient records stored in a JSON file.
#
# Features:
# - View all patient records
# - View a specific patient using patient_id
# - Sort patient records based on age
#
# Technologies Used:
# - FastAPI for building REST API
# - JSON for data storage
# - Pandas for sorting and data processing
#
# -------------------------------------------------------------

# Import required FastAPI modules
from fastapi import FastAPI, Path,HTTPException,Query

# Used to send custom JSON responses with status codes
from fastapi.responses import JSONResponse

# Used for reading and writing JSON files
import json

# Pandas is used here to sort patient data easily
import pandas as pd

# Pydantic is used for request validation and schema definition
from pydantic import BaseModel, Field, computed_field

# Used for typing and restricting values
from typing import Annotated, Literal


# -------------------------------------------------------------
# Patient Schema (Data Validation Model)
# -------------------------------------------------------------
# This class defines the structure of a patient record.
# FastAPI automatically validates incoming request data
# based on this schema.

class Patient(BaseModel):

    # Unique patient ID
    id: Annotated[str, Field(..., description="ID of the patient", example=["1","2"])]

    # Patient name
    name: Annotated[str, Field(..., description="Name of the patient", example=["Abhay","Shamye"])]

    # Age validation (must be between 0 and 120)
    age: Annotated[int, Field(...,description="Age of the patient",gt=0,lt=120)]

    # Restrict gender to only these values
    gender: Annotated[Literal['Male','Female','Others'], Field(..., description="Gender of the patient")]

    # City where the patient lives
    city: Annotated[str, Field(..., description="Where patient lives")]

    # Patient height in centimeters
    height_cm: Annotated[float, Field(..., description="Hieght of the weight in cm",gt=0)]

    # Patient weight in kilograms
    weight_kg: Annotated[float, Field(..., description="Hieght of the weight in kg",gt=0)]  

    # Disease or medical condition
    disease: Annotated[str, Field(..., description="Patient is allgeric to")]

    # Admission date
    admission_date: Annotated[str, Field(..., description="When patient admit")]


    # -------------------------------------------------------------
    # Computed Field: BMI
    # -------------------------------------------------------------
    # BMI is calculated automatically when patient data is returned.
    # Formula:
    # BMI = weight (kg) / (height in meters)^2
    @computed_field
    @property
    def bmi(self)-> float:
        bmi = round(self.weight_kg / ((self.height_cm / 100) ** 2), 2)
        return bmi


# -------------------------------------------------------------
# Initialize FastAPI Application
# -------------------------------------------------------------
app = FastAPI()


# -------------------------------------------------------------
# Function: Load Data From JSON File
# -------------------------------------------------------------
# This function reads the patient data stored in patients.json
# and returns it as a Python dictionary.
def load_data():
    with open('patients.json','r') as f:
        data= json.load(f)
    return data


# -------------------------------------------------------------
# Function: Save Data Into JSON File
# -------------------------------------------------------------
# This function writes updated patient data back into the file.
def save_data(data):
    with open('patients.json','w') as f:
        json.dump(data,f)


# -------------------------------------------------------------
# Root Endpoint
# -------------------------------------------------------------
# Simple welcome endpoint to confirm API is running.
@app.get("/")
def hello():
    return {"message": "This is patient record management system API"}


# -------------------------------------------------------------
# About Endpoint
# -------------------------------------------------------------
# Provides a short description of the API.
@app.get("/about")
def hello_2():
    return {"message": "Fully function API to manage your patient records"}


# -------------------------------------------------------------
# View All Patients
# -------------------------------------------------------------
# Returns the entire dataset stored in the JSON file.
@app.get("/view")
def view():
    return load_data()


# -------------------------------------------------------------
# View Specific Patient By ID
# -------------------------------------------------------------
# Retrieves patient information using patient_id.
@app.get("/view/{patient_id}")
def view_with_patient_id(patient_id: str= Path(...,description="ID of the patient",example="1")):

    # Load patient dataset
    df = load_data()

    # Check if patient ID exists
    if patient_id in df["patients"]:
        return df["patients"][patient_id]

    # If patient does not exist, return 404 error
    raise HTTPException(status_code=404, detail="Patient not found")


# -------------------------------------------------------------
# Sort Patients
# -------------------------------------------------------------
# Allows sorting patient records based on age
# Example:
# /sort?sort_by=age&order_by=asc
from fastapi import Query

@app.get("/sort")
def sort_patient(
    sort_by: str = Query(..., description="Sort on the basis of age"),
    order_by: str = Query("asc", description="Order of sorting: asc or desc")
):

    # Allowed sorting fields
    sort_by_list = ['age']

    # Allowed ordering values
    order_by_list = ['asc', 'desc']

    # Validate sort field
    if sort_by not in sort_by_list:
        raise HTTPException(status_code=404, detail="Sort by value is not correct")

    # Validate order type
    if order_by not in order_by_list:
        raise HTTPException(status_code=404, detail="Order by value is not correct")

    # Convert order to boolean for pandas
    order_by_value = True if order_by == 'asc' else False

    # Load dataset
    df = load_data()

    # Convert dictionary to pandas DataFrame
    df = pd.DataFrame.from_dict(df["patients"], orient="index")

    # Set index name
    df.index.name = "patient_id"

    # Convert index into a column
    df.reset_index(inplace=True)

    # Sort DataFrame
    df = df.sort_values(by=sort_by, ascending=order_by_value)

    # Convert back to dictionary format
    return df.to_dict(orient="records")


# -------------------------------------------------------------
# Create New Patient
# -------------------------------------------------------------
# Adds a new patient record to the JSON database.
@app.post('/create')
def create_patient(patient: Patient):

    # Load existing data
    data= load_data()

    # Check if patient already exists
    if patient.id in data["patients"]:
        raise HTTPException(status_code=403, detail=" Patient already present in the database")

    # Add new patient record
    data["patients"][patient.id] = patient.model_dump(exclude=["id"])

    # Save updated data back to JSON file
    save_data(data)

    # Return success response
    return JSONResponse(status_code=201, content={'message':'Patient created successfully into the databse'})