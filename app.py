import pandas as pd
import streamlit as st
import helpers
from matplotlib import pyplot as plt
import seaborn as sns

st.sidebar.title("Whatsapp Data Analysis")

uploaded_file = st.sidebar.file_uploader("Upload Chat File")
if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode('utf-8')

    df = helpers.preprocessor(data)
    # fetch unique users
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0,"Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt",user_list)

    if st.sidebar.button("Show analysis"):
        num_messages, words,num_media,urls = helpers.fetch_stats(selected_user, df)
        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(len(words))
        with col3:
            st.header("Media Messages")
            st.title(num_media)
        with col4:
            st.header("URLs Sent")
            st.title(len(urls))

        st.title("Top Statistics")
        #  Monthly Timeline
        st.title("Monthly Timeline")
        tl = helpers.monthly_timeline(selected_user,df)
        fig, axis = plt.subplots()
        axis.plot(tl['time'],tl['message'])
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        #  Daily Timeline
        st.title("Daily Timeline")
        tl = helpers.daily_timeline(selected_user,df)
        fig, axis = plt.subplots()
        axis.plot(tl['only_date'],tl['message'])
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # activity map
        st.title('Activity Map')
        col1,col2 = st.columns(2)

        with col1:
            st.header("Most Active day")
            busy_day = helpers.weekly_activity(selected_user,df)
            fig,ax = plt.subplots()
            ax.bar(busy_day.index,busy_day.values,color='purple')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.header("Most Active month")
            busy_month = helpers.monthly_activity(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values,color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        st.title("Weekly Activity Map")
        fig, axis = plt.subplots()
        heatmap = sns.heatmap(helpers.activity_heatmap(selected_user, df))
        axis = heatmap
        st.pyplot(fig)

        if selected_user == "Overall":
            col1, col2, = st.columns(2)
            most_active,users_activity = helpers.get_activity(df)
            fig, axis = plt.subplots()
            with col1:
                st.header("Active Users")
                axis.bar(most_active.index, most_active.values)
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            with col2:
                st.header("Users Activity")
                st.dataframe(users_activity)

        df_wc = helpers.create_wordcloud(selected_user,df)
        fig, axis = plt.subplots()
        axis.imshow(df_wc)
        st.pyplot(fig)

        # most common list
        common_words = helpers.most_common_words(selected_user, df)
        common_words = pd.DataFrame(common_words)
        fig, axis = plt.subplots()
        axis.barh(common_words[0],common_words[1])
        st.title("Most Common Words")
        st.pyplot(fig)

        # emoji

        emoji_df = pd.DataFrame(helpers.emoji_counter(selected_user,df))

        st.title("Emoji Analysis")
        col1,col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)
        with col2:
            fig,ax = plt.subplots()
            ax.pie(emoji_df[1].head(),labels=emoji_df[0].head(),autopct="%0.2f")
            st.pyplot(fig)



