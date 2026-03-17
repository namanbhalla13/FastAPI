from pydantic import BaseModel, EmailStr, AnyUrl, Field, field_validator, model_validator, computed_field
from typing import List, Dict, Optional, Annotated


# -------------------------------------------------------------
# Patient Data Model
# -------------------------------------------------------------
# This Pydantic model defines the schema and validation rules
# for patient data. Whenever data is passed to this model,
# Pydantic automatically validates and converts types if needed.

class Patient(BaseModel):

    # Patient name
    # Annotated is used to attach metadata like validation rules and descriptions.
    name: Annotated[
        str,
        Field(
            max_length=50,
            title="Name of the patient",
            description="Give the name of the patient in less than 50+ chars",
            examples=['Naman','Abc']
        )
    ]

    # Age must be between 1 and 119
    age: int = Field(gt=0, lt=120)

    # Gender of the patient
    gender: str

    # Disease or medical condition
    disease: str

    # Admission date (currently stored as string)
    addmission_date: str

    # Whether the patient is married
    married: Annotated[
        bool,
        Field(default=None, description="Is the patient is married or not")
    ]

    # Optional allergies list (max 5 allergies allowed)
    allergies: Annotated[
        Optional[list[str]],
        Field(default=None, max_length=5)
    ]

    # Dictionary storing contact numbers
    # Example: {"self": "12345", "emergency": "99999"}
    contact_details: Dict[str,str]

    # Patient weight
    # strict=True ensures that type coercion is NOT allowed
    # meaning strings like "70" will NOT automatically convert to float.
    weight: Annotated[float, Field(gt=0, strict=True)]

    # EmailStr automatically validates email format
    email: EmailStr

    # Optional LinkedIn URL
    # AnyUrl validates whether the provided string is a valid URL
    linkedIn_url: Optional[AnyUrl] = None

    # Height in meters (used for BMI calculation)
    height: float


    # -------------------------------------------------------------
    # Email Domain Validator
    # -------------------------------------------------------------
    # mode='after' means this validator runs AFTER Pydantic performs
    # basic validation and type conversion.
    #
    # Pydantic first ensures the value is a valid email using EmailStr,
    # then this validator checks whether the email domain is allowed.

    @field_validator('email', mode='after')
    @classmethod
    def emial_validator(cls, value):

        valid_domains = ['hdfc.com','icici.com','gmail.com']

        # Extract domain name after "@"
        domain_name = value.split("@")[-1]

        # Raise error if email domain is not allowed
        if domain_name not in valid_domains:
            raise ValueError("Not in valid email")

        return value


    # -------------------------------------------------------------
    # Name Transformation Validator
    # -------------------------------------------------------------
    # This validator converts the patient name to uppercase.
    # It runs automatically whenever the model is created.

    @field_validator('name')
    @classmethod
    def transform_name(cls, value):
        return value.upper()


    # -------------------------------------------------------------
    # Model-Level Validation
    # -------------------------------------------------------------
    # model_validator runs after all fields are validated.
    # It checks conditions involving multiple fields.

    @model_validator(mode="after")
    def validate_emergncy_conatct(cls, model):

        # If patient is older than 60,
        # ensure emergency contact exists.
        if model.age > 60 and 'emergency' not in model.contact_details:
            raise ValueError(
                "Patient older than 60 and must have at least one emergency contact"
            )

        return model


    # -------------------------------------------------------------
    # Computed Field: BMI
    # -------------------------------------------------------------
    # This field is automatically calculated and included
    # in the output model but is NOT required in input data.

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight / (self.height ** 2), 2)
        return bmi


# -------------------------------------------------------------
# Insert Patient Data Function
# -------------------------------------------------------------
# Simulates inserting patient data into a database.

def insert_patient_data(patient_data: Patient):

    print("data inserted successfully")
    print("Here is your data please check")

    # Access validated and transformed data
    print(patient_data.name)

    # Access computed BMI field
    print(patient_data.bmi)

    return 1


# -------------------------------------------------------------
# Update Patient Data Function
# -------------------------------------------------------------
# Simulates updating patient information.

def update_patient_data(patient_data: Patient):

    print("data update successfully")
    print("Here is your data please check")

    print(patient_data.name)

    return 1


# -------------------------------------------------------------
# Example Patient Data
# -------------------------------------------------------------
# Raw input data that will be validated by Pydantic.

patient_1_info = {
    'name':'naman',
    'age':111,
    'gender':'male',
    'disease':'over thinking',
    'addmission_date':'01-02-9999',
    'married':False,
    'allergies':['pollen','dust'],
    'contact_details':{
        'self':'111111',
        'other':'777777',
        'emergency':'ababbabba'
    },
    'weight':69.95,
    'email':'abba@gmail.com',
    'height':187
}


# -------------------------------------------------------------
# Model Creation
# -------------------------------------------------------------
# The ** operator unpacks the dictionary and sends
# the values into the Patient model.

test_patient_1 = Patient(**patient_1_info)


# -------------------------------------------------------------
# Insert Data
# -------------------------------------------------------------
# Passing validated patient object to the insert function.

insert_patient_data(test_patient_1)

