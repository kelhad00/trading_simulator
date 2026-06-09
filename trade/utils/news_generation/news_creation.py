from openai import OpenAI, RateLimitError
import pandas as pd
import os
import random
import functools
import time
from datetime import datetime

# Force all print() calls in this module to flush immediately so logs appear
# in the terminal in real time instead of being held in Python's output buffer.
print = functools.partial(print, flush=True)

from trade.utils.news_generation.modules import load_data, save_data
from trade.utils.news_generation.modules import percentage_change
from trade.utils.market import get_market_dataframe
from trade.utils.news_generation.modules import find_sector_for_company
from trade.utils.news_generation.verify import verify_article
from trade.defaults import defaults as dlt

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "llama-3.3-70b-versatile"
OLLAMA_MODEL = "qwen3:8b"


def _build_client(provider, base_url, groq_api_key):
    """Return (OpenAI client, model name) for the chosen provider."""
    if provider == "groq":
        return OpenAI(base_url=GROQ_BASE_URL, api_key=groq_api_key), GROQ_MODEL
    return OpenAI(base_url=base_url, api_key="ollama"), OLLAMA_MODEL


def _chat_with_retry(client, model, messages, max_retries=4):
    """Call the chat API with exponential back-off on rate-limit errors."""
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(messages=messages, model=model)
        except RateLimitError:
            if attempt < max_retries - 1:
                wait = 10 * (2 ** attempt)  # 10s → 20s → 40s → 80s
                print(f"[NEWS] Rate limit hit — waiting {wait}s (attempt {attempt + 1}/{max_retries})...")
                time.sleep(wait)
            else:
                raise


def create_news_for_companies(companies, news_position, lang, provider="ollama",
                               base_url="http://localhost:11434/v1", groq_api_key="", delta=0):
    _, model = _build_client(provider, base_url, groq_api_key)
    news_path = os.path.join(dlt.data_path, 'news.csv')

    endpoint = GROQ_BASE_URL if provider == "groq" else base_url
    print(f"[NEWS] Starting article generation for {len(news_position)} companies using {provider} ({endpoint})")

    report_path = os.path.join(dlt.data_path, 'verification_report.csv')
    total_verified = 0
    total_passed   = 0

    for ticker, company_info in companies.items():
        company_sector = company_info['activity']
        company_name = company_info['label']
        curve_profile = company_info.get('curve_profile', 'linear')
        company_description = company_info.get('description', '')

        if company_info.get('got_charts') is not True:
            continue
        if ticker not in news_position:
            print(f"[NEWS] {company_name} ({ticker}) — no positions found, skipping")
            continue
        pos = news_position[ticker]
        if not pos[0] and not pos[1]:
            print(f"[NEWS] {company_name} ({ticker}) — position lists are empty, skipping")
            continue

        print(f"[NEWS] Generating articles for {company_name} — {len(pos[0])} positive, {len(pos[1])} negative")
        n, v_results = create_news(ticker, company_name, company_sector, curve_profile, lang, pos, model, provider, base_url, groq_api_key, company_description, delta)

        # ── Save news immediately (per company) ───────────────────────────────
        if os.path.exists(news_path):
            try:
                existing = load_data(news_path)
                existing = existing[existing['ticker'] != company_name]
                n = pd.concat([existing, n]).reset_index(drop=True)
            except pd.errors.EmptyDataError:
                pass
        save_data(n, news_path)
        print(f"[NEWS] ----------------------------------------")
        print(f"[NEWS] All articles for {company_name} written to file.")
        print(f"[NEWS] File : {news_path}")
        print(f"[NEWS] Total rows now in file: {len(n)}")
        print(f"[NEWS] ----------------------------------------")

        # ── Save verification report immediately (per company) ────────────────
        if v_results:
            new_rows = pd.DataFrame(v_results)
            if os.path.exists(report_path):
                try:
                    existing_report = pd.read_csv(report_path)
                    existing_report = existing_report[existing_report['company'] != company_name]
                    new_rows = pd.concat([existing_report, new_rows]).reset_index(drop=True)
                except (pd.errors.EmptyDataError, KeyError):
                    pass
            new_rows.to_csv(report_path, index=False)
            company_passed = sum(1 for r in v_results if r['passed'])
            total_verified += len(v_results)
            total_passed   += company_passed
            print(f"[VERIFY] {company_name} — {company_passed}/{len(v_results)} passed | report updated")

    flagged = total_verified - total_passed
    if total_verified:
        print(f"[VERIFY] Report saved → {report_path}  ({total_passed}/{total_verified} passed, {flagged} flagged)")
        return {'total': total_verified, 'passed': total_passed, 'flagged': flagged}

    return {'total': 0, 'passed': 0, 'flagged': 0}


