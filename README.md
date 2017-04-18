# AlexaZork

Zork for your Amazon Alexa device.

This project was made by Team DevOps Dungeoneers (Jacob Foster, Matt Thompson, and Myles Loffler) and published on [hackster.io](https://www.hackster.io/devops-dungeoneers/classic-zork-494ff1).

The initial project was updated with documentation and installation instructions, as well as with changes to the Lambda function to get it to run.

# Notes
The version of Zork is based on the MIT Dungeon game. If you are looking at walkthroughs and maps online, many of them are for Infocom version.

![MIT Zork Dungeon Map](https://i.redd.it/6cxj790ozfjy.jpg)


# Files

The files in this project are defined below. They are organized by their target (Alexa Skill, Lamdba Function, and S3 storage).

## Alexa Skill

These files are used to create the Alexa Skill and will be used in the Alexa Skill developer portal. https://developer.amazon.com/edw/home.html#/skills.

* **intents.json** - This file contains the intents for the Alexa Skill and will be pasted in to the Interaction Model Intent Schema.
* **utterances.txt** - This file contains the possible utterances and is used to configure the Alexa Skill in the "Sample Utterances" section.

### alexa-types
These file represent the types used to configured the Alexa Skill. Each type file contains the list of possible values.
* **LOCATION**
* **NOUN**
* **SWITCH**
* **USING**
* **VERB**

## Lamda
These files are used to build the Lambda function that takes the utterances from the Alexa Skill and processes the command against the Zork game binary.
* **dtextc.dac** - Holds text strings and initialization information for the game.
* **zork** - This is the compiled Zork game binary.
* **lambda_function.py** - This is the Python Lambda function.
* **zork.properties.sample** - Sample zork.properties file.
* **zorkreadme.txt** - This is the readme for Zork.


# Installation Instructions

In order to get the game working on Alexa, you will need to deploy an Alexa Skill, a Lamdba function, and an S3 bucket. Additionally, you will create an Identify and Access Management (IAM) user that will be used by your Lamdba function to access the S3 bucket. The installation instructions will go in reverse order to simplify the configuration of previous steps and to allow for the Alexa Skill to be tested when it is deployed.

# Create IAM User

First, create a new IAM User. Full instructions on the process can be found here: http://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html.
1. Log in to the [AWS Console](https://console.aws.amazon.com/).
2. Navigate to *Identify and Access Management (IAM)*.
3. Click *Users*.
4. Click *Add User*.
5. Give your user a name and check the **Programmatic Access** box.
6. Click *Next: Permissions*.
7. Click *Next: Review*.
8. Click *Create User*.
9. Copy the **User ARN**, **Access key ID**, **Secret access key** values.

# Create S3 Bucket

Next, we're going to create the S3 bucket that will be used to save the game progress.

1. Log in to the [AWS Console](https://console.aws.amazon.com/).
2. Navigate to *S3*.
3. Click *Create Bucket*.
4. Give it a name and region and click *Next*.
5. You do not need to change the properties. Click *Next*.
6. Leave the permissions as the default values and click *Next*.
7. Click *Create Bucket*.
8. From the dashboard, click on the name of the bucket you just created.
9. Click the *Permissions* tab.
10. Click the *Buckey Policy* button.
11. Copy the text from the **polcy.sample** file in the S3 folder.
12. Update the **"AWS": "arn:aws:iam::1483726191252:user/youriamuser"** line to reflect the **User ARN** for the IAM user you created above.
13. Update the **"Resource": "arn:aws:s3:::yourbuckename/*"** line to reflect the name of the S3 bucket you created.

# Create Lamdba Function

Next, we're going to create the Lamdba function. This is the Python function that takes input from the Alexa Skill, executes it against the Zork binary, and returns the output back to the Alexa Skill. It needs to be configured to point to your S3 bucket which will be done through *environment variables*.

1. Log in to the [AWS Lamdba Console](https://console.aws.amazon.com/lambda/).
2. Click *Create a Lambda Function*.
3. Select the **Blank Function** template.
4. On the **Configure triggers** screen, click the empty box next to the Lamdba icon and select **Alexa Skills Kit** and click *Next*.
5. Give your function a name, description, and select **Python 2.7** as the runtime.
6. Create the following three environment variables in your function by typing the key and value in the **Environment variables** section:
  - **BUCKET** - Specify your S3 bucket name.
	- **SECRET_KEY** - Specify the secret key for your IAM user.
	- **ACCESS_KEY** - Specify the access key for your IAM user.
7. Create a zip file with the **dtextc.dat, lamdba_function.py, zork, and zorkreadme.txt** files.
8. In the *Code entry type* drop down, select **Upload a .zip file**.
9. Click *Upload* and select the zip file.
10. Select **lambda_basic_execution** in the **Existing role** drop down and click *Next*.
11. Click *Create function*.

**Note: Leave this AWS Lamdba browser window open. It will be useful for troubleshooting. You may also want to click on the Monitoring tab of your new function and click the *View logs in CloudWatch* link so that you can monitor the error logs.**

## Create Alexa Skill

Finally, we're going to create the Alexa Skill.

1. Log in to the [Alexa Skill Developer Console](https://developer.amazon.com/edw/home.html#/skills).
2. Click *Add a New Skill*.
3. Give the skill a **name** and **invocation name** and click *Save*.
4. Click the *Interaction model* tab.
5. Paste the contents of the *intents.json* file in to the **Intent Schema** box.
6. Paste the contents of the *utterances.txt* file in to the **Sample Utterances** box.
7. Next, for each of the files in the *alexa-types* folder, under **Custome slot types**:
  - Click *Add slot type*.
	- Use the name of the file (e.g., LOCATION) as the type name.
	- Paste the contents of the file in to the **Enter Values** box.
	- Click *Add*.
8. Once all the types are added, click the *Configuration* tab.
9. Get the ARN value from your Lambda function, select **AWS Lamdba ARN** as the type and paste your ARN value in to the **Service Endpoint** box.
10. Click *Next*.

# Testing

## Testing From The Alexa Skill Console

At this point, you should be full configured. On the *Test* tab of the Alexa Skill, you can enter "look" in the **Enter utterance** box and click "Ask". You should see the request and response.

## Testing From Alexa

If you have enabled it on the *Test* tab of your Alexa Skill, you can invoke your skill and test Zork on your Alexa.

# Troubleshooting
## Save Game and S3 Interaction
The game depends on the save game functionality working in order to sequence events. The leaflet test is a good example. When you open the mailbox and take the leaflet, if you succeed,
that means the sequencing is working. If you try to take the leaflet and the game responds that it can't find the leaflet, it's likely because the save game isn't working and the step that opens the mailbox was forgotten. You can verify by again opening the mailbox.

Check through the logs of CloudWatch to see if your Lamdba function is failing on the S3 save or load process. You can also check your bucket in S3 to verify that a file was created inside of a **saves** folder.

# Change Log
## Initial Release - December 1, 2016
Initial release by Team DevOps Dungeoneers.

## 0.0.1 - April 18, 2017
### Added
- Installation instructions and project information to the README.md

### Changed
- Updated file structure to create folders for the different targets (Alexa, Lamdba, S3).
- Updated Lamdba function to use environment variables

### Fixed
- Fixed lamdba function.
