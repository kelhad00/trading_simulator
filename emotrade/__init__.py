# Constants for the trading simulator
UPDATE_TIME = 1*1000 # in milliseconds
MAX_REQUESTS = 10    # Maximum number of requests
MAX_INV_MONEY=100000 # Initial money
COMP = { # List of stocks to download
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
INDEX = {
	"^GSPC" : "S&P 500",
	"^DJI" : "Dow Jones Industrial Average",
	"^FCHI" : "CAC 40",
	"^SPGSGC" : "S&P GSCI Gold Index",
}

# When importing the package, import the app variable needed to run the app
from .app import app