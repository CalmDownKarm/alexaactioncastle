from game_classes import *
from game_classes import Location, Item


def run_special_command(game, command):
    """Run a special command associated with one of the items in this location
       or in the player's inventory"""
    for item in game.get_items_in_scope():
        special_commands = item.get_commands()
        for special_command in special_commands:
            if command == special_command.lower():
                return item.do_action(special_command, game)


def perform_multiple_actions(game, *args):
    (actions) = args[0]
    descriptions = [action(game, params) for action, params in actions]
    strung = " ".join([d for d in descriptions if isinstance(d, str)])
    return strung


def add_item_to_inventory(game, *args):
    """ Add a newly created Item and add it to your inventory."""
    (item, action_description, already_done_description) = args[0]
    if(not game.is_in_inventory(item)):
        game.add_to_inventory(item)
        return action_description
    return already_done_description


def take(game, *args):
    """ The player wants to put something in their inventory """
    # This gets set to True if posession of this object ends the game.
    end_game = False
    (item_name) = args[0]

    # check whether any of the items at this location match the command
    if item_name in game.inventory:
        return f"You already have {item_name}", end_game
    item = game.curr_location.items.get(item_name, None)
    if item:
        if item.get_property('gettable'):
            game.add_to_inventory(item)
            game.curr_location.remove_item(item)
            end_game = item.get_property('end_game')
            return item.take_text, end_game
        else:
            return "You cannot take the %s." % item_name, end_game
    return f"You can't find {item_name}", end_game


def check_inventory(game):
    """ The player wants to check their inventory"""
    if len(game.inventory) == 0:
        return "You don't have anything. Git Gud"
    else:
        descriptions = []
        for item_name in game.inventory:
            item = game.inventory[item_name]
            descriptions.append(item.description)
        return "You have: " + ", ".join(descriptions)


def describe_something(game, *args):
    """Describe some aspect of the Item"""
    # We don't need the game object here
    (description) = args[0]
    return description


def destroy_item(game, *args):
    # Destroy Item can never end the game
    """Removes an Item from the game by setting its location is set to None."""
    (item, action_description, already_done_description) = args[0]
    logger.error(
        f"item: {item}, action Description : {action_description}, Done: {already_done_description}")
    if game.is_in_inventory(item):
        game.inventory.pop(item.name)
        return action_description
    elif item.name in game.curr_location.items:
        game.curr_location.remove_item(item)
        return action_description
    return already_done_description


def create_item(game, *args):
    (item, action_description, already_done_description) = args[0]
    if item.name not in game.curr_location.items:
        game.curr_location.add_item(item.name, item)
        return action_description
    return already_done_description


def create_item_at_location(game, *args):
    (item, location, action_description) = args[0]
    if item.name not in location.items:
        location.add_item(item.name, item)
    return False


def end_game(game, *args):
    """Ends the game."""
    end_message = args[0]
    return end_message


