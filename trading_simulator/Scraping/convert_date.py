from datetime import datetime

# this function transforms a date from the format "dd/mm/yyyy" to "yyyymmdd" for a comparison
def compare_date(date):
    date_str = date.split("/")
    date_int = date_str[2] + date_str[1] + date_str[0]
    return int(date_int)


# this function reformats the dates that are not in the format "dd/mm/yyyy"
def convert_date(date_str):
    # remove spaces, newlines and the "Par ....." part of the date
    date_str = date_str.replace("\n", "")
    date_str = date_str.replace("  ", "")
    date_str = date_str.split("Par ")[0]
    date_str = date_str.split(" ")
    # if the date is in format "Aujourd'hui à hh:mm", we reformat it to the format "dd/mm/yyyy hh:mm"
    if date_str[0] == "Aujourd'hui":
        date_reformatted = datetime.now().strftime("%d/%m/%Y " + date_str[2])
    # if the date is in format "Hier à hh:mm", we reformat it to the format "dd/mm/yyyy hh:mm"
    elif date_str[0] == "Hier":
        date_reformatted = str(int(datetime.now("%d") - 1)) + datetime.now().strftime("/%m/%Y " + date_str[2])
        print(date_reformatted)
    # if the date is in format "Le dd mois yyyy à hh:mm", we reformat it to the format "dd/mm/yyyy hh:mm"
    else:
        month = date_str[2]
        # we need to translate the month from french to english
        month_fr = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre",
                    "novembre", "décembre"]
        month_en = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                    "November", "December"]
        try:
            # we find the index of the month in the french list and replace it with the english equivalent
            index = month_fr.index(month.lower())
            date_str = " ".join(date_str).replace(month, month_en[index])
            # we reformat the date
            date_obj = datetime.strptime(date_str, "Le %d %B %Y à %H:%M")
            date_reformatted = date_obj.strftime("%d/%m/%Y %H:%M")
        except ValueError:
                print("Mois invalide")
                return date_str
    return date_reformatted