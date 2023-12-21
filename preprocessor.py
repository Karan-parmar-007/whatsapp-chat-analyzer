import re
import pandas as pd

def preprocess(data):
    try:
        pattern = r'\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2} [ap]m - '
        pattern1 = r'(\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2} [ap]m)'

        messages = re.split(pattern, data)
        messages = [message.strip() for message in messages if message.strip()]
        dates_and_times = re.findall(pattern1, data)

        formatted_dates = []

        def convert_to_12_hour(time_24_hour):
            time_24_hour = time_24_hour.replace('\u202f', ' ')  
            return pd.to_datetime(time_24_hour, format='%I:%M %p').strftime('%I:%M %p')

        for date_time in dates_and_times:
            time_24_hour = date_time.split(', ')[1]
            time_12_hour = convert_to_12_hour(time_24_hour)
            formatted_date = f"{date_time.split(', ')[0]}, {time_12_hour}"
            formatted_dates.append(formatted_date)

        df = pd.DataFrame({'user_message': messages, 'message_date': formatted_dates})

        df.rename(columns={'message_date': 'date'}, inplace=True)

        users = []
        messages = []

        for message in df['user_message']:
            entry = re.split('([\w\W]+?): ', message)
            if entry[1:]:
                users.append(entry[1])
                messages.append(entry[2])
            else:
                users.append('group_notification')
                messages.append(entry[0])

        df['user'] = users
        df['message'] = messages
        df.drop(columns=['user_message'], inplace=True)

        df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y, %I:%M %p', errors='coerce')  
        df['date'].fillna(pd.to_datetime(df['date'], format='%d/%m/%y, %I:%M %p'), inplace=True)  

        df['year'] = df['date'].dt.year
        df['month_num'] = df['date'].dt.month
        df['only_date'] = df['date'].dt.date
        df['day_name'] = df['date'].dt.day_name()
        df['month'] = df['date'].dt.month_name()
        df['day'] = df['date'].dt.day
        df['hour'] = df['date'].dt.hour
        df['minute'] = df['date'].dt.minute

        period = []
        for hour in df[['day_name', 'hour']]['hour']:
            if hour == 23:
                period.append(str(hour) + '-' + str('00'))
            elif hour == 0:
                period.append(str('00') + '-' + str(hour + 1))
            else:
                period.append(str(hour) + '-' + str(hour + 1))

        df['period'] = period

        return df

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


