# AlexaZork

Zork for your Amazon Alexa device.

The version of zork is based on the MIT Dungeon game, so if you are looking at walktrhoughs, many of them are for infocom version.

# Files

The files in this project are defined below.

## Alexa Skill
<ul>
	<li><strong>intents.json</strong> - This file contains the intents for the Alexa Skill.</li>
	<li>utterences.txt</li> - This file contains the possible utterences and is used to configure the Alexa Skill.
</ul>

### alexa-types
These file represent the types used to configured the Alexa Skill. Each type file contains the list of possible values.
<ul>
	<li>LOCATION</li>
	<li>NOUN</li>
	<li>SWITCH</li>
	<li>USING</li>
	<li>VERB</li>
</ul>

## Lamda
These files are used to build the Lambda function that takes the utterences from the Alexa Skill and processes the command against the Zork game binary.
<ul>
	<li>dtextc.dac - This file holds the text strings and initialization information for the game.</li>
	<li>zork - This is the compiled Zork game binary.</li>
	<li>lambda_function.py - This is the Python lambda function.</li>
	<li>zork.properties.sample - Sample zork.properties file.</li>
	<li>zorkreadme.txt - This is the readme for Zork. </li>
</ul>

# Installation Instructions

In order to get the game working on Alexa, you will need to deploy an Alexa Skill, a Lamdba function, and an S3 bucket. Additionally, you will create an IAM 
user that will be used by your Lamdba function to access the S3 bucket.

## Create IAM User
Instructions
Get the secret and key, used in configuration
## Create S3 bucket
Create bucket. Get the bucket name for configuration.
Create policy on bucket for IAM user.
## Create Lamdba function
instructions
environment variables - encrypted, and you can change them without redeploying code
## Create Alexa Skill
insturcions

# Test
## Test with Alexa Skill


## Test on Alexa
	Play Alexa
	Open mailbox
	Take leaflet
	Read leaflet
## Troubleshoot
	The game depends on the save game functionality working in order to sequence events. The leaflet test is a good example. When you open the mailbox and take the leaflet, if you succeed, 
	that means the sequencing is working. If you try to take the leaflet and the game responds that it can't find the leaflet, it's likely because the save game isn't working and the step that 
	opens the mailbox was forgotten. You can verify by again opening the mailbox. 
	
# Version History
# Initial Release
# Updated file structure to create folders for the different targets (Alexa, Lamdba, S3).
# Updated lamdba function.
# Updated README.md to include project information and installation instructions.

https://i.redd.it/6cxj790ozfjy.jpg