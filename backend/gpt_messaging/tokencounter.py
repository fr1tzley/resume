import tiktoken


class TokenCounter:
    """Singleton class to track token usage across all API calls."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TokenCounter, cls).__new__(cls)
            cls._instance.input_tokens = 0
            cls._instance.output_tokens = 0
            cls._instance.encoder = tiktoken.encoding_for_model("gpt-4o-mini")
        return cls._instance
    
    def add_input_tokens(self, messages):
        """Count and add input tokens from messages."""
        tokens = 0
        for message in messages:
            # Add tokens for message content
            tokens += len(self.encoder.encode(message.get("content", "")))
            # Add tokens for role (system, user, assistant)
            tokens += 4  # Approximate token count for message metadata
        
        # Add tokens for message formatting and model overhead
        tokens += 3  # Add tokens for basic formatting overhead
        
        self.input_tokens += tokens
        return tokens
    
    def add_output_tokens(self, text):
        """Count and add output tokens from response text."""
        tokens = len(self.encoder.encode(text))
        self.output_tokens += tokens
        return tokens
    
    def get_counts(self):
        """Get the current token counts."""
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.input_tokens + self.output_tokens
        }
    
    def reset(self):
        """Reset the token counters."""
        self.input_tokens = 0
        self.output_tokens = 0