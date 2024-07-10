from time import sleep
from groq import Groq
import pandas as pd
import os

from trade.utils.news_generation.modules import load_data, save_data
from trade.utils.news_generation.modules import random_number, percentage_change
from trade.utils.market import get_market_dataframe
from trade.utils.news_generation.modules import find_sector_for_company
from trade.defaults import defaults as dlt


def create_news_for_companies(companies, activities, news_position, api):
    model = 'llama3-70b-8192'
    news_path = os.path.join(dlt.data_path, 'news.csv')

    # Create a dataframe to store the news we have created
    news_created = pd.DataFrame(columns=['date', 'ticker', 'sector', 'title', 'content', 'sentiment'])

    for ticker, company_name in companies.items():
        company_sector = find_sector_for_company(ticker, activities)
        
        n = create_news(ticker, company_name, company_sector, news_position[ticker], model, api)

        news_created = pd.concat([news_created, n])

    # Save the news created
    save_data(news_created, news_path)
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

    for company in companies.keys():
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

    return (positive_positions, negative_positions)

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
            news_created.loc[len(news_created)] = [market_data.iloc[position]['date'], company_name, sector, title, content, sentiment]
 
            print("News created for " + company_name)
            i += 1

            # Set a delay to avoid the rate limit
            sleep(6)

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
            """except Exception as e:
                print('Need to wait 1 minute...')
                sleep(60)
                content = transform_news_content(news[1]['content'], row['name'], client, model, sentiment)"""

            # Create a new row in news_created
            news_created.loc[len(news_created)] = [market_data.iloc[position]['date'], company_name, sector, title, content, sentiment]
 
            print("News created for " + company_name)
            i += 1

            # Set a delay to avoid the rate limit
            sleep(6)

    else:
        # The sector is not in the dataset or there are not enough of them
        raise Exception('There are not enough negative news for the sector of ' + company_name + ' in the dataset')

    return news_created


def transform_news_content(content, company, client, model, sentiment):
    '''
    Transform the content of a news into a news for the company with a LLM
    '''

    if sentiment == 'negative':
        sent = 'négatif'
    else:
        sent = 'positif'

    # Prompt for the LLM
    p = """Contexte:
    Vous recevez une nouvelle concernant une entreprise. Vous devez reformuler cette nouvelle pour qu'elle s'applique à l'entreprise {company}, une autre entreprise du même secteur. Les actionnaires doivent recevoir cette nouvelle avec un ton formel, informatif et {sentiment}.

    Nouvelle originale:
    {data}

    Tâche:
    Reformulez la nouvelle ci-dessus pour qu'elle concerne l'entreprise {company} et fournissez directement le texte reformulé SANS préambules, introduction ou note supplémentaire ! La réponse doit être en français.""".format(data=content, company=company, sentiment=sent)

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
    p = """Contexte:
    Vous recevez une nouvelle concernant une entreprise. Vous devez créer un court titre qui résume au mieux cette nouvelle. Le titre doit être informatif et attirer l'attention des lecteurs.

    Nouvelle :
    {data}

    Tâche:
    Créez un titre par rapport à la nouvelle ci-dessus et fournissez directement le titre SANS préambules, introduction ou note supplémentaire ! La réponse doit être en français.""".format(data=content)

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
