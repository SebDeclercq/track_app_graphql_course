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
        query: Document = gql(
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
    def create_track(
        cls, jwt: str, title: str, desc: str, url: str
    ) -> Dict[str, Any]:
        query: Document = gql(
            '''
            mutation($title: String!, $desc: String!, $url: String!) {
                createTrack(title: $title, description: $desc, url: $url) {
                    track {
                        id
                        title
                        description
                        postedBy {
                            username
                        }
                    }
                }
            }
            '''
        )
        return cls._get_client(cls.auth(jwt)).execute(
            query,
            variable_values={'title': title, 'desc': desc, 'url': url},
        )

    @classmethod
    def update_track(
        cls, jwt: str, track_id: int, title: str, desc: str, url: str
    ) -> Dict[str, Any]:
        query: Document = gql(
            '''
            mutation($trackId: Int!, $title: String!, $desc: String!, $url: String!) {
                updateTrack(trackId: $trackId, title: $title, description: $desc, url: $url) {
                    track {
                        id
                        title
                        description
                        postedBy {
                            username
                        }
                    }
                }
            }
            '''
        )
        return cls._get_client(cls.auth(jwt)).execute(
            query,
            variable_values={
                'trackId': track_id,
                'title': title,
                'desc': desc,
                'url': url,
            },
        )

    @classmethod
    def delete_track(cls, jwt: str, track_id: int) -> Dict[str, Any]:
        query: Document = gql(
            '''
            mutation($trackId: Int!) {
                deleteTrack(trackId: $trackId) {
                    trackId
                }
            }
            '''
        )
        return cls._get_client(cls.auth(jwt)).execute(
            query,
            variable_values={
                'trackId': track_id,
            },
        )

    @classmethod
    def add_like(cls, jwt: str, track_id: int) -> Dict[str, Any]:
        query: Document = gql(
            '''
            mutation($trackId: Int!) {
                createLike(trackId: $trackId) {
                    track {
                        id
                    }
                    user {
                        username
                    }
                }
            }
            '''
        )
        return cls._get_client(cls.auth(jwt)).execute(
            query, variable_values={'trackId': track_id}
        )

    @classmethod
    def auth(cls, jwt: str) -> Dict[str, str]:
        return {'Authorization': f'JWT {jwt}'}


def main() -> None:
    '''Main function'''
    jwt: str = GQLClient.get_jwt('sdq', '123456')
    title: str = 'yeah it is a really good song'
    desc: str = 'what more to say?'
    url: str = 'http://...'
    resp: Dict[str, Any] = GQLClient.create_track(jwt, title, desc, url)
    track: Dict[str, Any] = resp['createTrack']['track']
    assert track['title'] == title
    assert track['description'] == desc
    title = 'it was badly named :-O'
    desc = 'now I could say more but I dunno what to say'
    url = 'https://...'
    resp = GQLClient.update_track(jwt, track['id'], title, desc, url)
    track = resp['updateTrack']['track']
    assert track['title'] == title
    assert track['description'] == desc
    track_id = track['id']
    resp = GQLClient.add_like(jwt, track_id)
    track = resp['createLike']['track']
    user = resp['createLike']['user']
    assert track['id'] == track_id
    assert user['username'] == 'sdq'
    resp = GQLClient.delete_track(jwt, track['id'])
    track_id = resp['deleteTrack']['trackId']
    assert track_id == int(track['id'])


if __name__ == '__main__':
    main()
