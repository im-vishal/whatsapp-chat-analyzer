
from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji


extract = URLExtract()

def fetch_stats(selection, df):

    if selection != 'Overall':
        df = df[df['user'] == selection]
        
    # fetch the number of msg
    num_msg = df.shape[0]

    # fetch the number of words
    words = []
    for message in df['message']:
        words.extend(message.split())

    # fetch number of media messages
    num_media_msg = df[df['message'] == '<Media omitted>\n'].shape[0]
    
    # fetch number of urls
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))
    
    
    return num_msg, len(words), num_media_msg, len(links)


def most_busy_users(df):
    x = df['user'].value_counts().head()
    df = round(df['user'].value_counts()/df.shape[0]*100,2).reset_index().rename(columns={'index':'name',
                                                                                'user':'percent'})
    return x, df

def create_wordcloud(selection, df):
    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()
    f.close()

    if selection != 'Overall':
        df = df[df['user'] == selection]

    temp = df[df['user'] != 'group notification']
    temp = temp[temp['message'] != '<Media omitted>\n'].reset_index()

    def remove_stopwords(message):
        y = []
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return ' '.join(y)
    
    wc =WordCloud(width=500, height=500, min_font_size= 10,
                background_color='white')
    temp['message'] = temp['message'].apply(remove_stopwords)
    df_wc = wc.generate(temp['message'].str.cat(sep=' '))
    return df_wc


def  most_common_words(selection, df):

    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()
    f.close()

    if selection != 'Overall':
        df = df[df['user'] == selection]

    temp = df[df['user'] != 'group notification']
    temp = temp[temp['message'] != '<Media omitted>\n'].reset_index()
 

    words = []
    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20)).rename(columns={0:'words',1:'Count'})

    return most_common_df


def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.UNICODE_EMOJI['en']])
    
    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

    return emoji_df

def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year','month_num','month']).count()['message'].reset_index()
    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + '-' + str(timeline['year'][i]))
        
    timeline['time'] = time
    return timeline

def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['day_name'].value_counts()


def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['month'].value_counts()

def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period',
                    values='message',aggfunc='count').fillna(0)

    return user_heatmap