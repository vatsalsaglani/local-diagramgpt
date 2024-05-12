import streamlit as st
from diagramgpt import diagramGPT

st.set_page_config(page_title="Nano DiagramGPT", page_icon="🏗")


def main():
    st.title("Nano DiagramGPT 🏗")
    user_description = st.text_input("What do you want to create?",
                                     key="user_description")
    if st.button("Generate"):
        if user_description and len(user_description) >= 4:
            st.write_stream(diagramGPT(user_description))
        else:
            st.error(
                "Please provide a valid description which should at least have 4 characters!"
            )


if __name__ == "__main__":
    main()
