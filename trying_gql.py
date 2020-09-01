from typing import Any, ClassVar, Dict, Optional
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from graphql.language.ast import Document


class GQLClient:
    URL: ClassVar[str] = 'http://localhost:8000/graphql/'

    @classmethod
    def _get_transport(
        cls, headers: Optional[Dict[str, str]] = None
    ) -> RequestsHTTPTransport:
        return RequestsHTTPTransport(cls.URL, headers=headers)

    @classmethod
    def _get_client(cls, headers: Optional[Dict[str, str]] = None) -> Client:
        return Client(
            transport=cls._get_transport(headers),
            fetch_schema_from_transport=True,
        )

    @classmethod
    def get_jwt(cls, username: str, password: str) -> str:
        query: Document = gql(
            '''
            mutation($username: String!, $password: String!) {
                tokenAuth(username: $username, password: $password) {
                    token
                }
            }
            '''
        )
        resp: Dict[str, Any] = cls._get_client().execute(
            query,
            variable_values={'username': username, 'password': password},
        )
        return resp['tokenAuth']['token']

    @classmethod
    def get_me(cls, jwt: str) -> Dict[str, Any]:
        query: DocumentNode = gql(
            '''
            query {
                me {
                    id
                    username
                    dateJoined
                }
            }
            '''
        )
        resp: Dict[str, Any] = cls._get_client(cls.auth(jwt)).execute(query)
        return resp

    @classmethod
    def auth(cls, jwt: str) -> Dict[str, str]:
        return {'Authorization': f'JWT {jwt}'}


def main() -> None:
    '''Main function'''
    jwt: str = GQLClient.get_jwt('sdq', '123456')
    print(GQLClient.get_me(jwt))


if __name__ == '__main__':
    main()
