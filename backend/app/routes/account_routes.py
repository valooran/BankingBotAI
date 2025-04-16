from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.account import Account
from app.models.user import User
from app.models.schemas import AccountCreate, FundTransfer, AccountResponse
from jose import jwt, JWTError
from app.auth import SECRET_KEY, ALGORITHM
from app.models.transaction import Transaction
from datetime import datetime
import random

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
@router.post("/create", response_model=AccountResponse)
def create_account(account: AccountCreate, db: Session = Depends(get_db), token: str = Header(...)):
    user_id = get_user_id_from_token(token, db)
    
    new_account = Account(
        user_id=user_id,
        account_number = generate_unique_account_number(db),
        account_type=account.account_type.lower(),
        balance=account.initial_deposit
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account

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
    
    transaction = Transaction(
        from_account=transfer.from_account,
        to_account=transfer.to_account,
        amount=transfer.amount,
        timestamp=datetime.utcnow()
    )
    db.add(transaction)

    db.commit()
    return {"message": "Transfer successful", "from": from_acc.account_number, "to": to_acc.account_number}

@router.get("/transactions")
def get_transactions(
    token: str = Header(...),
    db: Session = Depends(get_db),
    from_date: datetime = Query(None),
    to_date: datetime = Query(None),
    account_number: str = Query(None),
    page: int = Query(1),
    limit: int = Query(10)
):
    user_id = get_user_id_from_token(token, db)
    user_accounts = db.query(Account.account_number).filter(Account.user_id == user_id).subquery()

    query = db.query(Transaction).filter(
        (Transaction.from_account.in_(user_accounts)) |
        (Transaction.to_account.in_(user_accounts))
    )

    if from_date:
        query = query.filter(Transaction.timestamp >= from_date)
    if to_date:
        query = query.filter(Transaction.timestamp <= to_date)
    if account_number:
        if account_number.strip():
            query = query.filter(
                (Transaction.from_account == account_number) |
                (Transaction.to_account == account_number)
            )

    total = query.count()
    transactions = query.order_by(Transaction.timestamp.desc()).offset((page - 1) * limit).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "transactions": transactions
    }

def generate_unique_account_number(db: Session) -> int:
    while True:
        account_number = random.randint(1000000000, 9999999999)
        existing = db.query(Account).filter_by(account_number=account_number).first()
        if not existing:
            return account_number
