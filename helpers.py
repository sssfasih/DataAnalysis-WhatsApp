import re
import pandas as pd
from urlextract import URLExtract
from wordcloud import WordCloud
from collections import Counter
import emoji

def segregate_messages(df):
    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:  # username exists
            users.append(re.split(' - ', entry[1])[1])
            messages.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages.append(entry[0])
    return users,messages

def preprocessor(data):
    pattern = '\d{1,2}\/\d{1,2}\/\d{2},\s\d{1,2}:\d{2}\s(?:AM|PM)'
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)
    df = pd.DataFrame({'user_message': messages, 'date': dates})
    df['date'] = pd.to_datetime(df['date'], format='%m/%d/%y, %I:%M %p')

    df['user'] , df['message'] = segregate_messages(df)
    df.drop(columns=['user_message'], inplace=True)
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute
    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df

def fetch_stats(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # fetch the number of messages
    num_messages = df.shape[0]

    def words_collector(df):
        # fetch the total number of words
        words = []
        df = df[df['message'] != '<Media omitted>\n']
        df = df[df['user'] != 'group_notification']
        for message in df['message']:
            words.extend(message.split())
        return words
    words = words_collector(df)
    num_media = df[df['message'] == '<Media omitted>\n'].shape[0]

    links = []
    extractor = URLExtract()
    for i in df['message']:
        links.extend(extractor.find_urls(i))

    return num_messages, words,num_media,links

def get_activity(df):
    most_active = df['user'].value_counts().head()
    users_activity = round((( df['user'].value_counts()/ df['user'].shape[0] )* 100),2).reset_index().rename(columns={'index':'name','user':'%'})
    return most_active, users_activity

def create_wordcloud(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    df = df[df['message'] != '<Media omitted>\n']
    df = df[df['user'] != 'group_notification']

    file = open('stop_words_urdu_hindi_english.txt', 'r')
    file = file.read()
    def remove_stop_words(message):
        words = []
        for i in re.split(r'[:/ .,!"?>;(*~`]+', message.lower()):
            if i in ['http','https','www']:
                return ''
            if i not in file:
                words.append(i)
        return ' '.join(words)

    df['message'] = df['message'].apply(remove_stop_words)
    wc = WordCloud(width=500,height=500,min_font_size=10,background_color='white')
    df_wc = wc.generate(df['message'].str.cat(sep=' '))
    return df_wc

def most_common_words(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    df = df[df['message'] != '<Media omitted>\n']
    df = df[df['user'] != 'group_notification']

    file = open('stop_words_urdu_hindi_english.txt', 'r')
    file = file.read()
    words = []

    for i in df['message']:
        for j in i.lower().split():
            if j not in file:
                words.append(j)

    return Counter(words).most_common(20)

def emoji_counter(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if emoji.is_emoji(c)])

    return Counter(emojis).most_common(len(Counter(emojis)))

def monthly_timeline(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    tl = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(tl.shape[0]):
        time.append(tl['month'][i] + "-" + str(tl['year'][i]))

    tl['time'] = time

    return tl

def daily_timeline(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    tl = df.groupby('only_date').count()['message'].reset_index()

    return tl

def weekly_activity(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()


def monthly_activity(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap