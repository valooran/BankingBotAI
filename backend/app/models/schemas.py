from pydantic import BaseModel
from typing import Optional

class AccountCreate(BaseModel):
    account_type: str
    initial_deposit: float
    
class AccountResponse(BaseModel):
    account_number: int
    account_type: str
    balance: float

class FundTransfer(BaseModel):
    from_account: str
    to_account: str
    amount: float
