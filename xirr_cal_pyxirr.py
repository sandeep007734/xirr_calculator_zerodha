import pandas as pd
from pyxirr import xirr
import datetime
import sys

if len(sys.argv)<2:
    print("Please enter the file name as an argument")
    sys.exit()

def listOfTuples(list1, list2):
    #make a list of tuples having an element from each list
    return list(map(lambda x, y:(x,y), list1, list2))

def readLedger(filename):
    #read ledger file from Zerodha in a specified format
    headers = ['particulars', 'posting_date', 'cost_center', 'voucher_type', 'debit', 'credit', 'net_balance']
    dataType = {'particulars': 'str', 'posting_date': 'str', 'cost_center': 'str', 'voucher_type': 'str', 'debit': 'float', 'credit': 'float', 'net_balance': 'float'}
    dateColumns = ['posting_date']
    return pd.read_csv(filename, sep=',', header = 0, names = headers, dtype = dataType, parse_dates = dateColumns, dayfirst=True).dropna()

# combine two list column wise and return a dataframe with the combined list
def combineList(list1, list2):
    return pd.DataFrame(listOfTuples(list1, list2))

# given a list of dates, remove the timestamp from the date and return modified list
def removeTimestamp(dateList):
    return [date.date() for date in dateList]

#take inputs from user
endDate = datetime.datetime.now()
print(f"Using current date as end date: {endDate}")
# endDate = pd.to_datetime(input("Enter Date for end of investment period in dd-mm-yyyy format: "), format= '%d-%m-%Y')
fundBalance = float(input("Enter the final portfolio value including fund balance: "))
# ledgerData = readLedger(input("Enter funds ledger name: "))
print(f"Using ledger file: {sys.argv[1]}")
ledgerData = readLedger(sys.argv[1])

# print(list(ledgerData))
with pd.option_context('display.max_rows', None,
                       'display.max_columns', None,
                       'display.precision', 3,
                       ):
    # print(ledgerData["vou"][["posting_date","voucher_type","debit","credit"]])
    mod_ledgerData = ledgerData[(ledgerData["voucher_type"] == "Bank Receipts") | (ledgerData["voucher_type"] == "Bank Payments")][["posting_date","voucher_type","debit","credit"]].sort_values(by="posting_date", ascending=False)
    print(mod_ledgerData)

dateLedger = list(ledgerData["posting_date"])
voucherData = ledgerData['voucher_type'].tolist()
debitData = ledgerData['debit'].tolist()
creditData = ledgerData['credit'].tolist()

combinedFlow = list()

for entryIndex, voucher in enumerate(voucherData):
    if voucher == 'Bank Receipts':
        #all deposits to Zerodha funds are treated as negative flow
        combinedFlow.append(-1*creditData[entryIndex])
    elif voucher == 'Bank Payments':
        #all withdrawals to account are treated as positive flow
        combinedFlow.append(debitData[entryIndex])
    else:
        combinedFlow.append(0)

dateLedger.append(endDate)
combinedFlow.append(fundBalance)

# combineList(removeTimestamp(dateLedger), combinedFlow).to_csv("data/xirr_data.csv", index=False, header=False)
mod_ledgerData.to_csv("data/xirr_data.csv", index=False, header=False)

calculatedXIRR = xirr(dateLedger, combinedFlow)*100
print(f"Calculated XIRR: {round(calculatedXIRR,2)}%")
# print(calculatedXIRR*100)