def build_game():
    # Locations
    nowhere = Location("nowhere", "")
    cottage = Location(
        "Cottage", "You are standing in a small cottage. There is a fishing pole here. A door leads outside.")
    garden_path = Location(
        "Garden Path", "You are standing on a lush garden path that leads North and South. There is a rosebush here. There is a cottage here.")
    pond = Location(
        "Fish Pond", "You are at the edge of a fish pond. A path leads North.")
    winding_path = Location(
        "Winding Path", "You are at the edge of a winding path that leads South and East. There is a tall tree here.")
    up_tall_tree = Location(
        "Tall Tree", "You're on top of a tall tree, you can see for miles.")
    drawbridge = Location(
        "Drawbridge", "You come to the drawbridge of Action Castle. There is a mean troll guarding the bridge.")
    courtyard = Location(
        "Courtyard", "You are in the courtyard of Action Castle. A castle guard stands watch to the East. Stairs lead up into the tower and down into the darkness.")
    tower_stairs = Location(
        "Tower Stairs", "You climb the tower stairs until you come to a door")
    dungeon_stairs = Location(
        "Dungeon Stairs", "You are on the dungeon stairs. It's very dark here")
    tower = Location(
        "Tower", "You are in the tower. There is a princess here. Stairs lead down")
    dungeon = Location(
        "Dungeon", "You are in the dungeon. There is a spooky ghost here. Stairs lead up")
    great_feasting_hall = Location(
        "Great Feasting Hall", "You stand inside the great feasting hall. There is a strange candle here. Exits are to the East and West")
    throne_room = Location(
        "Throne Room", "This is the throne room of Action Castle. There is an ornate gold throne here.")

    # Connections
    cottage.add_connection("out", garden_path)
    garden_path.add_connection("north", winding_path)
    garden_path.add_connection("south", pond)
    garden_path.add_connection("enter", cottage)

    pond.add_connection("north", garden_path)

    winding_path.add_connection("south", garden_path)
    winding_path.add_connection("east", drawbridge)
    winding_path.add_connection("up", up_tall_tree)

    up_tall_tree.add_connection("down", winding_path)

    drawbridge.add_connection("west", winding_path)
    drawbridge.add_connection("east", courtyard)

    courtyard.add_connection("east", great_feasting_hall)
    courtyard.add_connection("west", drawbridge)
    courtyard.add_connection("up", tower_stairs)
    courtyard.add_connection("down", dungeon_stairs)

    tower_stairs.add_connection("in", tower)
    tower_stairs.add_connection("up", tower)

    dungeon_stairs.add_connection("up", courtyard)
    dungeon_stairs.add_connection("down", dungeon)

    tower.add_connection("down", tower_stairs)

    dungeon.add_connection("up", dungeon_stairs)

    great_feasting_hall.add_connection("east", throne_room)
    great_feasting_hall.add_connection("west", courtyard)

    throne_room.add_connection("west", great_feasting_hall)

    # Items that you can pick up
    fishing_pole = Item("pole", "a fishing pole",
                        "YOU SEE A SIMPLE FISHING POLE.", start_at=cottage)
    lamp = Item("lamp", "a lamp",
                "YOU SEE AN OLD LAMP; IT'S CURRENTLY UNLIT", start_at=cottage)
    rose = Item("rose", "a red rose",
                "A BEAUTIFUL ROSE WITH THREE THORNS",  start_at=garden_path)
    fish = Item("fish", "a dead fish", "IT SMELLS TERRIBLE.", start_at=nowhere)
    branch = Item("branch", "a dead tree branch",
                  "YOU THINK IT WOULD MAKE A GOOD CLUB.", start_at=up_tall_tree)
    key = Item("key", "a key", "A SMALL LIGHT GOLD KEY.", start_at=None)
    crown = Item("crown", "a gold crown",
                 "YOU SEE A GOLD CROWN THAT ONCE BELONGED TO THE KING OF ACTION CASTLE")
    candle = Item("candle", "a strange candle",
                  "YOU SEE A STRANGE OMINOUS CANDLE FLICKERING", start_at=great_feasting_hall)
    princess = Item("princess", "the princess is beautiful, sad and lonely.",
                    start_at=tower, examine_text="The princess is beautiful, sad and lonely.")

    # Sceneary (not things that you can pick up)
    fishing_pond = Item("fishpond", "a pond", start_at=pond)
    rosebush = Item("rosebush", "a rosebush",
                    "THE ROSEBUSH CONTAINS A SINGLE RED ROSE.  IT IS BEAUTIFUL.", start_at=garden_path)
    rosebush.set_property("gettable", False)
    tree = Item("Tree", "a tall tree",
                "YOU SEE A TALL STURDY TREE", start_at=winding_path)
    tree.set_property("gettable", False)
    climbed_tree = Item("climbed tree", "a tall tree that you're at the top of",
                        "YOU SEE BRANCHES OF A TREE. YOU'RE AT THE TOP")
    climbed_tree.set_property("gettable", False)

    troll = Item("troll", "a mean troll",
                 "THE TROLL HAS A WARTY GREEN HIDE AND LOOKS HUNGRY", start_at=drawbridge)
    troll.set_property("gettable", False)
    guard = Item("guard", "a castle guard",
                 "THE GUARD WEARS CHAINMAIL ARMOR BUT NO HELMET. A KEY HANGS FROM THE GUARDS BELT.", start_at=courtyard)
    guard.set_property("gettable", False)
    door = Item("door", "a door",
                "YOU SEE A DOOR AT THE TOP OF THE STAIRS", start_at=tower_stairs)
    door.set_property("gettable", False)
    unlocked_door = Item("unlocked door", "a door",
                         "YOU SEE A DOOR AT THE TOP OF THE STAIRS. IT'S UNLOCKED")
    unlocked_door.set_property("gettable", False)

    ghost = Item("ghost", "a spooky ghost",
                 "THE GHOST HAS BONY, CLAW-LIKE FINGERS AND WEARS A GOLD CROWN", start_at=dungeon)
    ghost.set_property("gettable", False)
    throne = Item("throne", "a ornate gold throne",
                  "YOU SEE AN ORNATE GOLD THRONE", start_at=throne_room)
    throne.set_property("gettable", False)

    talked_to = Item(
        "talked to", "the princess appreciates your conversation and is warming up to you.")
    talked_to.set_property("gettable", False)
    lit_lamp = Item("lit lamp", "a lit lamp",
                    "YOU SEE AN OLD LAMP; IT'S CURRENTLY LIT")
    lit_lamp.set_property("gettable", False)
    lit_candle = Item("lit candle", "a lit candle",
                      "YOU SEE A TALL CANDLE. IT'S CURRENTLY LIT")
    lit_candle.set_property("gettable", True)

    wearing_crown = Item("wearing crown", "You are wearing the crown")
    wearing_crown.set_property("gettable", False)

    # Add special functions to your items

    rose.add_action("smell rose",  describe_something, ("It smells sweet."))
    rose.add_action("smell rose",  describe_something, ("It smells sweet."))
    lamp.add_action("light lamp", create_item, (lit_lamp,
                    "The lamp lights up the room around it."), preconditions={"in_location": dungeon_stairs})
    # tree.add_action("climb tree", perform_multiple_actions, ([
    #                 (describe_something,
    #                  ("You climb up the tree - it takes a long time")),
    #                 (destroy_item, (tree,
    #                  "You shimmy your way up the tree grabbing branches and pulling yourself up")),
    #                 (create_item, (climbed_tree, "You climbed up the tree")),
    #                 (create_item, (branch, "You see a dead branch, you think it would make a good club"))]))
    # branch.add_action("break branch", destroy_item,
    #                   (branch, "You snap the branch in half"))
    climbed_tree.add_action("look", describe_something,
                            ("You are at the top of the tall tree"))
    climbed_tree.add_action("climb down", perform_multiple_actions, ([(destroy_item, (climbed_tree, "You shimmy your way down the tree, it takes a long time")),
                                                                      (create_item, (
                                                                          tree, "You touch the ground safely"))
                                                                      ]), preconditions={"location_has_item": climbed_tree})
    climbed_tree.add_action("jump", end_game, ("You did not survive the fall. THE END"), preconditions={
                            "location_has_item": climbed_tree})

    troll.add_action("attack troll", end_game,
                     ("you did not pay the toll, so the troll rips you limb from limb"))
    troll.add_action("feed troll a fish", perform_multiple_actions, ([(destroy_item, (fish, "You tentatively hand the troll a fish", "you already gave it the fish")),
                                                                      (destroy_item, (
                                                                          troll, "The troll grabs the fish and scurries away to eat, the path is clear", "The troll already took the fish"))
                                                                      ]), preconditions={"inventory_contains": fish})

    door.add_action("open", perform_multiple_actions, (
                    [(destroy_item, (door, "You put the troll's key in the door and turn...", "Already opened")),
                        (create_item, (unlocked_door, "The door is unlocked.", "The door is already unlocked"))]), preconditions={"inventory_contains": key})

    candle.add_action("light candle", perform_multiple_actions,
                      ([(create_item, (lit_candle, "You light the candle. It gives off a strange acrid smoke, causing the ghost to flee the dunegeon. It leaves behind a gold crown.")),
                       (create_item, (crown, "The crown is in front of you.."))]), preconditions={"in_location": dungeon})

    # princess.add_action("ask about crown", perform_multiple_actions,
    #                     [(describe_something, ("My father's crown was lost after he died")),
    #                      (create_item, (talked_to, "The princess appreciates your conversation. She's warming up to you."))])
    # princess.add_action("ask about tower", perform_multiple_actions,
    #                     [(describe_something, ("I cannot leave the tower until I'm wed!")),
    #                      (create_item, (talked_to, "The princess appreciates your conversation. She's warming up to you."))])

    # princess.add_action("ask about throne", perform_multiple_actions,
    #                     [(describe_something, ("Only the rightful ruler of Action Castle may claim the thrown")),
    #                      (create_item, (talked_to, "The princess appreciates your conversation. She's warming up to you."))])

    # princess.add_action("give crown to princess", perform_multiple_actions,
    #                     [(describe_something, ("My father's crown! You have put his soul to rest and may now take his place as the ruler of this land!")),
    #                      (create_item, (wearing_crown,
    #                       "She places the crown on your head")),
    #                      (add_item_to_inventory, (wearing_crown, "It looks good on you!", "You have the crown."))])

    throne.add_action("sit on throne", end_game,
                      ("You are now the ruler of Action Castle! THE END"))

    fishing_pond.add_action("catch fish",  describe_something, (
        "You reach into the pond and try to catch a fish with your hands, but they are too fast."))
    fishing_pond.add_action("use fishing pole",  add_item_to_inventory, (fish, "You dip your hook into the pond and catch a fish.",
                            "You weren't able to catch another fish."), preconditions={"inventory_contains": fishing_pole})
    fishing_pond.add_action("catch fish with pole",  add_item_to_inventory, (fish, "You dip your hook into the pond and catch a fish.",
                            "You weren't able to catch another fish."), preconditions={"inventory_contains": fishing_pole})
    fish.add_action("eat fish",  end_game,
                    ("That's disgusting! It's raw! And definitely not sashimi-grade! But you've won this version of the game. THE END."))

    guard.add_action("hit guard with club", perform_multiple_actions, ([(destroy_item, (branch, "You smack the guard on the head and knock him out, he drops a key", "you already hit him")),
                                                                        (create_item, (key,
                                                                         "The guard drops a key", "can't drop a key twice")),
                                                                        (destroy_item, (
                                                                            guard, "The guard is knocked out and no longer blocks the way", "guard goes poof"))
                                                                        ]), preconditions={"inventory_contains": branch})
    candle.add_action("read runes", describe_something,
                      ("The odd runes are part of an exorcism ritual used to dispel evil spirits"))
    lit_candle.add_action("read runes", describe_something, (
        "The odd runes are part of an exorcism ritual used to dispel evil spirits"))

    # Blocks
    tower_stairs.add_block("in", "The door is locked. You can't go in.", preconditions={
                           "location_has_item": unlocked_door})
    tower_stairs.add_block("up", "The door is locked. You can't go up.", preconditions={
                           "location_has_item": unlocked_door})
    dungeon_stairs.add_block("down", "You can't go down it's too dark to see", preconditions={
                             "location_has_item": lit_lamp})
    drawbridge.add_block("east", "The Troll blocks your path", preconditions={
                         "location_does_not_have_item": troll})
    
    courtyard.add_block("east", "The guard blocks your path", preconditions={
                        "location_does_not_have_item": guard})

    return Game(cottage)

