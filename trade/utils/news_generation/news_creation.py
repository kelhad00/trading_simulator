import time
from time import sleep
from groq import Groq
import pandas as pd
import os
from datetime import datetime
from transformers import pipeline


from trade.utils.news import get_news_dataframe
from trade.utils.news_generation.modules import load_data, save_data
from trade.utils.news_generation.modules import random_number, percentage_change
from trade.utils.market import get_market_dataframe
from trade.utils.news_generation.modules import find_sector_for_company
from trade.defaults import defaults as dlt


def create_news_for_companies(companies, news_position, api):
    model = 'llama3-70b-8192'
    news_path = os.path.join(dlt.data_path, 'news_fr.csv')

    # Create a dataframe to store the news we have created
    news_created = pd.DataFrame(columns=['date', 'ticker', 'sector', 'title', 'content', 'sentiment'])

    for ticker, company_info in companies.items():
        company_sector = company_info['activity']
        company_name = company_info['label']
        if company_info['got_charts'] is True:
            n = create_news(ticker, company_name, company_sector, news_position[ticker], model, api)
            news_created = pd.concat([news_created, n])

    # Save the news created
    save_data(news_created, news_path)

    #Traduction English
    news_path = os.path.join(dlt.data_path, 'news_en.csv')

    translator = FrenchToEnglishTranslator()

    news_created_trad = translator.translate_dataframe(news_created,['title','content'])

    save_data(news_created_trad, news_path)

    print('News created and saved in ' + news_path)
        

def get_news_position_for_companies(companies, mode, nbr_positive_news, nbr_negative_news, alpha, alpha_day_interval, delta):
    '''
    Get the position of the news for all companies
    Parameters:
        - companies : the companies to generate the news position
        - mode : the mode to generate the news position
    '''

    # Load the market data
    generated_market_data = get_market_dataframe()

    # Create a dictionary to store the news positions
    news_positions = {}

    for company, values in companies.items():
        if values["got_charts"] is True:
        # Generate the news position for the generated data companies
            if company in generated_market_data.keys():
                if mode == "random":
                    news_positions[company] = get_news_position_rand(generated_market_data[company], nbr_positive_news, nbr_negative_news, alpha, alpha_day_interval, delta)
                else:
                    news_positions[company] = get_news_position_lin(generated_market_data[company], alpha, alpha_day_interval, delta)

    return news_positions


def get_news_position_rand(market_data, nbr_positive_news, nbr_negative_news, alpha, alpha_day_interval, delta):
    '''
    Get a defined numbers of random possible position of the news in the market data
    Parameters:
        - alpha : the minimum percentage of market variation to place a news
        - alpha_day_interval : the number of days between the two days used to calculate the percentage change
        - delta : the number of days to shift the news position
    '''

    # List of possible positions
    positive_positions = []
    negative_positions = []

    # Get the size of the market data
    data_size = market_data.shape[0]

    for p in range(nbr_positive_news):
        i = 0
        while True:
            rand = random_number(data_size - 1 - alpha_day_interval)
            i += 1

            # Calculate the percentage change compared to 3 days later
            change = percentage_change(market_data['Close'].iloc[rand], market_data['Close'].iloc[rand + alpha_day_interval])

            if (rand - delta) not in positive_positions:
                if change >= alpha:
                    i = 0
                    positive_positions.append(rand - delta)
                    break

            # Break if it's impossible to found others position
            if i > 1000:
                raise Exception("Not enough position found for the positive news, reduce the number of news or the alpha value.")
            
    for n in range(nbr_negative_news):
        i = 0
        while True:
            rand = random_number(data_size - 1 - alpha_day_interval)
            i += 1

            # Calculate the percentage change compared to 3 days later
            change = percentage_change(market_data['Close'].iloc[rand], market_data['Close'].iloc[rand + alpha_day_interval])

            if (rand - delta) not in negative_positions:
                if change <= -alpha:
                    i = 0
                    negative_positions.append(rand - delta)
                    break

            # Break if it's impossible to found others position
            if i > 1000:
                raise Exception("Not enough position found for the negative news, reduce the number of news or the alpha value.")
            
    return (positive_positions, negative_positions)


def get_news_position_lin(market_data, alpha, alpha_day_interval, delta):
    '''
    Get all possible position of the news in the market data in function of the parameters
    Parameters:
        - alpha : the minimum percentage of market variation to place a news
        - alpha_day_interval : the number of days between the two days used to calculate the percentage change
        - delta : the number of days to shift the news position
    '''

    # List of possible positions
    positive_positions = []
    negative_positions = []

    # Get the size of the market data
    data_size = market_data.shape[0]

    for index in range(alpha_day_interval, data_size - alpha_day_interval):
        # Calculate the percentage change compared to 3 days later
        change = percentage_change(market_data['Close'].iloc[index], market_data['Close'].iloc[index + alpha_day_interval])

        if change >= alpha:
            positive_positions.append(index - delta)
        elif change <= -alpha:
            negative_positions.append(index - delta)

    return positive_positions, negative_positions

