import streamlit as st
from dotenv import load_dotenv
from query import MilonQuery

load_dotenv()

st.set_page_config(page_title="מילון הראיה", page_icon="📖", layout="wide")

# Proper RTL setup using HTML lang and dir attributes
st.markdown("""
<script>
document.documentElement.lang = 'he';
document.documentElement.dir = 'rtl';
</script>
""", unsafe_allow_html=True)


def main():
    st.title("📖 מילון הראיה")

    if "milon" not in st.session_state:
        st.session_state.milon = MilonQuery()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("מה תרצה לדעת?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("חושב..."):
                response = st.session_state.milon.query(prompt)
                st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

    if st.button("נקה שיחה"):
        st.session_state.messages = []
        st.session_state.milon = MilonQuery()  # Reset conversation state
        st.rerun()


if __name__ == "__main__":
    main()
