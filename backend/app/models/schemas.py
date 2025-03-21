from pydantic import BaseModel
from typing import Optional

class AccountCreate(BaseModel):
    account_type: str

class FundTransfer(BaseModel):
    from_account: str
    to_account: str
    amount: float
