from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar, Dict, List
import json
import uuid
from graphql.execution.base import ExecutionResult, ResolveInfo
import graphene


class Team:
    members: ClassVar[List[UserType]] = []


@dataclass
class User:
    username: str
    created_at: datetime
    id: str


class UserType(graphene.ObjectType):
    id: graphene.String = graphene.String(default_value=str(uuid.uuid4()))
    username: graphene.String = graphene.String()
    created_at: graphene.DateTime = graphene.DateTime(
        default_value=datetime.now()
    )


class CreateUser(graphene.Mutation):
    user: graphene.Field = graphene.Field(UserType)

    class Arguments:
        username = graphene.String()

    def mutate(self, info: ResolveInfo, username: str) -> CreateUser:
        user: UserType = UserType(username=username)
        Team.members.append(user)
        return CreateUser(user=user)


class Mutation(graphene.ObjectType):
    create_user: graphene.Field = CreateUser.Field()


class Query(graphene.ObjectType):
    users: graphene.List = graphene.List(UserType)

    def resolve_users(self, info: ResolveInfo) -> List[UserType]:
        return [UserType(username=user.username) for user in Team.members]


def main() -> None:
    '''Main function'''
    schema: graphene.Schema = graphene.Schema(mutation=Mutation, query=Query)
    names: List[str] = ['Eric', 'François', 'Aline', 'Sébastien']
    query: str = '''
        mutation($username: String!) {
            createUser(username: $username) {
                user {
                    username
                    id
                    createdAt
                }
            }
        }
        '''
    for name in names:
        schema.execute(query, variables={'username': name})
    query = '''
    {
        users {
            username
            id
            createdAt
        }
    }
    '''
    users: List[User] = []
    if (resp := schema.execute(query)) is not None:
        for user in resp.data['users']:
            users.append(
                User(
                    username=user['username'],
                    id=user['id'],
                    created_at=user['createdAt'],
                )
            )
    print('\n'.join(str(user) for user in users))


if __name__ == '__main__':
    main()
