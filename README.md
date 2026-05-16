# BluChat
Bluchat is a self-hosted SMS to LLM relay service which allows searching content on the internet without any form of mobile data or internet connection. This projects main goal is to provide some level of internet access/retrieval to areas with very poor or no internet access.

## Features
- LLM responses from a handful of LLM providers
  - Google
  - Deepseek
  - OpenAI 
  - Mistral 
  - Anthropic (Claude)
- Local web interface for configuring settings
- Open ended LLM model selection (use official LLM model names)
- Customisable LLM Instructions (Response Context)
- Whitelist for allowed phone numbers
- Groups to manage numbers with customisable settings
- Sensative data (API keys, Phone numbers, LLM instructions) is stored encrypted on device

## Hardware Requirements 
The project was developed on the following hardware but "should" be compatible with a any Raspberry Pi, and modems which use AT commands.
- Raspberry Pi 5 (8gb) - w/ Stock Raspberry Pi OS
- Clipper 4G LTE HAT Mini ([link](https://thepihut.com/products/clipper-hat-mini-lte-4g-for-raspberry-pi?variant=53799699775873))
- Generic physical SIM

## Installation & Setup
### Installation
- Git clone this repository (or download zip and unzip)
- Navigate to folder
- Create python virtual environment
- Install requirements.txt within the virtual environment

To run the program once setup, run `bash run_bluchat.sh`, this will create a detached tmux session and launch the program using the virtual environment. tmux is used to allow the terminal to be closed after starting BluChat.

### Setup
I recommend assigning a static IP to the Raspberry Pi in your routers settings, just to make accessing the settings portal easier 

Once the program is running, using another device nativage too `http://[IP Address]:8080` which will show the BluChat setup page

Proceed to set a password for BluChat, **this cannot be changed without deleting your settings**.

Following this navigate to the settings page and enter your API key for your chosen model (or models).

Set the "default LLM for chats" to your chosen LLM.

When texting the system make sure your sending SMS messages and not RCS or other technologies, this should be togglable on your phone's messaging app.

To update or change the providers LLM model, enter the LLM's model name found within the providers developer documentation.

### Reseting System/ Changing Password
To reset the system delete the folder `data` then restart the program, this will trigger the first time setup again, allowing for a new password to be set.

Note: all currently saved data will be deleted (obviously), and will require re-reconfiguring the system.

## Current Limitations
Currently the LLM's have no form of memory, meaning requests need to contain all the info needed to generate a response. 

As well as this only Gemini has the web searching tool implemented allowing it to search the internet. The rest try to generate a result on their own, if you need more accurate, or up to date info use Gemini.

Certian caracters, such as the '°' for degrees C/F and emojis, cannot be sent over SMS and end up being replaced by letters and numbers (e.g. B1G for fahrenheit, B1C for celcius).

## Reccomended LLM Instructions (Response Context)
`Respond in less than 1000 characters, without any emojis. Do not include any
symbols which cannot be displayed via SMS. You do not have any form of memory, do not ask for follow ups.`
