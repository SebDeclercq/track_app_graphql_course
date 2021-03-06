from __future__ import annotations
from typing import Optional
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.manager import BaseManager
from graphql import GraphQLError
from graphql.execution.base import ExecutionResult, ResolveInfo
from graphene_django import DjangoObjectType
import graphene
from tracks.models import Like, Track
from users.schema import UserType


class TrackType(DjangoObjectType):
    class Meta:
        model: type = Track
        description: str = (
            'The documentation for the TrackType in GraphQL goes here'
        )


class LikeType(DjangoObjectType):
    class Meta:
        model: type = Like
        description: str = (
            'The documentation for the LikeType in GraphQL goes here'
        )


class Query(graphene.ObjectType):
    tracks: graphene.List = graphene.List(TrackType, search=graphene.String())
    likes: graphene.List = graphene.List(LikeType)
    track: graphene.Field = graphene.Field(TrackType, track_id=graphene.Int())

    def resolve_tracks(
        self, info: ResolveInfo, search: Optional[str] = None
    ) -> BaseManager[Track]:
        if search is not None:
            return Track.objects.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        return Track.objects.all()

    def resolve_likes(self, info: ResolveInfo) -> BaseManager[Like]:
        return Like.objects.all()

    def resolve_track(self, info: ResolveInfo, track_id: int) -> Track:
        return Track.objects.get(pk=track_id)


class CreateTrack(graphene.Mutation):
    track: graphene.Field = graphene.Field(TrackType)

    class Arguments:
        title = graphene.String(description='the description for title')
        description = graphene.String(description='the description for desc')
        url = graphene.String(description='the description for title')

    class Meta:
        description: str = 'The doc for the mutation goes here'

    def mutate(
        self, info: ResolveInfo, title: str, description: str, url: str
    ) -> CreateTrack:
        if info.context is not None:
            user: User = info.context.user
        if user.is_anonymous:
            raise GraphQLError('Anonymous user not allowed to add tracks')
        track: Track
        track, _ = Track.objects.get_or_create(
            title=title, description=description, url=url, posted_by=user
        )
        return CreateTrack(track=track)


class UpdateTrack(graphene.Mutation):
    track: graphene.Field = graphene.Field(TrackType)

    class Arguments:
        track_id = graphene.Int(required=True)
        title = graphene.String(description='the description for title')
        description = graphene.String(description='the description for desc')
        url = graphene.String(description='the description for title')

    def mutate(
        self,
        info: ResolveInfo,
        track_id: int,
        title: str,
        description: str,
        url: str,
    ):
        if info.context is not None:
            user: User = info.context.user
        track: Track = Track.objects.get(pk=track_id)
        if track.posted_by != user:
            raise GraphQLError("Not permitted to update someone else's track")
        track.title = title
        track.description = description
        track.url = url
        track.save()
        return UpdateTrack(track=track)


class DeleteTrack(graphene.Mutation):
    track_id: graphene.Int = graphene.Int()

    class Arguments:
        track_id = graphene.Int(required=True)

    def mutate(self, info: ResolveInfo, track_id: int) -> DeleteTrack:
        if info.context is not None:
            user: User = info.context.user
        track: Track = Track.objects.get(pk=track_id)
        if track.posted_by != user:
            raise GraphQLError("Not permitted to delete someone else's track")
        track.delete()
        return DeleteTrack(track_id=track_id)


class CreateLike(graphene.Mutation):
    user: graphene.Field = graphene.Field(UserType)
    track: graphene.Field = graphene.Field(TrackType)

    class Arguments:
        track_id = graphene.Int(required=True)

    def mutate(self, info: ResolveInfo, track_id: int) -> CreateLike:
        if info.context is not None:
            user: User = info.context.user
        if user.is_anonymous:
            raise GraphQLError('Anonymous user not allowed to like tracks')
        track: Track = Track.objects.get(pk=track_id)
        Like.objects.create(user=user, track=track)
        return CreateLike(user=user, track=track)


class Mutation(graphene.ObjectType):
    create_track: graphene.Field = CreateTrack.Field()
    update_track: graphene.Field = UpdateTrack.Field()
    delete_track: graphene.Field = DeleteTrack.Field()
    create_like: graphene.Field = CreateLike.Field()