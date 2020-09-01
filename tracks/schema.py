from __future__ import annotations
from django.db.models.manager import BaseManager
from graphql.execution.base import ExecutionResult, ResolveInfo
from graphene_django import DjangoObjectType
import graphene
from tracks.models import Track


class TrackType(DjangoObjectType):
    class Meta:
        model: type = Track
        description: str = (
            'The documentation for the TrackType in GraphQL goes here'
        )


class Query(graphene.ObjectType):
    tracks: graphene.List = graphene.List(TrackType)

    def resolve_tracks(self, info: ResolveInfo) -> BaseManager[Track]:
        return Track.objects.all()


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
        track: Track
        track, _ = Track.objects.get_or_create(
            title=title, description=description, url=url
        )
        return CreateTrack(track=track)


class Mutation(graphene.ObjectType):
    create_track: graphene.Field = CreateTrack.Field()
