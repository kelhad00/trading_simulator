from modules import load_data, save_data
from time import sleep
from groq import Groq
import pandas as pd
import datetime

'''
    Warning : The user need to have the news_dataset.csv file in the data folder

    TODO: Create a field to get the user groq api key
'''

def get_api_key():
    '''
    Get the user groq api key
    '''

    return None


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


def create_news_for_companies(DATASET_PATH, SAVE_DATA_PATH, company_news, model, number_of_news, sentiment):
    '''
    Create some news for the companies
    '''

    # Create a Groq client
    client = Groq(
        api_key=get_api_key(),
    )

    # Load the dataset
    dataset = load_data(DATASET_PATH)

    # Create a dataframe to store the news we have created
    news_created = pd.DataFrame(columns=['date', 'ticker', 'sector', 'title', 'content', 'sentiment'])

    for index, row in company_news.iterrows():
        # Get the sector of the companies we want to create some news for
        sector = row['sector']

        # Check if the subset is well represented in the dataset
        subset = dataset.query('sector == @sector & sentiment == @sentiment')
        if len(subset) >= number_of_news:
            # The sector is in the dataset and there are more than 'number_of_news' of them

            # Create the news
            for news in subset.sample(number_of_news).iterrows():
                try:
                    content = transform_news_content(news[1]['content'], row['name'], client, model, sentiment)
                except Exception as e:
                    print('Need to wait 1 minute...')
                    sleep(60)
                    content = transform_news_content(news[1]['content'], row['name'], client, model, sentiment)

                # Create a new row in news_created
                try:
                    news_created.loc[len(news_created)] = [datetime.date(1,1,1), row['ticker'], sector, transform_news_title(content, client, model), content, sentiment]
                except Exception as e:
                    print('Need to wait 1 minute...')
                    sleep(60)
                    news_created.loc[len(news_created)] = [datetime.date(1,1,1), row['ticker'], sector, transform_news_title(content, client, model), content, sentiment]

                
                print("News created for " + row['name'])

                # Set a delay to avoid the rate limit
                sleep(6)

            # Save the news created in a csv file
            save_data(news_created, SAVE_DATA_PATH)

        else:
            # The sector is not in the dataset or there are not enough of them
            print('There are not enough news for the sector of ' + row['name'] + ' in the dataset')
