from assistant import assistWith
from chat_survey import client

# Helper functions
def submit_message(assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
        # instructions="Respond with a question that will help the user understand deeper her personal values. Do not explain. Be concise and only respond with a question."
    )