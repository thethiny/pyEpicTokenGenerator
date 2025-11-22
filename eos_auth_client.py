from typing import List
import requests


class EpicAuthClient:

    GRANT_MAP = {
        "exchange_code": "exchange_code",
        "authorization_code": "code",
    }

    @classmethod
    def make_auth_url(cls, client_id: str, redirect_uri: str, response_type: str = "code", scope: List[str] = ["basic_profile"]) -> str:
        """
            Constructs the URL that leads the user to Sign In with Epic Games.
            Used for applications that have a Web Sign in flow that don't require token exchange.
        """
        base_url = "https://www.epicgames.com/id/authorize"
        scope_param = "%20".join(scope)
        auth_url = (
            f"{base_url}?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"response_type={response_type}&"
            f"scope={scope_param}"
        )
        return auth_url

    @classmethod
    def make_redirect_url(cls, client_id: str, response_type: str = "code"):
        """
            Constructs the URL that leads the user to a json response with the code if the user is already signed in.
            Used for applications that cannot host a redirect URI to exchange the code for a token later on.
        """
        base_url = "https://www.epicgames.com/id/api/redirect"
        redirect_url = f"{base_url}?clientId={client_id}&responseType={response_type}"

        return redirect_url

    @classmethod
    def get_exchange_token_from_access(cls, access_token: str):
        url = "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/exchange"

        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        response = requests.get(url, headers=headers)

        data = response.json()
        error = data.get("error")
        if error:
            error_description = data.get("error_description", "No description provided")
            raise Exception(f"Error exchanging token: {error} - {error_description}")

        return data.get("code")

    @classmethod
    def get_access_token(cls, code: str, client_id: str, client_secret: str, grant_type: str = "authorization_code") -> str:
        url = "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        authorization = (client_id, client_secret)
        data = {
            "grant_type": grant_type,
            cls.GRANT_MAP[grant_type]: code
        }

        response = requests.post(url, headers=headers, data=data, auth=authorization)
        access_token = cls.get_token_from_response(response)
        
        return access_token

    @classmethod
    def get_jwt_token(cls, code: str, client_id: str, client_secret: str, deployment_id: str, grant_type: str = "authorization_code", scope: List[str] = ["basic_profile"]) -> str:
        url = "https://api.epicgames.dev/epic/oauth/v1/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        authorization = (client_id, client_secret)
        data = {
            "grant_type": grant_type,
            cls.GRANT_MAP[grant_type]: code,
            "deployment_id": deployment_id,
            "scope": " ".join(scope)
        }

        response = requests.post(url, headers=headers, data=data, auth=authorization)
        access_token = cls.get_token_from_response(response)
        
        return access_token

    @classmethod
    def get_token_from_response(cls, response):
        data = response.json()
        
        error = data.get("error")
        if error:
            error_description = data.get("error_description", "No description provided")
            if error == "scope_consent_required":
                error_description += " If this is a game or a service then the user should launch it at least once."
            raise Exception(f"Error obtaining token: {error} - {error_description}")

        access_token = data.get("access_token")
        if not access_token:
            raise Exception("No access token found in the response")
        return access_token

    # The following 2 methods are the main entry points for authentication and require either of the 2 make_*_url methods to be used first to get the code.
    @classmethod
    def auth(cls, code: str, client_id: str, client_secret: str, deployment_id: str, scope: List[str] = ["basic_profile"]) -> str:
        """
            Authenticates a user using a token received from the Epic Games OAuth2 flow.
        """
        jwt_token = cls.get_jwt_token(code, client_id, client_secret, deployment_id, "authorization_code", scope)
        return jwt_token

    @classmethod
    def auth_with_exchange(cls, code: str, issuing_client_id: str, issuing_client_secret: str, requesting_client_id: str, requesting_client_secret: str, requesting_deployment_id: str, scope: List[str] = ["basic_profile"]) -> str:
        """
            Authenticates a user for a service/game that does not have a web sign-in flow and a redirect URI.
            Exchanges a token by a Web Sign-In flow for a different service.
        """
        access_token = cls.get_access_token(code, issuing_client_id, issuing_client_secret)
        exchange_code = cls.get_exchange_token_from_access(access_token)
        jwt_token = cls.get_jwt_token(exchange_code, requesting_client_id, requesting_client_secret, requesting_deployment_id, "exchange_code", scope)
        return jwt_token