def create_news(company_ticker, company_name, company_sector, news_position, model, api):
    '''
    Create news for a company based on the position in market data given
    '''

    # Paths
    dataset_path = os.path.join(dlt.data_path, 'news_dataset.csv')

    # Create a Groq client
    client = Groq(
        api_key=api,
    )

    # Load the dataset & market data
    dataset = load_data(dataset_path)
    market_data = get_market_dataframe()[company_ticker]
    market_data = market_data.reset_index(drop=False)

    # Create a dataframe to store the news we have created
    news_created = pd.DataFrame(columns=['date', 'ticker', 'sector', 'title', 'content', 'sentiment'])

    # Browse the positive positions
    sentiment = 'positive'
    sector = company_sector
    subset = dataset.query('sector == @sector & sentiment == @sentiment')
    # Check if the subset is well represented in the dataset

    if len(subset) >= len(news_position[0]):
        news = subset.sample(len(news_position[0]))

        i = 0
        for position in news_position[0]:
            # Create the news
            content = transform_news_content(news.iloc[i]['content'], company_name, client, model, sentiment)
            title = transform_news_title(content, client, model)
            # Create a new row in news_created

            date = market_data.iloc[position]['index']
            date = datetime.fromisoformat(date)
            date = date.strftime('%d/%m/%y %H:%M')


            news_created.loc[len(news_created)] = [date, company_name, sector, title, content, sentiment]

            i += 1
            print("News created for " + company_name)
            print(f"Positive news number {i} / {len(news_position[0])}")
            # Set a delay to avoid the rate limit
            time.sleep(6)
    else:
        # The sector is not in the dataset or there are not enough of them
        raise Exception('There are not enough positive news for the sector of ' + company_name + ' in the dataset')

    # Browse the negative positions
    sentiment = 'negative'
    sector = company_sector
    subset = dataset.query('sector == @sector & sentiment == @sentiment')
    # Check if the subset is well represented in the dataset
    if len(subset) >= len(news_position[1]):
        news = subset.sample(len(news_position[1]))

        i = 0
        for position in news_position[1]:
            # Create the news
            content = transform_news_content(news.iloc[i]['content'], company_name, client, model, sentiment)
            title = transform_news_title(content, client, model)

            # Create a new row in news_created

            date = market_data.iloc[position]['index']
            date = datetime.fromisoformat(date)
            date = date.strftime('%d/%m/%y %H:%M')

            # Create a new row in news_created
            news_created.loc[len(news_created)] = [date, company_name, sector, title, content, sentiment]
 
            i+=1
            print("News created for " + company_name)
            print(f"Negative news number {i} / {len(news_position[1])}")


            # Set a delay to avoid the rate limit
            sleep(6)

    else:
        # The sector is not in the dataset or there are not enough of them
        raise Exception('There are not enough negative news for the sector of ' + company_name + ' in the dataset')
    companies_list = list(dlt.companies_list)
    print(f"Company : {companies_list.index(company_ticker) + 1}/{len(companies_list) + 1}")
    companies_list = list(dlt.companies_list)
    progress = round(((companies_list.index(company_ticker) + 1) / (len(companies_list) + 1))*100, 2)
    print(f"Progress : {progress} %")
    return news_created


def transform_news_content(content, company, client, model, sentiment):
    '''
    Transform the content of a news into a news for the company with a LLM
    '''

    if sentiment == 'negative':
        sentiment = 'négatif'
    else:
        sentiment = 'positif'

    # Prompt for the LLM
    p = f"""Contexte:
    Vous recevez une nouvelle concernant une entreprise. Vous devez reformuler cette nouvelle pour qu'elle s'applique à l'entreprise {company}, une autre entreprise du même secteur. Les actionnaires doivent recevoir cette nouvelle avec un ton formel, informatif et {sentiment}.

    Nouvelle originale:
    {content}

    Tâche:
    Reformulez la nouvelle ci-dessus pour qu'elle concerne l'entreprise {company} et fournissez directement le texte reformulé SANS préambules, introduction ou note supplémentaire ! La réponse doit être en français."""

    # Create a news for the company
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": p,
            }
        ],
        model=model,
    )

    return response.choices[0].message.content


def transform_news_title(content, client, model):
    '''
    Create a title from a content of a news for the company with a LLM
    '''
    # Prompt for the LLM
    p = f"""Contexte:
    Vous recevez une nouvelle concernant une entreprise. Vous devez créer un court titre qui résume au mieux cette nouvelle. Le titre doit être informatif et attirer l'attention des lecteurs.

    Nouvelle :
    {content}

    Tâche:
    Créez un titre par rapport à la nouvelle ci-dessus et fournissez directement le titre SANS préambules, introduction ou note supplémentaire ! La réponse doit être en français."""

    # Create a news for the company
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": p,
            }
        ],
        model=model,
    )

    return response.choices[0].message.content

def load_translator(model_name: str = "Helsinki-NLP/opus-mt-fr-en"):
    """
    Loads a translation pipeline for French to English.
    """
    return pipeline("translation_fr_to_en", model=model_name)

class FrenchToEnglishTranslator:
    def __init__(self, model_name: str = "Helsinki-NLP/opus-mt-fr-en"):
        self.translator = load_translator(model_name)

    def translate_text(self, text: str) -> str:
        """
        Translate a single French string to English.
        """
        result = self.translator(text)
        return result[0]['translation_text']

    def translate_list(self, texts: list[str]) -> list[str]:
        """
        Translate a list of French strings to English.
        """
        results = self.translator(texts)
        return [res['translation_text'] for res in results]

    def translate_dataframe(self, df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
        """
        Translate specified DataFrame columns from French to English in place.
        :param df: pandas DataFrame
        :param columns: list of column names to translate
        :return: DataFrame with translated columns
        """
        for col in columns:
            # Drop NaNs or non-strings if needed
            df[col] = df[col].fillna("")
            texts = df[col].astype(str).tolist()
            translations = self.translate_list(texts)
            df[col] = translations
        return df

