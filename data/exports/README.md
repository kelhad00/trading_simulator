# Exports
This directory contains the exports of the data from the database. The exports are in CSV format.

## Session 
Each session is exported in a separate folder. The folder name is the session id.

## Files
Each session folder contains the following files:
- `interface-logs.csv` : contains the logs of the interface
- `portfolio-logs.csv` : contains the logs of the portfolio
- `request-logs.csv` : contains the logs of the requests

`interface-logs.csv` contains an ID column that is used to join the logs of the interface with the logs of the portfolio and the logs of the requests.
