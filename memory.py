class ConversationMemory:
    def __init__(self):
        self.history = []

    def add_interaction(self, user_input, retrieved_context, assistant_response):
        self.history.append({
            "user_input": user_input,
            "retrieved_context": retrieved_context,
            "assistant_response": assistant_response
        })

    def get_recent_history(self, n=5):
        return self.history[-n:]