def get_news_position_manual(market_data, positive_dates, negative_dates):
    '''
    Convert user-provided dates to row indices for manual news placement.
    Normalises both the market data index and the stored dates to YYYY-MM-DD
    so timezone suffixes and time components never cause a mismatch.
    Delta is intentionally not applied — the user has already chosen the
    exact date by clicking, so there is nothing to shift.
    Returns the same (positive_positions, negative_positions) tuple as the
    other position functions.
    '''
    index_list = [str(d)[:10] for d in market_data.index]
    data_size = len(index_list)

    def to_index(date_str):
        prefix = str(date_str)[:10]
        try:
            idx = index_list.index(prefix)
            return idx if 0 <= idx < data_size else None
        except ValueError:
            return None

    positive_positions = [i for d in positive_dates if (i := to_index(d)) is not None]
    negative_positions = [i for d in negative_dates if (i := to_index(d)) is not None]
    return (positive_positions, negative_positions)


def get_news_position_for_companies(companies, mode, nbr_positive_news, nbr_negative_news, alpha, alpha_day_interval, delta, k=0, manual_positions=None):
    '''
    Get the position of the news for all companies
    Parameters:
        - companies : the companies to generate the news position
        - mode : the mode to generate the news position
        - k : top-K filter for linear mode (0 = no limit, use all positions above alpha)
    '''

    print(f"[NEWS] Starting position generation — mode={mode}, companies={list(companies.keys())}")

    # Load the market data
    generated_market_data = get_market_dataframe()

    if generated_market_data is None:
        print("[NEWS] ERROR: No market data found — cannot generate positions.")
        return {}

    available = list(generated_market_data.columns.get_level_values(0).unique())
    print(f"[NEWS] Market data available for: {available}")

    # Create a dictionary to store the news positions
    news_positions = {}

    for company, values in companies.items():
        if values.get("got_charts") is not True:
            print(f"[NEWS] Skipping {company} — got_charts is not True")
            continue
        if company not in available:
            print(f"[NEWS] Skipping {company} — not found in market data")
            continue
        try:
            if manual_positions and company in manual_positions:
                pos = manual_positions[company]
                news_positions[company] = get_news_position_manual(
                    generated_market_data[company],
                    pos.get("positive", []),
                    pos.get("negative", []),
                )
                print(f"[NEWS] {company} — manual: {len(news_positions[company][0])} positive, {len(news_positions[company][1])} negative")
            elif mode == "random":
                news_positions[company] = get_news_position_rand(generated_market_data[company], nbr_positive_news, nbr_negative_news, alpha, alpha_day_interval, delta)
                print(f"[NEWS] {company} — random: {len(news_positions[company][0])} positive, {len(news_positions[company][1])} negative")
            else:
                news_positions[company] = get_news_position_lin(generated_market_data[company], alpha, alpha_day_interval, delta, k)
                print(f"[NEWS] {company} — linear: {len(news_positions[company][0])} positive, {len(news_positions[company][1])} negative")
        except Exception as e:
            print(f"[NEWS] Skipping {company} — error finding positions: {e}")

    print(f"[NEWS] Position generation complete — {len(news_positions)} companies ready")
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
        shifted_pos = index + delta
        if shifted_pos < 0 or shifted_pos >= data_size:
            continue
        scored.append((percentage_change(prev, curr), shifted_pos))

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


def get_news_position_lin(market_data, alpha, alpha_day_interval, delta, k=0):
    '''
    Get possible positions of the news in the market data in function of the parameters.
    If k=0, all positions above alpha are returned (original behaviour).
    If k>0, only the top-k positions with the highest absolute change are returned.
    '''

    positive_scored = []
    negative_scored = []

    data_size = market_data.shape[0]

    for index in range(alpha_day_interval, data_size - alpha_day_interval):
        change = percentage_change(market_data['Close'].iloc[index], market_data['Close'].iloc[index + alpha_day_interval])
        shifted_pos = index + delta
        if shifted_pos < 0 or shifted_pos >= data_size:
            continue
        if change >= alpha:
            positive_scored.append((change, shifted_pos))
        elif change <= -alpha:
            negative_scored.append((change, shifted_pos))

    if k > 0:
        positive_scored.sort(key=lambda x: x[0], reverse=True)
        negative_scored.sort(key=lambda x: x[0])
        positive_positions = [pos for _, pos in positive_scored[:k]]
        negative_positions = [pos for _, pos in negative_scored[:k]]
    else:
        positive_positions = [pos for _, pos in positive_scored]
        negative_positions = [pos for _, pos in negative_scored]

    return (positive_positions, negative_positions)

def _currency_symbol(ticker):
    """Return € for European tickers (exchange suffix or known index), $ otherwise."""
    european_suffixes = ('.PA', '.MI', '.AS', '.BR', '.DE', '.MC', '.LS', '.CO', '.ST', '.HE', '.OL')
    european_indices  = ('^FCHI', '^GDAXI', '^AEX', '^BFX', '^IBEX', '^PSI20', '^OSEAX', '^OMXS30', '^OMXHPI', '^OMXC25')
    t = ticker.upper()
    return '€' if any(t.endswith(s) for s in european_suffixes) or t in european_indices else '$'


