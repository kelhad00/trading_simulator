from time import sleep
from groq import Groq
import pandas as pd
import os
import random
from datetime import datetime

from trade.utils.news_generation.modules import load_data, save_data
from trade.utils.news_generation.modules import percentage_change
from trade.utils.market import get_market_dataframe
from trade.utils.news_generation.modules import find_sector_for_company
from trade.defaults import defaults as dlt


def create_news_for_companies(companies, news_position, lang, api):
    model = 'llama-3.1-8b-instant'
    news_path = os.path.join(dlt.data_path, 'news.csv')

    for ticker, company_info in companies.items():
        company_sector = company_info['activity']
        company_name = company_info['label']
        curve_profile = company_info.get('curve_profile', 'linear')
        if company_info['got_charts'] is True and ticker in news_position:
            n = create_news(ticker, company_name, company_sector, curve_profile, lang, news_position[ticker], model, api)

            # Save immediately after each company so a crash never loses progress.
            # Replace only this company's existing news, keep everyone else's.
            if os.path.exists(news_path):
                try:
                    existing = load_data(news_path)
                    existing = existing[existing['ticker'] != company_name]
                    n = pd.concat([existing, n]).reset_index(drop=True)
                except pd.errors.EmptyDataError:
                    pass  # empty file — nothing to merge, just save the new news

            save_data(n, news_path)
            print(f'News saved for {company_name}')
        

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
            if company in generated_market_data.keys():
                try:
                    if mode == "random":
                        news_positions[company] = get_news_position_rand(generated_market_data[company], nbr_positive_news, nbr_negative_news, alpha, alpha_day_interval, delta)
                    else:
                        news_positions[company] = get_news_position_lin(generated_market_data[company], alpha, alpha_day_interval, delta)
                except Exception as e:
                    print(f"Skipping news positions for {company}: {e}")

    return news_positions


def get_news_position_rand(market_data, nbr_positive_news, nbr_negative_news, alpha, alpha_day_interval, delta):
    '''
    Get a defined number of random positions for news in the market data.
    Scores every valid position by its percentage change, then picks the top N
    for positive news and the bottom N for negative news.  Falls back to this
    rank-based selection when the alpha threshold yields too few results, so the
    function never fails due to a monotone or mostly-directional curve.
    '''

    data_size = market_data.shape[0]
    close = market_data['Close']

    # Build a scored list of (change, position) for every valid row pair
    scored = []
    for index in range(1, data_size - alpha_day_interval):
        prev = close.iloc[index]
        curr = close.iloc[index + alpha_day_interval]
        if pd.isna(prev) or pd.isna(curr) or prev == 0:
            continue
        scored.append((percentage_change(prev, curr), index - delta))

    needed = nbr_positive_news + nbr_negative_news
    if len(scored) < needed:
        raise Exception(
            f"Not enough data: only {len(scored)} valid positions found, "
            f"need at least {needed}."
        )

    scored.sort(key=lambda x: x[0])

    # Try alpha threshold first; fall back to rank-based selection
    positive_pool = [pos for chg, pos in scored if chg >= alpha]
    negative_pool = [pos for chg, pos in scored if chg <= -alpha]

    if len(positive_pool) < nbr_positive_news:
        # Take the top N*3 changes (most positive available)
        positive_pool = [pos for _, pos in scored[-(nbr_positive_news * 3):]]

    if len(negative_pool) < nbr_negative_news:
        # Take the bottom N*3 changes (most negative available)
        negative_pool = [pos for _, pos in scored[:(nbr_negative_news * 3)]]

    return (
        random.sample(positive_pool, nbr_positive_news),
        random.sample(negative_pool, nbr_negative_news),
    )


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

