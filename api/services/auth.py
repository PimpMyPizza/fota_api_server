import secrets
import bcrypt
from fastapi.security import OAuth2AuthorizationCodeBearer
from api.core.config import config
import requests
import jwt
from jose import JWTError, ExpiredSignatureError
from fastapi import Depends, HTTPException, status
import logging

from api.models.user import Role, AuthUser

logger = logging.getLogger(__name__)
public_key = None
alg = None


# OAuth2 Password Bearer for FastAPI (authorization code flow)
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{config.keycloak_server_url}/protocol/openid-connect/auth",
    tokenUrl=f"{config.keycloak_server_url}/protocol/openid-connect/token",
    scopes={
        "openid": "OpenID Connect scope required for authentication",
        "profile": "",
    },
)


def extract_roles_from_payload(payload: dict) -> list[Role]:
    roles = payload.get("groups", [])
    filtered_roles = [Role.default]
    if "admin" in roles:
        filtered_roles.append(Role.admin)
    if "support" in roles:
        filtered_roles.append(Role.support)
    return filtered_roles


def verify_token_with_keycloak(token: str = Depends(oauth2_scheme)) -> AuthUser:
    """Verify the JWT token using Keycloak introspection endpoint."""
    if config.is_test:
        # Special case for when the server is running only for pytests.
        return AuthUser(
            username="test_user",
            first_name="Test",
            last_name="User",
            email="test@user.com",
            locale="en",
            roles=[Role.default],
        )
    try:
        logger.debug(f"verify_token_with_keycloak.")
        response = requests.post(
            url=f"{config.keycloak_server_url}/protocol/openid-connect/token/introspect",
            data={
                "token": token,
                "client_id": config.keycloak_client_id,
                "client_secret": config.keycloak_client_secret
            },
            verify=config.is_production,
        )
        logger.debug(f"Response from KC: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            if not token_data.get("active"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token is not active"
                )
            return AuthUser(
                username=token_data.get("preferred_username", ""),
                first_name=token_data.get("given_name", ""),
                last_name=token_data.get("family_name", ""),
                email=token_data.get("email", ""),
                locale=token_data.get("locale", "en"),
                roles=extract_roles_from_payload(token_data),
            )
        else:
            logger.error(f"Token verification failed. Got code: {response.status_code}, message {response.content}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token verification failed"
            )
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Keycloak validation error: {str(e)}"
        )


def get_keycloak_public_key() -> str:
    """Fetch the public key from Keycloak JWKS endpoint."""
    logger.info(f"get_keycloak_public_key")
    # TODO: Something is wrong here. I think the public key is not fetched correctly, or the wrong one is taken
    response = requests.get(
        f"{config.keycloak_server_url}/protocol/openid-connect/certs",
        verify=config.is_production,
    )
    logger.info(f"Response: {response.status_code}")
    if response.status_code == 200:
        global public_key
        global alg
        jwks = response.json()
        # Assume the first key in JWKS is the one we need (handle key rotation appropriately in production)
        public_key = jwks["keys"][0]["x5c"][0]
        alg = jwks["keys"][0]["alg"]
        return f"-----BEGIN PUBLIC KEY-----\n{public_key}\n-----END PUBLIC KEY-----"
    else:
        raise Exception("Could not fetch public key from Keycloak")


def verify_token_locally(token: str = Depends(oauth2_scheme)) -> AuthUser:
    # Workaround because Depends(oauth2_scheme) bugs with websocket endpoint
    return token_to_user(token)


def token_to_user(token: str) -> AuthUser:
    """Decode and validate the JWT locally."""
    try:
        global public_key
        if not public_key:
            public_key = get_keycloak_public_key()
        logger.info(f"verify_token_locally with alg {alg}: {token}")
        payload = jwt.decode(
            token,
            options={"verify_signature": config.is_production}
            #public_key, # TODO: add verification here
            #algorithms=alg,
            #audience="realm-management broker account",
            #issuer=config.keycloak_server_url,
        )
        return AuthUser(
            username=payload.get("preferred_username", ""),
            first_name=payload.get("given_name", ""),
            last_name=payload.get("family_name", ""),
            email=payload.get("email", ""),
            locale=payload.get("locale", "en"),
            roles=extract_roles_from_payload(payload),
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token is invalid: {str(e)}"
        )


def hash_token(token: str) -> str:
    return bcrypt.hashpw(token.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def generate_token() -> str:
    return secrets.token_urlsafe(32)
