class ValidationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ProfileError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class DatabaseError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class APIError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ExternalServiceError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