def create_news(company_ticker, company_name, company_sector, curve_profile, lang, news_position,
                model, provider="ollama", base_url="http://localhost:11434/v1", groq_api_key="",
                company_description="", delta=0):
    '''
    Create news for a company based on the position in market data given
    '''

    # Paths
    dataset_path = os.path.join(dlt.data_path, 'news_dataset.csv')

    client, _ = _build_client(provider, base_url, groq_api_key)
    currency = _currency_symbol(company_ticker)

    # Load the dataset & market data
    dataset = load_data(dataset_path)
    market_data = get_market_dataframe()[company_ticker]
    market_data = market_data.reset_index(drop=False)

    start_price    = float(market_data.iloc[0]['Close'])
    sim_start_date = str(market_data.iloc[0]['date'])[:10]
    sim_end_date   = str(market_data.iloc[-1]['date'])[:10]

    # Create a dataframe to store the news we have created
    news_created = pd.DataFrame(columns=['date', 'ticker', 'sector', 'title', 'content', 'sentiment'])
    verification_results = []

    # Browse the positive positions
    sentiment = 'positive'
    sector = company_sector
    subset = dataset.query('sector == @sector & sentiment == @sentiment')
    # Check if the subset is well represented in the dataset
    if len(subset) >= len(news_position[0]):
        news = subset.sample(len(news_position[0]))

        total_pos = len(news_position[0])
        print(f"[NEWS GEN] {company_name} — {total_pos} POSITIVE article(s) to generate")
        i = 0
        for position in news_position[0]:
            print(f"[NEWS GEN]   ({i + 1}/{total_pos}) Generating POSITIVE article...")

            # Extract real price context from simulation data
            current_price    = float(market_data.iloc[position]['Close'])
            price_high       = float(market_data['Close'].max())
            price_low        = float(market_data['Close'].min())
            article_date_str = str(market_data.iloc[position]['date'])[:10]

            # Create the news
            delta_label = f"BEFORE ({abs(delta)}d)" if delta < 0 else f"AFTER ({delta}d)" if delta > 0 else "AT EVENT"
            print(f"[NEWS GEN]     -> Context: date={article_date_str} | price={currency}{current_price:.2f} | range={currency}{price_low:.2f}–{currency}{price_high:.2f} | curve={curve_profile} | delta={delta} ({delta_label})")
            print(f"[NEWS GEN]     -> Sending content to {provider.capitalize()} for rewriting...")
            content = transform_news_content(news.iloc[i]['content'], company_name, sector, curve_profile, lang, client, model, sentiment, company_description,
                                             article_date=article_date_str, current_price=current_price, price_high=price_high, price_low=price_low,
                                             start_price=start_price, sim_start_date=sim_start_date, sim_end_date=sim_end_date, delta=delta, currency=currency)
            print(f"[NEWS GEN]     -> Content received. Generating title...")
            title = transform_news_title(content, company_name, curve_profile, lang, client, model, sentiment)
            print(f"[NEWS GEN]     -> Title: \"{title[:80]}{'...' if len(title) > 80 else ''}\"")

            # Create a new row in news_created
            date = market_data.iloc[position]['date']
            date = datetime.fromisoformat(date)
            date = date.strftime('%d/%m/%y %H:%M')


            news_created.loc[len(news_created)] = [date, company_name, sector, title, content, sentiment]

            v = verify_article(title, content, sentiment, company_name, curve_profile, lang)
            tone_sym    = '✓' if v['tone_ok']          else '✗'
            company_sym = '✓' if v['company_mentioned'] else '✗'
            curve_sym   = '✓' if v['curve_ok']          else '✗'
            lang_sym    = '✓' if v['language_ok']        else '✗'
            print(f"[VERIFY] (+) Article {i + 1}: grade={v['grade']} | tone={tone_sym}({v['tone_confidence']}) | company={company_sym} | curve={curve_sym}({v['curve_score']}) | lang={lang_sym}")
            if not v['passed']:
                print(f"[VERIFY]     Grade {v['grade']} — retrying once...")
                content = transform_news_content(news.iloc[i]['content'], company_name, sector, curve_profile, lang, client, model, sentiment, company_description,
                                                 article_date=article_date_str, current_price=current_price, price_high=price_high, price_low=price_low,
                                                 start_price=start_price, sim_start_date=sim_start_date, sim_end_date=sim_end_date, delta=delta, currency=currency)
                title   = transform_news_title(content, company_name, curve_profile, lang, client, model, sentiment)
                v = verify_article(title, content, sentiment, company_name, curve_profile, lang)
                news_created.at[len(news_created) - 1, 'title']   = title
                news_created.at[len(news_created) - 1, 'content'] = content
                print(f"[VERIFY]     Retry grade={v['grade']}")
            v['company'] = company_name
            v['sentiment_expected'] = sentiment
            v['date'] = article_date_str
            verification_results.append(v)

            print(f"[NEWS GEN]     [SAVED] POSITIVE article {i + 1}/{total_pos} stored for {company_name} (date: {date})")
            i += 1

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

        total_neg = len(news_position[1])
        print(f"[NEWS GEN] {company_name} — {total_neg} NEGATIVE article(s) to generate")
        i = 0
        for position in news_position[1]:
            print(f"[NEWS GEN]   ({i + 1}/{total_neg}) Generating NEGATIVE article...")

            # Extract real price context from simulation data
            current_price    = float(market_data.iloc[position]['Close'])
            price_high       = float(market_data['Close'].max())
            price_low        = float(market_data['Close'].min())
            article_date_str = str(market_data.iloc[position]['date'])[:10]

            # Create the news
            delta_label = f"BEFORE ({abs(delta)}d)" if delta < 0 else f"AFTER ({delta}d)" if delta > 0 else "AT EVENT"
            print(f"[NEWS GEN]     -> Context: date={article_date_str} | price={currency}{current_price:.2f} | range={currency}{price_low:.2f}–{currency}{price_high:.2f} | curve={curve_profile} | delta={delta} ({delta_label})")
            print(f"[NEWS GEN]     -> Sending content to {provider.capitalize()} for rewriting...")
            content = transform_news_content(news.iloc[i]['content'], company_name, sector, curve_profile, lang, client, model, sentiment, company_description,
                                             article_date=article_date_str, current_price=current_price, price_high=price_high, price_low=price_low,
                                             start_price=start_price, sim_start_date=sim_start_date, sim_end_date=sim_end_date, delta=delta, currency=currency)
            print(f"[NEWS GEN]     -> Content received. Generating title...")
            title = transform_news_title(content, company_name, curve_profile, lang, client, model, sentiment)
            print(f"[NEWS GEN]     -> Title: \"{title[:80]}{'...' if len(title) > 80 else ''}\"")

            # Create a new row in news_created
            date = market_data.iloc[position]['date']
            date = datetime.fromisoformat(date).strftime('%d/%m/%y %H:%M')
            news_created.loc[len(news_created)] = [date, company_name, sector, title, content, sentiment]

            v = verify_article(title, content, sentiment, company_name, curve_profile, lang)
            tone_sym    = '✓' if v['tone_ok']          else '✗'
            company_sym = '✓' if v['company_mentioned'] else '✗'
            curve_sym   = '✓' if v['curve_ok']          else '✗'
            lang_sym    = '✓' if v['language_ok']        else '✗'
            print(f"[VERIFY] (-) Article {i + 1}: grade={v['grade']} | tone={tone_sym}({v['tone_confidence']}) | company={company_sym} | curve={curve_sym}({v['curve_score']}) | lang={lang_sym}")
            if not v['passed']:
                print(f"[VERIFY]     Grade {v['grade']} — retrying once...")
                content = transform_news_content(news.iloc[i]['content'], company_name, sector, curve_profile, lang, client, model, sentiment, company_description,
                                                 article_date=article_date_str, current_price=current_price, price_high=price_high, price_low=price_low,
                                                 start_price=start_price, sim_start_date=sim_start_date, sim_end_date=sim_end_date, delta=delta, currency=currency)
                title   = transform_news_title(content, company_name, curve_profile, lang, client, model, sentiment)
                v = verify_article(title, content, sentiment, company_name, curve_profile, lang)
                news_created.at[len(news_created) - 1, 'title']   = title
                news_created.at[len(news_created) - 1, 'content'] = content
                print(f"[VERIFY]     Retry grade={v['grade']}")
            v['company'] = company_name
            v['sentiment_expected'] = sentiment
            v['date'] = article_date_str
            verification_results.append(v)

            print(f"[NEWS GEN]     [SAVED] NEGATIVE article {i + 1}/{total_neg} stored for {company_name} (date: {date})")
            i += 1

    else:
        # The sector is not in the dataset or there are not enough of them
        raise Exception('There are not enough negative news for the sector of ' + company_name + ' in the dataset')

    print(f"[NEWS GEN] ============================================")
    print(f"[NEWS GEN] DONE — {company_name} ({company_ticker})")
    print(f"[NEWS GEN]   Total articles generated : {len(news_created)}")
    print(f"[NEWS GEN]   Positive : {len(news_created[news_created['sentiment'] == 'positive'])}")
    print(f"[NEWS GEN]   Negative : {len(news_created[news_created['sentiment'] == 'negative'])}")
    print(f"[NEWS GEN] ============================================")
    return news_created, verification_results


