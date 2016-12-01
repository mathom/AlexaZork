from __future__ import print_function

import base64
import json
import os
import shutil
import subprocess
import zlib
import boto3


BUCKET = 'alexazork'


def run_zork(input, save=None, look=False):
    if save:
        with open('/tmp/dsave.dat', 'wb') as out:
            out.write(zlib.decompress(base64.b64decode(save)))
        prefix = "restore\n"
        if look:
            prefix += "look\n"
        input = prefix + input

    input += "\nsave\n"

    if os.path.exists('/tmp/zork'):
        os.remove('/tmp/zork')
    if os.path.exists('/tmp/dtextc.dat'):
        os.remove('/tmp/dtextc.dat')

    shutil.copyfile('/var/task/zork', '/tmp/zork')
    shutil.copyfile('/var/task/dtextc.dat', '/tmp/dtextc.dat')
    os.chmod('/tmp/zork', 0755)

    os.chdir('/tmp')
    print('sending input to zork:', json.dumps({'input': input}))
    cmd = subprocess.Popen(['/tmp/zork'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = cmd.communicate(input)
    print('got output:', json.dumps({'stdout': stdout.split('\n'), 'stderr': stderr}))
    print('return code', str(cmd.returncode))
    message = stdout.replace('\n>', '\n')  # get rid of prompts
    message = message.split('\n', 1)[1]  # first line is header junk
    if save:
        message = message.split('\nRestored.\n')[1]  # strip leader before restoring the game
    message = message.split('\nSaved.\n')[0]
    message = message.replace('\n', ' ').replace('.', '.\n')
    return message


def get_save():
    if os.path.exists('/tmp/dsave.dat'):
        with open('/tmp/dsave.dat', 'rb') as save:
            return base64.b64encode(zlib.compress(save.read()))
    else:
        return None


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "Zork: " + title,
            'content': "Zork: " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


def get_save_key(session):
    user_id = session['user']['userId']
    return 'saves/' + user_id


def get_save_from_s3(save_key, s3):

    try:
        key = s3.get_object(Bucket=BUCKET, Key=save_key)
        saved_game = key['Body'].read()
    except:
        saved_game = None

    return saved_game

def get_welcome_response(session):
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = session.get('attributes', {})

    save_key = get_save_key(session)
    s3 = boto3.client('s3')
    saved_game = get_save_from_s3(save_key, s3)

    card_title = "Welcome"
    speech_output = "Welcome to Zork. "

    if saved_game:
        speech_output += "Resuming saved game."

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "You should probably walk somewhere."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for visiting Zork. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def do_zork(intent, session, command=None):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    s3 = boto3.client('s3')

    save_key = get_save_key(session)
    saved_game = get_save_from_s3(save_key, s3)

    if command:
        actions = command
    else:
        actions = [x[1]['value'] for x in sorted(intent['slots'].items(), key=lambda x: x[0]) if x[1].get('value')]
        actions = ' '.join(actions)

    print('intent was', intent)
    print('doing', actions)

    if actions:
        speech_output = run_zork(actions, save=saved_game)
        session_attributes = {'savegame': get_save()}

        s3.put_object(Bucket=BUCKET, Key=save_key, Body=get_save())  # TODO: expires

        reprompt_text = "What do you do next?"
    else:
        speech_output = "I'm not sure what that command was. " \
                        "Please try again."
        reprompt_text = "I'm not sure what that command was. " \
                        "You can say walk north to walk north."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def reset_game(intent, session):
    """ Clears out the s3 save and starts a new game. """
    save_key = get_save_key(session)
    s3 = boto3.client('s3')

    try:
        s3.delete_object(Bucket=BUCKET, Key=save_key)
    except:
        pass

    speechlet = build_speechlet_response(
        "Reset", "Your game has been reset.", "Move or look around.", False
    )
    return build_response(session.get('attributes', {}), speechlet)


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response(session)


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "DoZork":
        return do_zork(intent, session)
    elif intent_name.startswith("Command"):
        return do_zork(intent, session, intent_name.split("Command")[1].lower())
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response(session)
    elif intent_name in ["AMAZON.CancelIntent", "AMAZON.StopIntent", "AMAZON.PauseIntent"]:
        return handle_session_end_request()
    elif intent_name == "AMAZON.StartOverIntent":
        return reset_game(intent, session)
    # elif intent_name == "AMAZON.YesIntent":
    # elif intent_name == "AMAZON.NoIntent":
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
