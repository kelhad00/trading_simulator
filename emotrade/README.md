## Emotrade

Emotrade is a Python app developed using Dash librairy. It simulate stock exchanges and trading.

It was developed for research purpose in finance. 

On the app you will be able to make request (buy or sell shares of a company), visualize the shares and the incomes of the companies with graphs, visualize your shares with your portfolio and check the news. 

The app is available in english and in french. 

## Installation/Instruction

The app is run locally. 

To install the app, follow the steps below :
- Fork this repository,
- Clone the directory,
-

Launch the python file named 'app.py' to open the app. 

```bash
# Install emotrade
```

## File Tree Structure

The emotrade directory contains the necessary files and folders to run the trading simulator. Here is a description of the main directories:

- `app.py`: The main application file. This is the entry point to launch the trading simulator.

- `Components`: This directory contains files that implement different functionalities of the trading simulator, such as generating charts, managing financial news, or handling the portfolio.

- `Locales`: This directory contains the files with the english en french translations. 

- `Layouts`: This directory contains files related to the layout and user interface of the application. It defines the visual structure of the application.

- `Setup`: This directory contains configuration and preparation files for the application, such as downloading market data and financial news required for the simulation. This submodule should not be imported into other project files. It allows library users to access information on other actions collected by the various files in this directory.

- `States`: This directory contains files that manage the states or sessions of the application. It allows loading previously downloaded market data and saving the current state of the application.

## Usage and Contribution

How to use the project and how to contribute to it.
Provide instructions and examples so users/contributors can use the project.

```python
# emotrade
```

## Credits

This project was managed by Kevin El Haddad and it was developed by Gatien Villain and Capucine Fouillard. 