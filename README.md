# Quick Run

> **Notice:** Both authentication flows require you to manually provide the Authorization Code after obtaining it. There is no way to automatically capture the code in this flow; you must copy it from the Epic Games response and input it into your application.

> **Tip:** The issuing client is usually the Epic Games Launcher or the Fortnite Game. Both are valid sources for the code and are referenced in [MixV2/EpicResearch](https://github.com/MixV2/EpicResearch).

# EpicTokenGenerator

**EpicTokenGenerator** is a Python client for authenticating with Epic Online Services (EOS) on behalf of a service or game. It provides a minimal, focused implementation for obtaining OAuth2 tokens and JWTs required for EOS authentication flows. This project does **not** aim to support other Epic Games features such as account management, game entitlements, or general Epic Games Store APIs.



## Quick Run

> **Notice:** Both authentication flows require you to manually provide the Authorization Code after obtaining it. There is no way to automatically capture the code in this flow; you must copy it from the Epic Games response and input it into your application.

This library supports two main authentication flows, each with a corresponding method for obtaining an Authorization Code and a JWT token. Only one flow and one auth method are necessary for your use case.

### 1. Interactive Web Sign-In (for ID information only)

Use when you have a web application and can host a redirect URI. This flow is **not suitable for games/services** that cannot host a redirect URL.

```python
from eos_auth_client import EpicAuthClient

# Step 1: Generate the interactive sign-in URL
url = EpicAuthClient.make_auth_url(client_id, redirect_uri)
# Direct the user to this URL. After sign-in, Epic will redirect to your URI with an Authorization Code.

# Step 2: Exchange the code for a JWT token
jwt_token = EpicAuthClient.auth(code, client_id, client_secret, deployment_id)
```

### 2. Non-Interactive (for Games/Services without redirect URI)

Use when you are a game or service and **cannot host a redirect URI**. This is the main scenario targeted by this repo.

```python
from eos_auth_client import EpicAuthClient

# Step 1: Generate the direct code retrieval URL
url = EpicAuthClient.make_redirect_url(client_id)
# Use this URL to get a code if the user is already signed in (no redirect required).

# Step 2: Authenticate using exchange mode
jwt_token = EpicAuthClient.auth_with_exchange(
	code,  # code from make_redirect_url
	issuing_client_id, issuing_client_secret,
	requesting_client_id, requesting_client_secret,
	requesting_deployment_id
)
```

**Note:** Both `make_auth_url` and `make_redirect_url` ultimately provide an Authorization Code, but only the non-interactive flow works for games/services without a redirect URI. For authentication, use `auth_with_exchange` in these cases.

## Usage

The main class is `EpicAuthClient`, which provides the following methods:

- `make_auth_url(client_id, redirect_uri, ...)`: Generate a sign-in URL for Epic Games (interactive).
- `make_redirect_url(client_id, ...)`: Generate a direct code retrieval URL (non-interactive).
- `get_access_token(code, client_id, client_secret, ...)`: Exchange a code for an access token.
- `get_exchange_token_from_access(access_token)`: Exchange an access token for a code.
- `get_jwt_token(code, client_id, client_secret, deployment_id, ...)`: Exchange a code for a JWT token.
- `auth(...)`: Main entry point for authenticating a user and retrieving a JWT token (interactive flow).
- `auth_with_exchange(...)`: Authenticate a user for a service/game without a web sign-in flow (non-interactive/exchange flow).

See the docstrings in `eos_auth_client.py` for details on parameters and usage.

## Features

- Generate Epic Games OAuth2 authentication URLs for web sign-in and direct code retrieval.
- Exchange access tokens for codes and JWT tokens.
- Support for both standard OAuth2 flows and token exchange between services/games.
- Handles error responses and provides descriptive exceptions.

## Limitations

This library is **only** intended for authenticating with EOS on behalf of a service or game. There are **no plans** to support:

- Epic Games Store features
- Account management
- Game entitlements
- Friends, achievements, or other Epic platform APIs

If you need broader Epic Games API support, see [MixV2/EpicResearch](https://github.com/MixV2/EpicResearch) and related projects.

## Credits

This project is based on [MixV2/EpicResearch](https://github.com/MixV2/EpicResearch).
Please see the original repository for more information and research on Epic Games authentication.