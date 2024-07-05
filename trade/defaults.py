class Defaults:
    """Default values used in the trade-legacy"""

    # Period of time used to update data on the dashboard
    # update_time = 60*1000 # in milliseconds
    update_time = 5*1000 # in milliseconds

    # Maximum number of requests the user can make on the dashboard
    max_requests = 10

    # Initial money the user has
    initial_money = 100000

    # Path to the data folder
    data_path = "../Data"

    # Stocks used in the interface
    # They are also used to download data with the download_market_data setup tool
    # The key is the ticker and the value is the name of the company
    # So the data provided in the Data folder must have the same name as the symbol
    companies = {
        "MC.PA" : "LVMH MOËT HENNESSY LOUIS VUITTON SE (MC)",
        "OR.PA" : "L'ORÉAL (OR)",
        "RMS.PA" : "HERMÈS INTERNATIONAL (RMS)",
        "TTE.PA" : "TOTALENERGIES SE (TTE)",
        "SAN.PA" : "SANOFI (SAN)",
        "AIR.PA" : "AIRBUS SE (AIR)",
        "SU.PA" : "SCHNEIDER ELECTRIC SE (SU)",
        "AI.PA" : "AIR LIQUIDE (AI)",
        "EL.PA" : "ESSILORLUXOTTICA (EL)",
        "BNP.PA" : "BNP PARIBAS (BNP)",
        "KER.PA" : "KERING (KER)",
        "DG.PA" : "VINCI (DG)",
        "CS.PA" : "AXA (CS)",
        "SAF.PA" : "SAFRAN (SAF)",
        "RI.PA" : "PERNOD RICARD (RI)",
        "DSY.PA" : "DASSAULT SYSTÈMES SE (DSY)",
        "STLAM.MI" : "STELLANTIS N.V. (STLAM)",
        "BN.PA" : "DANONE (BN)",
        "STMPA.PA" : "STMICROELECTRONICS N.V. (STMPA)",
        "ACA.PA": "CRÉDIT AGRICOLE S.A. (ACA)"
    }

    # Indexes used in the interface
    # Same use as the companies variable
    indexes = {
        "^GSPC" : "S&P 500",
        "^DJI" : "Dow Jones Industrial Average",
        "^FCHI" : "CAC 40",
        "^SPGSGC" : "S&P GSCI Gold Index",
    }

    activities = {
        "Financial Services": [ "BNP.PA", "CS.PA", "ACA.PA" ],
        "Healthcare": [ "SAN.PA" ],
        "Consumer Goods": [ "MC.PA", "OR.PA", "RMS.PA", "RI.PA", "EL.PA" ],
        "Industrials": [ "TTE.PA", "AIR.PA", "SU.PA", "AI.PA", "SAF.PA", "DSY.PA" ],
        "Technology": [ "STMPA.PA" ],
        "Automobile": [ "STLAM.MI" ],
        "Aerospace": [ "AIR.PA" ],
        "Construction": [ "DG.PA" ],
        "Food": [ "BN.PA" ],
        "Luxury": [ "KER.PA" ],
        "Indexes": [ "^GSPC", "^DJI", "^FCHI", "^SPGSGC" ]
    }

    # Variables used to disable the start button on the home page
    home_start_button_disabled = False


# Provide the default values in global scope
defaults = Defaults()