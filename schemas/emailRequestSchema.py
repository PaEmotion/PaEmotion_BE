from pydantic import BaseModel, EmailStr

class EmailRequestSchema(BaseModel):
    email: EmailStr
