from __future__ import annotations
from typing import Sequence
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models.manager import BaseManager
from graphene_django import DjangoObjectType
from graphql.execution.base import ResolveInfo
import graphene


class UserType(DjangoObjectType):
    class Meta:
        model: type = get_user_model()
        # only_fields: Sequence[str] = ('id', 'email', 'username', 'dateJoined')


class Query(graphene.ObjectType):
    users: graphene.List = graphene.List(UserType)
    user: graphene.Field = graphene.Field(
        UserType, id=graphene.Int(), required=True
    )
    me: graphene.Field = graphene.Field(UserType)

    def resolve_users(self, info: ResolveInfo) -> BaseManager[User]:
        return get_user_model().objects.all()

    def resolve_user(self, info: ResolveInfo, id: int) -> User:
        return User.objects.get(pk=id)

    def resolve_me(self, info: ResolveInfo) -> User:
        if info.context is not None:
            user: User = info.context.user
        if user.is_anonymous:
            raise PermissionDenied('Anonymous user not allowed')
        return user


class CreateUser(graphene.Mutation):
    user: graphene.Field = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)

    class Meta:
        description: str = 'createUser mutation doc'

    def mutate(
        self, info: ResolveInfo, username: str, password: str, email: str
    ) -> CreateUser:
        user: User = get_user_model()(username=username, email=email)
        user.set_password(password)
        user.save()
        return CreateUser(user=user)


class Mutation(graphene.ObjectType):
    create_user: graphene.Field = CreateUser.Field()
