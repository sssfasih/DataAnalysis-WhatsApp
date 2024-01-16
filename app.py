import streamlit as st
import helpers

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
        num_messages, words,num_media = helpers.fetch_stats(selected_user, df)
        st.title("Top Statistics")

        st.dataframe(df)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(len(words))

