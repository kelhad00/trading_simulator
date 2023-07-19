## Emotrade

Emotrade is a Python library to study traders actions in stocks. Launch the Emotrade pyhton file to open the app with the shares and stocks. Emotrade can also launch a webcam, a shimmer and a Tobii. 
Describe the project purpose. 

## Installation/Instruction

Use the package manager [pip](link to source) to install Emotrade.

```bash
pip install emotrade
```

## File Tree Structure

The emotrade directory contains the necessary files and folders to run the trading simulator. Here is a description of the main directories:

- `app.py`: The main application file. This is the entry point to launch the trading simulator.

- `Components`: This directory contains files that implement different functionalities of the trading simulator, such as generating charts, managing financial news, or handling the portfolio.

- `Layouts`: This directory contains files related to the layout and user interface of the application. It defines the visual structure of the application.

- `Setup`: This directory contains configuration and preparation files for the application, such as downloading market data and financial news required for the simulation. This submodule should not be imported into other project files. It allows library users to access information on other actions collected by the various files in this directory.

- `States`: This directory contains files that manage the states or sessions of the application. It allows loading previously downloaded market data and saving the current state of the application.

## Usage

```python
import emotrade
```