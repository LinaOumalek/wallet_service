from sqlalchemy import create_engine, Column, Integer, String, CheckConstraint, DateTime, func, Numeric, Enum, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

engine = create_engine("postgresql+psycopg2://postgres:Linareda123@localhost:5432/database")
Base = declarative_base()

SessionLocal = sessionmaker(bind = engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key = True)
    full_name = Column(String(100), nullable = False)
    email = Column(String(255), nullable = False, unique = True)
    phone_number = Column(String(15), unique = True)
    created_at = Column(DateTime(timezone = True), server_default=func.now())
    
    __table_args__ = (
        CheckConstraint("email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'", 
                        name = "check_users_email_format"),
        CheckConstraint("phone_number IS NULL OR phone_number ~ '^[0-9]{10,15}$'",
                        name = "check_users_phone_number_format"),
                        )

    wallets = relationship("Wallet", back_populates = "user")


class Wallet(Base):
    __tablename__ = "wallets"

    wallet_id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable = False)
    balance = Column(Numeric(15,2), server_default = "0.00")
    currency = Column(String(3), nullable = False)
    created_at = Column(DateTime(timezone = True), server_default= func.now())

    __table_args__ = (CheckConstraint("balance >= 0", name = "check_wallets_balance_positive"),
                      CheckConstraint("currency IN ('USD', 'EUR', 'MAD', 'GBP')", name = "check_wallets_currency_valid"),

    )

    user = relationship("User", back_populates = "wallets")
    sender_transactions = relationship("Transaction", back_populates = "sender_wallet")
    receiver_transactions = relationship("Transaction", back_populates = "receiver_wallet")


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key = True)
    sender_id = Column(Integer, ForeignKey("wallets.wallet_id"), nullable = False)
    receiver_id = Column(Integer, ForeignKey("wallets.wallet_id"), nullable = False)
    transaction_type = Column(Enum("deposit", "withdrawal", "transfer", name = "transaction_type_enum"), nullable = False)
    amount = Column(Numeric(15,2), nullable = False)
    status = Column(Enum("pending", "approved", "failed", name = "status_enum"), nullable = False, server_default = "pending")
    timestamp = Column(DateTime(timezone = True), server_default = func.now())

    __table_args__ = (CheckConstraint("amount > 0", name = "check_transactions_amount_valid"),


    )

    sender_wallet = relationship("Wallet", foreign_keys=[sender_id], back_populates = "sender_transactions" )
    receiver_wallet = relationship("Wallet", foreign_keys=[receiver_id], back_populates = "receiver_transactions")

Base.metadata.create_all(engine)