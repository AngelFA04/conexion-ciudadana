import graphene
from graphene import relay

from .data import create_ship, get_empire, get_faction, get_rebels, get_ship

class Metacreator(graphene.ObjectType):
    """
    A metacreator is a profile for enginering, management, and auditoring.
    Here will be stored the 
    """
    configurations = graphene.String()

class Profile:
    """
    Information public in a person or organization page
    """
    name = 


# TODO Change name
class Person(graphene.ObjectType):
    """A person in the Star Wars universe"""
    name = graphene.String(description="The name of the person.")
    
    school = School()
    communication_preferences = ComunicationPreferences()
    projects = graphene.List(Project)



# Example classes 
# ---------------------------

class Episode(graphene.Enum):
    NEWHOPE = 4
    EMPIRE = 5
    JEDI = 6


class Character(graphene.Interface):
    id = graphene.ID()
    name = graphene.String()
    friends = graphene.List(lambda: Character)
    appears_in = graphene.List(Episode)

    def resolve_friends(self, info):
        # The character friends is a list of strings
        return [get_character(f) for f in self.friends]


class Human(graphene.ObjectType):
    class Meta:
        interfaces = (Character,)

    home_planet = graphene.String()


class Droid(graphene.ObjectType):
    class Meta:
        interfaces = (Character,)

    primary_function = graphene.String()


class Query(graphene.ObjectType):
    hero = graphene.Field(Character, episode=Episode())
    human = graphene.Field(Human, id=graphene.String())
    droid = graphene.Field(Droid, id=graphene.String())

    def resolve_hero(root, info, episode=None):
        return get_hero(episode)

    def resolve_human(root, info, id):
        return get_human(id)

    def resolve_droid(root, info, id):
        return get_droid(id)


schema = graphene.Schema(query=Query)


# Examples
# ------------------------------------- 
class Ship(graphene.ObjectType):
    """A ship in the Star Wars saga"""

    class Meta:
        interfaces = (relay.Node,)

    name = graphene.String(description="The name of the ship.")

    @classmethod
    def get_node(cls, info, id):
        return get_ship(id)


class ShipConnection(relay.Connection):
    class Meta:
        node = Ship


class Faction(graphene.ObjectType):
    """A faction in the Star Wars saga"""

    class Meta:
        interfaces = (relay.Node,)

    name = graphene.String(description="The name of the faction.")
    ships = relay.ConnectionField(
        ShipConnection, description="The ships used by the faction."
    )

    def resolve_ships(self, info, **args):
        # Transform the instance ship_ids into real instances
        return [get_ship(ship_id) for ship_id in self.ships]

    @classmethod
    def get_node(cls, info, id):
        return get_faction(id)


class IntroduceShip(relay.ClientIDMutation):
    class Input:
        ship_name = graphene.String(required=True)
        faction_id = graphene.String(required=True)

    ship = graphene.Field(Ship)
    faction = graphene.Field(Faction)

    @classmethod
    def mutate_and_get_payload(
        cls, root, info, ship_name, faction_id, client_mutation_id=None
    ):
        ship = create_ship(ship_name, faction_id)
        faction = get_faction(faction_id)
        return IntroduceShip(ship=ship, faction=faction)


class Query(graphene.ObjectType):
    rebels = graphene.Field(Faction)
    empire = graphene.Field(Faction)
    node = relay.Node.Field()

    def resolve_rebels(root, info):
        return get_rebels()

    def resolve_empire(root, info):
        return get_empire()


class Mutation(graphene.ObjectType):
    introduce_ship = IntroduceShip.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)