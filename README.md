# Mandy

## About
Silly little discord bot that continuously plays bad music.

## Installation
```shell
# Open Command Prompt or Powershell on Windows and Terminal on Mac or Linux

# Check if Git is installed
git --version
# Download it here if it is not installed 
# https://git-scm.com/downloads

# Check if python is installed 
python --version
# Download the latest version if it is not installed
# https://www.python.org/downloads/

# Clone the repository
git clone https://github.com/Bashiho/Mandy.git

# Navigate to the project's directory
cd Mandy

# Create a file called .env
# In this .env file, write the following, and paste your bot token where it says 'YOUR TOKEN' 
# TOKEN = 'YOUR TOKEN'

# Create a virtual environment however you like

# Install Requirements
pip install -r Requirements.txt
# you might be asked to update pip, if so, then run the command given to do so
```

##Commands
#Prefix
The default command prefix is "!!"
#Uhoh
"!!uhoh" will run the main function of Mandy. This will load the playlist via the link stored in "PL".
#Link
"!!link" will cause the bot to send a message with the link to the playlist.
#Skip
"!!skip" will skip the current song and start the next song.
#Pause
"!!pause" will pause whatever is being played.
#Play
"!!play" will resume play of whatever was playing.
#Stop
"!!stop" will cause the bot to stop what it is doing and leave vc.
#Name
"!!name" will cause the bot to send a message with the title of the currently playing video.