# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
from cgitb import handler
import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

from utils import *
from game_utils import *
from constants import *
from game_classes import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

game_state = None
END = False

# TODO
# CHECK BLOCKS
# GAME STATE SOMETIMES GETS SET TO NULL
# END GAME STATE

def end_game_check(handler_input):
    if END == True:
        return (handler_input.response_builder.speak("The game has ended.").ask("The game has ended").response)
    return False

def can_handle_name_based(handler_input, class_name):
    logger.error(f"can_handle_called {class_name} {handler}")
    intents_to_class_names = {
        "examineLocation": "ExamineLocationHandler",
        "specialActionIntent": "SpecialCommandHandler",
        "pickupItem": "PickUpItemRequestHandler",
        "directionIntent": "DirectionRequestHandler",
        "inventoryIntent": "ExamineInventoryHandler",
    }
    resolved_intent_name = ask_utils.get_intent_name(handler_input)
    if intents_to_class_names[resolved_intent_name] == class_name:
        return True
    return False

class SpecialCommandHandler(AbstractRequestHandler):
    '''Handles all special commands'''

    def can_handle(self, handler_input):
        return can_handle_name_based(handler_input, "SpecialCommandHandler")
    def handle(self, handler_input):
        global game_state
        global END
        kill = end_game_check(handler_input)
        if kill is not False:
            return kill
        item1 = ask_utils.request_util.get_slot_value(
            handler_input, "item")
        if item1 and isinstance(item1, str):
            item1 = item1.strip().lower()
        item2 = ask_utils.request_util.get_slot_value(
            handler_input, "item_")
        if item2 and isinstance(item2, str):
            item2 = item2.strip().lower()
        if item1 == "fish" and item2 is None:
            # Catch fish
            speak_output, end_game = run_special_command(game_state, "catch fish")
        elif item1 == "fish" and item2 in ["pole", "fishing pole"]:
            speak_output, end_game = run_special_command(game_state, "catch fish with pole")
            # Catch fish with fishing pole
        elif item1 == "troll" and (item2 is None or item2 in ['branch', 'club', 'stick']):
            # Hit troll with club
            speak_output, end_game = run_special_command(game_state, "attack troll")
            END = True
        elif item1 == "troll" and item2 == "fish":
            speak_output, end_game = run_special_command(game_state, "feed troll a fish")
        elif item1 == "rose" and item2 is None:
            speak_output, end_game = run_special_command(game_state, "smell rose")
        elif item1 == "tree" and item2 is None:
            speak_output, end_game = run_special_command(game_state, "climb tree")
        elif item1 == "guard" and item2 == "club":
            speak_output, end_game = run_special_command(game_state, "hit guard with club")
        # TODO READ RUNES AND SIT ON THRONE
        elif item1 == "runes" and item2 == "candle":
            speak_output, end_game = run_special_command(game_state, "read runes")
        elif item1 == "throne" and item2 == None:
            speak_output, end_game = run_special_command(game_state, "sit on throne")
            END = True
        elif item1 == "key" and item2 == "door":
            speak_output, end_game = run_special_command(game_state, "open")
        logger.error(f"GAME STATE IN SPECIAL COMMANDS END {game_state}")
        return (handler_input.response_builder.speak(speak_output).ask(speak_output).response)


class ExamineLocationHandler(AbstractRequestHandler):
    '''Handler for look'''

    def can_handle(self, handler_input):
        return can_handle_name_based(handler_input, "ExamineLocationHandler")
    def handle(self, handler_input):
        kill = end_game_check(handler_input)
        if kill is not False:
            return kill
        speak_output = game_state.describe()
        return (handler_input.response_builder.speak(speak_output).ask(speak_output).response)


class ExamineInventoryHandler(AbstractRequestHandler):
    '''Handler for look inventory'''

    def can_handle(self, handler_input):
        return can_handle_name_based(handler_input, "ExamineInventoryHandler")

    def handle(self, handler_input):
        kill = end_game_check(handler_input)
        if kill is not False:
            return kill
        speak_output = check_inventory(game_state)
        return (handler_input.response_builder.speak(speak_output).ask(speak_output).response)


class PickUpItemRequestHandler(AbstractRequestHandler):
    ''' Handler for Intent Pick up Item '''

    def can_handle(self, handler_input):
        return can_handle_name_based(handler_input, "PickUpItemRequestHandler")

    def handle(self, handler_input):
        '''The user wants to pick up an item'''
        global game_state
        global END
        kill = end_game_check(handler_input)
        if kill is not False:
            return kill
        item = ask_utils.request_util.get_slot_value(handler_input, "item")
        prompt, end_game = take(game_state, item)
        if game_state is not None:
            logger.error(f"game state is not None {game_state}")
        return (handler_input.response_builder.speak(prompt).ask(prompt).response)


class DirectionRequestHandler(AbstractRequestHandler):
    """Handler for Intent Direction."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return can_handle_name_based(handler_input, "DirectionRequestHandler")

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        """ The user wants to go in some direction """
        global game_state
        global END
        kill = end_game_check(handler_input)
        if kill is not False:
            return kill
        # direction =  ask_utils.get_intent_name(handler_input)
        direction = ask_utils.request_util.get_slot_value(
            handler_input, "direction")
        speak_output = ""
        if game_state:
            logger.error(f"BLOCKS{game_state.curr_location.blocks} - Location {game_state.curr_location.name}")
        if direction in game_state.curr_location.connections:
            if game_state.curr_location.is_blocked(direction, game_state):
                # check to see whether that direction is blocked.
                speak_output = game_state.curr_location.get_block_description(
                    direction)
            else:
                # if it's not blocked, then move there
                game_state.curr_location = game_state.curr_location.connections[direction]

                # If moving to this location ends the game, only describe the location
                # and not the available items or actions.
                if game_state.curr_location.get_property('end_game'):
                    speak_output = game_state.describe_current_location()
                else:
                    speak_output = game_state.describe()
        else:
            speak_output = "You can't go %s from here." % direction.capitalize()

        END = game_state.curr_location.get_property('end_game')

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        global game_state
        global END
        game_state = build_game()
        END = False
        speak_output = "Welcome, to action castle! " + game_state.describe()

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Maybe Look around?"

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
        )


class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = game_state.describe()

        return handler_input.response_builder.speak(speech).response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input) or END == True

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(ExamineInventoryHandler())
sb.add_request_handler(ExamineLocationHandler())
sb.add_request_handler(DirectionRequestHandler())
sb.add_request_handler(PickUpItemRequestHandler())
sb.add_request_handler(SpecialCommandHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
