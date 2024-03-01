import streamlit as st
from streamlit_pills import pills
from openai import OpenAI
import time
from assistant import assistWith
# from helper import utils

## Functions

# Waiting in a loop
def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

def back_to_menu():
    del st.session_state.pills_index
    del st.session_state.suggestions_list
    del st.session_state.suggestions_icons
    del st.session_state.selection_state
    del st.session_state.messages
    del st.session_state.thread
    del st.session_state.selected

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# General information
st.header("Micro journal for mindfulness.")
st.markdown("Writing out your thoughts and emotions helps you understand them better. Respond to tiny prompts to find patterns that will help you reduce daily stress.")

# Initializing session state
if "suggestions_list" not in st.session_state:
    st.session_state.pills_index = None
    st.session_state.suggestions_list = ["Explore my values", "Today I'm grateful", "I could have reacted better"]
    st.session_state.suggestions_icons = ["🚀","😌","🙈"]
    st.session_state.selection_state = False

# Display activity to work on
if st.session_state.selection_state==False:
    predefined_prompt_selected = pills("What would you like to work on today?:", st.session_state.suggestions_list,
                                                st.session_state.suggestions_icons, 
                                                index=st.session_state.pills_index,
                                                )
else:
    predefined_prompt_selected = st.session_state.selected

# Get rid of the suggestion now that it was chosen
if predefined_prompt_selected and st.session_state.selection_state==False:
    index_to_eliminate = st.session_state.suggestions_list.index(predefined_prompt_selected)
    st.session_state.selected = st.session_state.suggestions_list[index_to_eliminate]
    st.session_state.suggestions_list.pop(index_to_eliminate)
    st.session_state.suggestions_icons.pop(index_to_eliminate)
    st.session_state.selection_state=True
    st.rerun()
    
else:

    values_extractor = assistWith.values_extractor

    if "thread" not in st.session_state:
        st.session_state.thread = client.beta.threads.create()
   
    # create the message history state
    if "messages" not in st.session_state:
        if "selected" not in st.session_state:
            st.session_state.messages = []
    
    if "selected" not in st.session_state:
        st.session_state.selected=None
    

    # Choose assistant based on selection
    if st.session_state.selected == "Explore my values":
        st.subheader("Chat with Luna")
        if st.session_state.messages == []:
            st.session_state.messages.append({"role":"assistant", "content": "Let's work on identifying your values."})         
        ai_assistant=assistWith.values
    elif st.session_state.selected == "Today I'm grateful":
        st.subheader("Chat with Geno")
        if st.session_state.messages == []:
            st.session_state.messages.append({"role":"assistant", "content": "Gratitude increases mental strength 🧠."})         
        ai_assistant=assistWith.gratefulness
    elif st.session_state.selected == "I could have reacted better":
        st.subheader("Chat with Simone")
        if st.session_state.messages == []:
            st.session_state.messages.append({"role":"assistant", "content": "Reflection requires courage. Don't underestimate its power."})
        ai_assistant=assistWith.reflection
    else:
        st.markdown("Choose something to discuss 👆")

    # render older messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # render the chat input
    prompt = st.chat_input("Enter your message...")
    if prompt:
        # Add prompt to message to render
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Add message to a thread
        user_message = client.beta.threads.messages.create(
            thread_id=st.session_state.thread.id,
            role="user",
            content=prompt
        )

        # render the user's new message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # render the assistant's response
        with st.chat_message("assistant"):

            # Get an assistant for the need case
            run = client.beta.threads.runs.create(
                thread_id=st.session_state.thread.id,
                assistant_id=ai_assistant.id, 
                )
            
            wait_on_run(run,st.session_state.thread)
            
            assistant_messages = client.beta.threads.messages.list(
                thread_id=st.session_state.thread.id
            )

            response=assistant_messages.data[0].content[0].text.value
            st.markdown(response)

            # add the response to the message history
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            if response=="Your entry has been saved to your journal.":
                st.button("Back to main options", on_click=back_to_menu)

            #     run_extractor = client.beta.threads.runs.create(
            #         thread_id=st.session_state.thread.id,
            #         assistant_id=values_extractor.id, 
            #     )

            #     wait_on_run(run_extractor,st.session_state.thread)

            #     extractor_messages = client.beta.threads.messages.list(
            #     thread_id=st.session_state.thread.id
            #     )
            #     extracted_values=extractor_messages.data[0].content[0].text.value
            #     st.write()

            
        
            