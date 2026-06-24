from datetime import datetime
import os  # <-- Added to fetch environment secrets and paths
import pandas
import random
import smtplib

# STEP 4b FIX: Fetch secrets securely from GitHub Actions environment variables
MY_EMAIL = os.environ.get("MY_EMAIL")
MY_PASSWORD = os.environ.get("MY_PASSWORD")

today = datetime.now()
today_tuple = (today.month, today.day)

# PATH FIX: Determine absolute paths so GitHub runner doesn't get lost
current_dir = os.path.dirname(__file__)
csv_path = os.path.join(current_dir, "birthdays.csv")

# Read data and drop empty rows to avoid ValueError NaN crashes
data = pandas.read_csv(csv_path)
data.columns = data.columns.str.strip()
data = data.dropna(subset=["month", "day"])

birthdays_dict = {
    (int(data_row["month"]), int(data_row["day"])): data_row
    for (index, data_row) in data.iterrows()
}

if today_tuple in birthdays_dict:
    birthday_person = birthdays_dict[today_tuple]

    # PATH FIX: Point explicitly to the subfolder template
    file_path = os.path.join(current_dir, f"letter_templates/letter_{random.randint(1, 3)}.txt")

    with open(file_path) as letter_file:
        contents = letter_file.read()
        contents = contents.replace("[NAME]", birthday_person["name"])

    # PORT FIX: Added explicit port 587 for standard TLS connection stability
    with smtplib.SMTP("smtp.gmail.com", 587) as connection:
        connection.starttls()
        connection.login(MY_EMAIL, MY_PASSWORD)
        connection.sendmail(
            from_addr=MY_EMAIL,
            to_addrs=birthday_person["email"],
            msg=f"Subject:Happy Birthday!\n\n{contents}"
        )
    print(f"Success! Birthday email sent to {birthday_person['name']}.")
else:
    print(f"Executed successfully. No matching birthday for today: {today_tuple}.")
