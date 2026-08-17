class APIException(Exception):
    """
    Base exception for the application
    """


class ValidationException(APIException):
    """
    Raised when user input is invalid
    """


class KnowledgeBaseException(APIException):
    """
    Raised when document retrieval fails
    """


class LLMException(APIException):
    """
    Raised when the language model fails
    """
