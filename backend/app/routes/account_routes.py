from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.account import Account
from app.models.user import User
from app.models.schemas import AccountCreate, FundTransfer
from jose import jwt, JWTError
from app.auth import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/api/account", tags=["Account"])

# Helper to get user from token
def get_user_id_from_token(token: str, db: Session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user.id
    except JWTError:
        raise HTTPException(status_code=401, detail="Token error")

# Create account
@router.post("/create")
def create_account(account_data: AccountCreate, token: str = Header(...), db: Session = Depends(get_db)):
    user_id = get_user_id_from_token(token, db)
    import random
    acc_number = str(random.randint(1000000000, 9999999999))

    new_acc = Account(
        user_id=user_id,
        account_number=acc_number,
        account_type=account_data.account_type,
        balance=0.0
    )
    db.add(new_acc)
    db.commit()
    db.refresh(new_acc)
    return new_acc

# Get account summary
@router.get("/summary")
def get_account_summary(token: str = Header(...), db: Session = Depends(get_db)):
    user_id = get_user_id_from_token(token, db)
    accounts = db.query(Account).filter(Account.user_id == user_id).all()
    return accounts

# Fund Transfer (self)
@router.post("/transfer")
def transfer_funds(transfer: FundTransfer, token: str = Header(...), db: Session = Depends(get_db)):
    user_id = get_user_id_from_token(token, db)

    from_acc = db.query(Account).filter(Account.account_number == transfer.from_account, Account.user_id == user_id).first()
    to_acc = db.query(Account).filter(Account.account_number == transfer.to_account, Account.user_id == user_id).first()

    if not from_acc or not to_acc:
        raise HTTPException(status_code=404, detail="Invalid accounts")
    if from_acc.balance < transfer.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    from_acc.balance -= transfer.amount
    to_acc.balance += transfer.amount

    db.commit()
    return {"message": "Transfer successful", "from": from_acc.account_number, "to": to_acc.account_number}