def transform_news_content(content, company, sector, curve_profile, lang, client, model, sentiment,
                           company_description="", article_date=None, current_price=None, price_high=None,
                           price_low=None, start_price=None, sim_start_date=None, sim_end_date=None,
                           delta=0, currency='€'):
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
            "rally":       ("sharp upward surge — the stock is recovering and rising strongly", "strong rally"),
        }
    else:
        curve_descriptions = {
            "linear":      ("croissance linéaire et régulière", "croissance stable"),
            "exponential": ("croissance exponentielle et forte accélération", "forte croissance"),
            "logarithmic": ("croissance rapide puis ralentissement progressif", "maturité du marché"),
            "volatile":    ("évolution très volatile et imprévisible", "forte volatilité"),
            "crash":       ("déclin brutal après une phase de croissance", "crise et déclin"),
            "rally":       ("forte hausse — l'action est en plein rebond et progresse fortement", "fort rallye"),
        }

    curve_description, curve_description_short = curve_descriptions.get(curve_profile, list(curve_descriptions.values())[0])

    if article_date:
        article_year      = article_date[:4]
        article_prev_year = str(int(article_year) - 1)
        article_old_year  = str(int(article_year) - 2)
    else:
        article_year = article_prev_year = article_old_year = ""

    description_line = (
        f"\nCompany description: {company_description}" if lang == "en" and company_description.strip()
        else f"\nDescription de l'entreprise : {company_description}" if company_description.strip()
        else ""
    )

    # Build market context block
    if article_date and current_price is not None and price_low is not None and price_high is not None:
        if lang == "en":
            start_line = f"\n- Stock price at simulation start: {currency}{start_price:.2f}" if start_price is not None else ""
            window_line = f"\n- Simulation date window: {sim_start_date} to {sim_end_date}" if sim_start_date and sim_end_date else ""
            market_context = (
                f"\nMarket data at time of article:"
                f"\n- Article date: {article_date}"
                f"{window_line}"
                f"{start_line}"
                f"\n- Stock price on article date: {currency}{current_price:.2f}"
                f"\n- Full simulation price range: {currency}{price_low:.2f} – {currency}{price_high:.2f}"
            )
        else:
            start_line = f"\n- Prix de départ de la simulation : {start_price:.2f}{currency}" if start_price is not None else ""
            window_line = f"\n- Fenêtre de simulation : {sim_start_date} à {sim_end_date}" if sim_start_date and sim_end_date else ""
            market_context = (
                f"\nDonnées de marché au moment de l'article :"
                f"\n- Date de l'article : {article_date}"
                f"{window_line}"
                f"{start_line}"
                f"\n- Prix de l'action à la date de l'article : {current_price:.2f}{currency}"
                f"\n- Plage de prix de la simulation : {price_low:.2f}{currency} – {price_high:.2f}{currency}"
            )
    else:
        market_context = ""

    if delta < 0:
        if lang == "en":
            temporal_context = (
                f"\nTemporal context: this article is published {abs(delta)} day(s) BEFORE the price movement occurs."
                f"\nWrite it as an anticipatory piece — analysts are forecasting, warning, or predicting what is about to happen."
            )
        else:
            temporal_context = (
                f"\nContexte temporel : cet article est publié {abs(delta)} jour(s) AVANT le mouvement de prix."
                f"\nRédigez-le comme un article anticipatoire — les analystes prévoient, avertissent ou prédisent ce qui va se passer."
            )
    elif delta > 0:
        if lang == "en":
            temporal_context = (
                f"\nTemporal context: this article is published {delta} day(s) AFTER the price movement occurred."
                f"\nWrite it as a retrospective piece — explaining what happened, why, and its consequences."
            )
        else:
            temporal_context = (
                f"\nContexte temporel : cet article est publié {delta} jour(s) APRÈS le mouvement de prix."
                f"\nRédigez-le comme un article rétrospectif — expliquant ce qui s'est passé, pourquoi, et ses conséquences."
            )
    else:
        if lang == "en":
            temporal_context = (
                f"\nTemporal context: this article is published at the exact moment of the price movement."
                f"\nWrite it as a live report — describing what is happening right now."
            )
        else:
            temporal_context = (
                f"\nContexte temporel : cet article est publié au moment exact du mouvement de prix."
                f"\nRédigez-le comme un reportage en direct — décrivant ce qui se passe en ce moment."
            )

    # M4 — Unambiguous sentiment instruction
    if lang == "en":
        sentiment_instruction = (
            "The tone must be unmistakably NEGATIVE throughout — use vocabulary that signals decline, pressure, or concern (e.g. 'falls', 'slumps', 'fears', 'warning', 'losses'). The reader must be certain it is bad news from the very first sentence. Do not include any offsetting positive signals."
            if sentiment == "negative" else
            "The tone must be unmistakably POSITIVE throughout — use vocabulary that signals growth, strength, or confidence (e.g. 'rises', 'beats', 'record', 'gains', 'strong', 'momentum'). The reader must be certain it is good news from the very first sentence. Do not include any offsetting negative signals."
        )
    else:
        sentiment_instruction = (
            "Le ton doit être sans ambiguïté NÉGATIF dans tout l'article — utilisez un vocabulaire qui signale le déclin, la pression ou l'inquiétude (ex : 'chute', 'recul', 'pertes', 'avertissement', 'craintes'). Le lecteur doit être certain dès la première phrase que c'est une mauvaise nouvelle. N'incluez aucun signal positif compensatoire."
            if sentiment == "negative" else
            "Le ton doit être sans ambiguïté POSITIF dans tout l'article — utilisez un vocabulaire qui signale la croissance, la force ou la confiance (ex : 'hausse', 'dépasse', 'record', 'gains', 'solide', 'élan'). Le lecteur doit être certain dès la première phrase que c'est une bonne nouvelle. N'incluez aucun signal négatif compensatoire."
        )

    # M5 — Proportionate language based on actual price movement
    if start_price is not None and current_price is not None:
        pct = ((current_price - start_price) / start_price) * 100
        if lang == "en":
            direction = "up" if pct >= 0 else "down"
            price_movement = (
                f"The stock has moved {direction} {abs(pct):.1f}% from {currency}{start_price:.2f} at simulation start to {currency}{current_price:.2f} today. "
                f"The severity of events described must be proportionate to this actual movement — do not use catastrophic language for a modest move, and do not understate a large one."
            )
        else:
            direction_fr = "à la hausse" if pct >= 0 else "à la baisse"
            price_movement = (
                f"L'action a évolué {direction_fr} de {abs(pct):.1f}% depuis {start_price:.2f}{currency} au départ de la simulation jusqu'à {current_price:.2f}{currency} aujourd'hui. "
                f"La sévérité des événements décrits doit être proportionnelle à ce mouvement réel — n'utilisez pas un langage catastrophiste pour un mouvement modeste, et ne minimisez pas un grand mouvement."
            )
    else:
        price_movement = (
            "Calibrate the severity of the events described to match the actual price movement shown in the market data."
            if lang == "en" else
            "Calibrez la sévérité des événements décrits pour correspondre au mouvement de prix réel indiqué dans les données de marché."
        )

    # M6 — Curve narrative arc
    if lang == "en":
        curve_narrative = {
            "crash":       "The narrative must describe a company that was performing well but is now in clear decline — the turn has happened or is imminent. Structure the story as a deterioration, not just a snapshot.",
            "rally":       "The narrative must describe a company recovering and gaining strong upward momentum — the stock is climbing. Structure the story as a recovery or surge.",
            "linear":      "The narrative should describe steady, consistent progress — no drama, just sustained momentum.",
            "exponential": "The narrative should describe accelerating momentum — things are moving faster and faster.",
            "logarithmic": "The narrative should describe a company whose rapid early growth is now visibly plateauing.",
            "volatile":    "The narrative should reflect uncertainty — rapid swings, conflicting signals, no clear direction.",
        }.get(curve_profile, "")
    else:
        curve_narrative = {
            "crash":       "Le récit doit décrire une entreprise qui allait bien mais qui est maintenant en net déclin — le retournement a eu lieu ou est imminent. Structurez l'histoire comme une détérioration, pas seulement un instantané.",
            "rally":       "Le récit doit décrire une entreprise en reprise et en plein élan haussier — l'action progresse fortement. Structurez l'histoire comme une reprise ou une hausse.",
            "linear":      "Le récit doit décrire une progression régulière et constante — sans drame, juste une dynamique soutenue.",
            "exponential": "Le récit doit décrire une accélération — les choses évoluent de plus en plus vite.",
            "logarithmic": "Le récit doit décrire une entreprise dont la forte croissance initiale est maintenant visiblement en train de plafonner.",
            "volatile":    "Le récit doit refléter l'incertitude — des variations rapides, des signaux contradictoires, pas de direction claire.",
        }.get(curve_profile, "")

    # M8 — Journalism style rule
    curr_fmt  = f"{currency}{current_price:.2f}" if current_price is not None else ("the current price" if lang == "en" else "le prix actuel")
    start_fmt = f"{currency}{start_price:.2f}"   if start_price  is not None else ("the simulation start price" if lang == "en" else "le prix de départ")

    if lang == "en":
        style_rule = (
            f"8. JOURNALISM STYLE — STRUCTURE AND TEXTURE\n"
            f"Write in the style of a financial wire service (Reuters, Bloomberg) — short declarative sentences, no generic filler, every sentence earns its place.\n\n"
            f"- OPENING SENTENCE: State {company}'s current stock price ({curr_fmt}) and compare it directly to the price at simulation start ({start_fmt}). "
            f"Use these exact figures — do not round or alter them. "
            f"e.g. \"shares fell to {curr_fmt} — down from {start_fmt} in [month]\" or \"rose to {curr_fmt} from {start_fmt} at the start of the period\".\n"
            f"- ANALYST QUOTE: Include at least one short, anonymous analyst or investor quote that directly supports the article's sentiment, "
            f"e.g. \"said one [sector] analyst at a [city]-based fund.\" The quote must feel specific, not generic.\n"
            f"- CATALYST: Reference a specific, plausible sector event or catalyst (a scheduled meeting, a data release, an earnings report, a regulatory decision) "
            f"with a concrete date within the simulation window. This grounds the article in a real moment.\n"
            f"- CLOSING LINE: End with a brief note on the company's public response or non-response, "
            f"e.g. \"{company} has not commented publicly on the revised forecasts.\" or \"{company} confirmed the figures in a statement.\""
        )
    else:
        style_rule = (
            f"8. STYLE JOURNALISTIQUE — STRUCTURE ET TEXTURE\n"
            f"Rédigez dans le style d'une agence de presse financière (Reuters, Bloomberg) — des phrases courtes et directes, sans remplissage générique, chaque phrase doit être utile.\n\n"
            f"- PHRASE D'OUVERTURE : Mentionnez le prix actuel de l'action de {company} ({curr_fmt}) et comparez-le directement au prix de départ de la simulation ({start_fmt}). "
            f"Utilisez ces chiffres exacts — ne les arrondissez pas et ne les modifiez pas. "
            f"par exemple \"les actions ont chuté à {curr_fmt} — en recul par rapport à {start_fmt} en [mois]\" ou \"ont progressé à {curr_fmt} depuis {start_fmt} en début de période\".\n"
            f"- CITATION D'ANALYSTE : Incluez au moins une courte citation anonyme d'un analyste ou d'un investisseur qui soutient directement le sentiment de l'article, "
            f"par exemple \"a déclaré un analyste [secteur] dans un fonds basé à [ville].\" La citation doit sembler précise, pas générique.\n"
            f"- CATALYSEUR : Mentionnez un événement ou catalyseur sectoriel spécifique et plausible (une réunion prévue, une publication de données, des résultats, une décision réglementaire) "
            f"avec une date précise dans la fenêtre de simulation. Cela ancre l'article dans un moment réel.\n"
            f"- PHRASE DE CLÔTURE : Terminez par une brève note sur la réponse publique de l'entreprise ou son absence, "
            f"par exemple \"{company} n'a pas commenté publiquement les prévisions révisées.\" ou \"{company} a confirmé les chiffres dans un communiqué.\""
        )

    if lang == "en":
        p = """SIMULATION CONTEXT:{description_line}{market_context}{temporal_context}

Reference article:
{data}

TASK — Rewrite the reference article as a financial news piece. Follow every rule below exactly.

1. COMPANY & SECTOR
Every paragraph must be directly about {company} operating in the {sector} sector. Do not drift to unrelated industries or actors. Translate the sector name into the article's language if needed. Do not name or quote any real executive or person from another company — only reference {company}.

2. SIMULATION WINDOW
All events, results, and market conditions referenced must fall within the simulation date window. Do not reference any crisis, announcement, or condition from outside this window. Everything must be plausible on {article_date}.

3. DATE AND PRICE COHERENCE
The stock is at {currency}{current_price} on {article_date} — use this exact figure, do not round or alter it. Never use future tense for any event dated before {article_date} — use past tense. Cite only FY{article_year} or FY{article_prev_year} financial results — do not present FY{article_old_year} or older data as current. Do not use {currency}{price_low}–{currency}{price_high} as analyst price targets.

4. UNAMBIGUOUS SENTIMENT
{sentiment_instruction}

5. PROPORTIONATE LANGUAGE
{price_movement}

6. CHART NARRATIVE — MATCH THE CURVE SHAPE
{curve_narrative} The overall narrative arc must match the {curve_description} profile so that a reader who looks at the chart feels the article and the chart are telling the same story.

7. TEMPORAL FRAMING
The temporal framing established in the simulation context above must be reflected throughout the article. Use the tense and framing consistent with the article's position relative to the price event.

{style_rule}

Use only one currency symbol: {currency}. Use only standard, real-world financial and industry units — do not invent units. Reply ONLY with the rewritten article text — no preamble, no notes."""
    else:
        p = """CONTEXTE DE SIMULATION :{description_line}{market_context}{temporal_context}

Article de référence :
{data}

TÂCHE — Réécrivez l'article de référence comme un article de presse financière. Suivez chaque règle ci-dessous exactement.

1. ENTREPRISE & SECTEUR
Chaque paragraphe doit parler directement de {company} dans le secteur {sector}. Ne dérivez pas vers des industries ou des acteurs sans rapport. Traduisez le nom du secteur en français si nécessaire. Ne citez aucun vrai dirigeant ou personnalité d'une autre entreprise — ne mentionnez que {company}.

2. FENÊTRE DE SIMULATION
Tous les événements, résultats et conditions de marché mentionnés doivent s'inscrire dans la fenêtre de dates de la simulation. Ne référencez aucune crise, annonce ou condition en dehors de cette fenêtre. Tout doit être plausible à la date du {article_date}.

3. COHÉRENCE DE DATE ET DE PRIX
L'action est à {currency}{current_price} le {article_date} — utilisez ce chiffre exact, ne l'arrondissez pas et ne le modifiez pas. N'utilisez jamais le futur pour des événements datés avant le {article_date} — utilisez le passé. Citez uniquement les résultats de l'exercice {article_year} ou {article_prev_year} — ne présentez pas les données de {article_old_year} ou antérieures comme actuelles. N'utilisez pas {currency}{price_low}–{currency}{price_high} comme objectifs de cours d'analyste.

4. SENTIMENT SANS AMBIGUÏTÉ
{sentiment_instruction}

5. LANGAGE PROPORTIONNÉ
{price_movement}

6. ARC NARRATIF — CORRESPONDRE À LA FORME DE LA COURBE
{curve_narrative} L'arc narratif global doit correspondre au profil {curve_description} de sorte qu'un lecteur qui regarde ensuite le graphique ressente que l'article et le graphique racontent la même histoire.

7. CADRAGE TEMPOREL
Le cadrage temporel établi dans le contexte de simulation ci-dessus doit se refléter tout au long de l'article. Utilisez les temps et le cadrage cohérents avec la position de l'article par rapport à l'événement de prix.

{style_rule}

Utilisez un seul symbole de devise : {currency}. Utilisez uniquement des unités financières et sectorielles standard — n'inventez pas d'unités. Répondez UNIQUEMENT avec le texte de l'article réécrit — sans préambule, sans notes."""

    p = p.format(
        data=content,
        company=company,
        sector=sector,
        description_line=description_line,
        market_context=market_context,
        temporal_context=temporal_context,
        curve_description=curve_description,
        sentiment_instruction=sentiment_instruction,
        price_movement=price_movement,
        curve_narrative=curve_narrative,
        style_rule=style_rule,
        article_date=article_date or "",
        article_year=article_year,
        article_prev_year=article_prev_year,
        article_old_year=article_old_year,
        currency=currency,
        current_price=f"{current_price:.2f}" if current_price is not None else "",
        price_low=f"{price_low:.2f}" if price_low is not None else "",
        price_high=f"{price_high:.2f}" if price_high is not None else "",
    )

    response = _chat_with_retry(client, model, [{"role": "user", "content": p}])
    return response.choices[0].message.content


