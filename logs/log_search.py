import re
import sys
from datetime import datetime

def search_logs(log_file, keyword=None, log_level=None, start_date=None, end_date=None):
    """
    Search logs based on keyword, log level, and date range.
    
    :param log_file: Path to the log file.
    :param keyword: Keyword to filter logs.
    :param log_level: Log level (INFO, WARNING, ERROR, etc.).
    :param start_date: Start date (YYYY-MM-DD HH:MM:SS).
    :param end_date: End date (YYYY-MM-DD HH:MM:SS).
    :return: List of matching log entries.
    """
    results = []
    
    with open(log_file, 'r', encoding='utf-8') as file:
        for line in file:
            match = re.match(r'^(\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2},\\d{3}) - (\\w+) - (.*)$', line)
            
            if match:
                log_time, level, message = match.groups()
                log_time = datetime.strptime(log_time, "%Y-%m-%d %H:%M:%S,%f")
                
                if log_level and log_level.upper() != "NONE" and level != log_level:
                    continue
                
                if keyword and keyword.upper() != "NONE" and keyword.lower() not in message.lower():
                    continue
                
                if start_date and start_date.upper() != "NONE":
                    start_date_dt = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
                    if log_time < start_date_dt:
                        continue
                
                if end_date and end_date.upper() != "NONE":
                    end_date_dt = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
                    if log_time > end_date_dt:
                        continue
                
                results.append(line.strip())
    
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python log_search.py <log_file> <keyword> <log_level> <start_date> <end_date>")
        sys.exit(1)

    log_file = sys.argv[1]
    keyword = sys.argv[2] if len(sys.argv) > 2 else "NONE"
    log_level = sys.argv[3] if len(sys.argv) > 3 else "NONE"
    start_date = sys.argv[4] if len(sys.argv) > 4 else "NONE"
    end_date = sys.argv[5] if len(sys.argv) > 5 else "NONE"

    results = search_logs(log_file, keyword, log_level, start_date, end_date)

    for result in results:
        print(result)