def create_news(company_ticker, company_name, company_sector, curve_profile, lang, news_position, model, api):
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
            content = transform_news_content(news.iloc[i]['content'], company_name, sector, curve_profile, lang, client, model, sentiment)
            title = transform_news_title(content, company_name, curve_profile, lang, client, model)

            # Create a new row in news_created

            date = market_data.iloc[position]['date']
            date = datetime.fromisoformat(date)
            date = date.strftime('%d/%m/%y %H:%M')


            news_created.loc[len(news_created)] = [date, company_name, sector, title, content, sentiment]

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
            content = transform_news_content(news.iloc[i]['content'], company_name, sector, curve_profile, lang, client, model, sentiment)
            title = transform_news_title(content, company_name, curve_profile, lang, client, model)

            # Create a new row in news_created
            date = market_data.iloc[position]['date']
            date = datetime.fromisoformat(date).strftime('%d/%m/%y %H:%M')
            news_created.loc[len(news_created)] = [date, company_name, sector, title, content, sentiment]

            print("News created for " + company_name)
            i += 1

            # Set a delay to avoid the rate limit
            sleep(6)

    else:
        # The sector is not in the dataset or there are not enough of them
        raise Exception('There are not enough negative news for the sector of ' + company_name + ' in the dataset')

    return news_created


def transform_news_content(content, company, sector, curve_profile, lang, client, model, sentiment):
    '''
    Transform the content of a news into a news for the company with a LLM
    '''

    if lang == "en":
        curve_descriptions = {
            "linear":      ("steady linear growth", "stable growth"),
            "exponential": ("exponential growth and strong acceleration", "strong growth"),
            "logarithmic": ("rapid early growth then gradual slowdown", "market maturity"),
            "volatile":    ("highly volatile and unpredictable movement", "high volatility"),
            "crash":       ("sharp decline after a growth phase", "crisis and decline"),
        }
        sentiment_label = "negative" if sentiment == "negative" else "positive"
    else:
        curve_descriptions = {
            "linear":      ("croissance linéaire et régulière", "croissance stable"),
            "exponential": ("croissance exponentielle et forte accélération", "forte croissance"),
            "logarithmic": ("croissance rapide puis ralentissement progressif", "maturité du marché"),
            "volatile":    ("évolution très volatile et imprévisible", "forte volatilité"),
            "crash":       ("déclin brutal après une phase de croissance", "crise et déclin"),
        }
        sentiment_label = "négatif" if sentiment == "negative" else "positif"

    curve_description, curve_description_short = curve_descriptions.get(curve_profile, list(curve_descriptions.values())[0])

    language_instruction = "The response must be written in English." if lang == "en" else "La réponse doit être en français."

    p = """Context:
You receive a reference financial news article. Rewrite it to be specifically about the company {company}, which operates in the sector: {sector}.

Company market profile: {curve_description}

News sentiment: {sentiment_label}

Reference article:
{data}

Task:
Rewrite this article so it is directly about {company}, taking into account its sector and current market profile. The tone must reflect the market profile ({curve_description_short}). Reply ONLY with the rewritten article text, no preamble or notes. {language_instruction}""".format(
        data=content,
        company=company,
        sector=sector,
        curve_description=curve_description,
        curve_description_short=curve_description_short,
        sentiment_label=sentiment_label,
        language_instruction=language_instruction,
    )

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


def transform_news_title(content, company_name, curve_profile, lang, client, model):
    '''
    Create a title from a content of a news for the company with a LLM
    '''

    if lang == "en":
        curve_descriptions_short = {
            "linear":      "stable growth",
            "exponential": "strong growth",
            "logarithmic": "market maturity",
            "volatile":    "high volatility",
            "crash":       "crisis and decline",
        }
    else:
        curve_descriptions_short = {
            "linear":      "croissance stable",
            "exponential": "forte croissance",
            "logarithmic": "maturité du marché",
            "volatile":    "forte volatilité",
            "crash":       "crise et déclin",
        }

    curve_description_short = curve_descriptions_short.get(curve_profile, list(curve_descriptions_short.values())[0])
    language_instruction = "The response must be written in English." if lang == "en" else "La réponse doit être en français."

    p = """Context:
You receive a financial news article about the company {company}. Its market profile is: {curve_description_short}.

Article:
{data}

Task:
Write a short, punchy headline for this article. The headline must mention {company} and reflect the {curve_description_short} tone. Reply ONLY with the headline, no preamble or trailing punctuation. {language_instruction}""".format(
        data=content,
        company=company_name,
        curve_description_short=curve_description_short,
        language_instruction=language_instruction,
    )

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