def transform_news_title(content, company_name, curve_profile, lang, client, model, sentiment):
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
            "rally":       "strong rally",
        }
        sentiment_instruction = (
            "The headline MUST sound clearly and unmistakably NEGATIVE — use words like 'drops', 'falls', 'crisis', 'loss', 'decline', 'slump', 'fears', 'warning', 'cut', 'crash', or similar. A reader must instantly know it is bad news without reading the article."
            if sentiment == "negative" else
            "The headline MUST sound clearly and unmistakably POSITIVE — use words like 'rises', 'surges', 'record', 'growth', 'gain', 'boost', 'strong', 'soars', 'leads', or similar. A reader must instantly know it is good news without reading the article."
        )
    else:
        curve_descriptions_short = {
            "linear":      "croissance stable",
            "exponential": "forte croissance",
            "logarithmic": "maturité du marché",
            "volatile":    "forte volatilité",
            "crash":       "crise et déclin",
            "rally":       "fort rallye",
        }
        sentiment_instruction = (
            "Le titre DOIT sonner clairement et sans ambiguïté NÉGATIF — utilisez des mots comme 'chute', 'baisse', 'crise', 'perte', 'déclin', 'avertissement', 'effondrement' ou similaires. Le lecteur doit immédiatement savoir que c'est une mauvaise nouvelle sans lire l'article."
            if sentiment == "negative" else
            "Le titre DOIT sonner clairement et sans ambiguïté POSITIF — utilisez des mots comme 'hausse', 'bond', 'record', 'croissance', 'gain', 'solide', 's'envole' ou similaires. Le lecteur doit immédiatement savoir que c'est une bonne nouvelle sans lire l'article."
        )

    curve_description_short = curve_descriptions_short.get(curve_profile, list(curve_descriptions_short.values())[0])

    if lang == "en":
        p = """Context:
You receive a financial news article about the company {company}. Its market profile is: {curve_description_short}.

Article:
{data}

Task:
Write a short, punchy headline for this article. The headline must mention {company}. {sentiment_instruction} The headline must be an honest summary of the article body — do not exaggerate beyond what the body actually describes. Reply ONLY with the headline, no preamble or trailing punctuation.""".format(
            data=content,
            company=company_name,
            curve_description_short=curve_description_short,
            sentiment_instruction=sentiment_instruction,
        )
    else:
        p = """Contexte :
Vous recevez un article de presse financière concernant l'entreprise {company}. Son profil de marché est : {curve_description_short}.

Article :
{data}

Tâche :
Rédigez un titre court et percutant pour cet article. Le titre doit mentionner {company}. {sentiment_instruction} Le titre doit être un résumé honnête du contenu de l'article — ne pas exagérer au-delà de ce que l'article décrit réellement. Répondez UNIQUEMENT avec le titre, sans préambule ni ponctuation finale.""".format(
            data=content,
            company=company_name,
            curve_description_short=curve_description_short,
            sentiment_instruction=sentiment_instruction,
        )

    response = _chat_with_retry(client, model, [{"role": "user", "content": p}])
    return response.choices[0].message.content
