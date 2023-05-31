from datetime import datetime


def convert_date(date_str):
    date_str = date_str.replace("\n", "")
    date_str = date_str.replace("  ", "")
    date_str = date_str.split(" ")
    month = date_str[2]
    month_fr = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre",
                "novembre", "décembre"]
    month_en = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                "November", "December"]
    # if in date_str there is "aujourd'hui" replace it by the current date
    if date_str[0] == "Aujourd'hui":
        date_reformatted = datetime.now().strftime("%d/%m/%Y " + date_str[2])
        str = "hello world i'm a breakpoint"
    else:
        try:
            index = month_fr.index(month.lower())
            date_str = " ".join(date_str).replace(month, month_en[index])
            date_obj = datetime.strptime(date_str, "Le %d %B %Y à %H:%M")
            date_reformatted = date_obj.strftime("%d/%m/%Y %H:%M")
        except ValueError:
            if "Par" in date_str:
                date_obj = date_str.split("Par ")[0]
                date_obj = datetime.strptime(date_obj, "Le %d %B %Y à %H:%M")
                date_reformatted = date_obj.strftime("%d/%m/%Y %H:%M")
            else:
                print("Mois invalide")
                return date_str
    return date_reformatted