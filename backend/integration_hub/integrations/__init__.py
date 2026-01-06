from .google import GoogleWorkspaceClient
from .slack import SlackClient
from .zapier import ZapierClient


class IntegrationFactory:
    """Factory to create integration clients"""

    CLIENTS = {
        'slack': SlackClient,
        'google-workspace': GoogleWorkspaceClient,
        'zapier': ZapierClient,
    }

    @classmethod
    def get_client(cls, provider_slug):
        """Get client instance for a provider"""
        client_class = cls.CLIENTS.get(provider_slug)
        if not client_class:
            raise ValueError(f"No client available for provider: {provider_slug}")
        return client_class()

    @classmethod
    def register_client(cls, provider_slug, client_class):
        """Register a new client"""
        cls.CLIENTS[provider_slug] = client_class
