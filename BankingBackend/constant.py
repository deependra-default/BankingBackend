SAVING = "SV"
SALARY = "SL"
CURRENT = "CT"
BUSINESS = "BS"
OTHER = "OT"

ACTIVE = "AC"
INACTIVE = "IA"
HOLD = "HL"
BLOCKED = "BL"
SUSPENDED = "SP"

UPI = "UPI"
NEFT = "NEFT"
IMPS = "IMPS"
RTGS = "RTGS"
ATM = "ATM"
POS = "POS"
WITHDRAW = "WITHDRAW"
CASH = "CASH"

DEBIT = "Debit"
CREDIT = "Credit"


BANK_MANAGER = 'BM'
EMPLOYEE = 'EM'
CUSTOMER = 'CU'

USER_CHOICES =  (
    (BANK_MANAGER, 'Bank Manager'),
    (EMPLOYEE, 'Employee'),
    (CUSTOMER, 'Customer'),
    )

ACCOUNT_CHOICES = (
    (SAVING, "Savings"),
    (SALARY, "Salary"),
    (CURRENT, "Current"),
    (BUSINESS, "Business"),
    (OTHER, "Other"),
)

ACCOUNT_STATUS_CHOICES = (
    (ACTIVE, "Active"),
    (INACTIVE, "Inactive"),
    (HOLD, "Hold"),
    (BLOCKED, "Blocked"),
    (SUSPENDED, "Suspended"),
    (OTHER, "Other"),
)

TRANSACTION_METHOD = (
    (UPI, "UPI"),
    (NEFT, "NEFT"),
    (IMPS, "IMPS"),
    (RTGS, "RTGS"),
    (ATM, "ATM"),
    (POS, "POS"),
    (WITHDRAW, "WITHDRAW"),
    (OTHER, "OTHER"),
    (CASH, "CASH"),
)

TRANSACTION_TYPE = (
    (DEBIT, "Debit"),
    (CREDIT, "Credit"),
)
