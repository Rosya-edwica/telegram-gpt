from typing import NamedTuple
import re

class LogLine(NamedTuple):
    Date: str
    Time: str
    TimeEx: int
    Cost: float
    Tokens: int

# LOG_FILES = (
#     "~/go-gpt-processing_copy/info.log",
#     "~/go/src/github.com/Rosya-edwica/go-gpt-processing/info.log",
# )

LOG_FILES = (
    "info_1.log",
    "info_2.log",
)

def read_logs(path:str) -> list[LogLine]:
    data = []
    with open(path, mode="r", encoding="utf-8") as f:
        lines = f.read().split("\n")
        for line in lines:
            if "INFO:" not in line:
                continue
            res = decode_logs(line)
            data.append(res)
    return data

def decode_logs(line: str) -> LogLine:
    date = re.findall(r"\d+\/\d+\/\d+", line)[0]
    datetime = re.findall(r"\d+:\d+:\d+", line)[0]
    time_exe = re.findall(r"\d+ сек", line)[0].replace(" сек", "")
    cost = re.findall(r"\d\.\d+\$", line)[0].replace("$", "")
    tokens = re.findall(r"Tokens: \d+", line)[0].replace("Tokens: ", "")

    return LogLine(
        Date=date,
        Time=datetime,
        Cost=float(cost),
        TimeEx=int(time_exe),
        Tokens=int(tokens)        
    )


def get_cost_for_date(date: str) -> float:
    """date format: 2023/11/21"""
    cost = 0
    for i in LOG_FILES:
        data = read_logs(i)
        cost += sum((i.Cost for i in data if i.Date == date or date == ''))
    return cost

def get_cost_for_all_time():
    stat = dict()

    for file in LOG_FILES:
        data = read_logs(file)
        for i in data:
            if i.Date in stat:
                stat[i.Date] += i.Cost
            else:
                stat[i.Date] = i.Cost
    
    return stat

