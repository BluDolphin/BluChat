# BluChat
Bluchat is a self-hosted SMS to LLM relay service to allow for searching for online content without any form of mobile data or internet connection. This projects main goal is to provide some level of internet access to areas with very poor or no form of internet access.

## Features
- LLM responses from a handful of LLM providers
  - Google
  - Deepseek
  - OpenAI 
  - Mistral 
  - Claude
- Open ended LLM model selection (use official LLM model names)
- Customisable LLM Context
- Whitelist for phone numbers
- Groups to manage numbers with custom settings
- Sensative data (API keys, Phone numbers, LLM instructions) is stored encrypted on device

## Hardware Requirements 
The project was developed on the following hardware but "should" be compatible with a any Raspberry Pi, and modems which use AT commands.
- Raspberry Pi 5 (8gb)
- Clipper 4G LTE HAT Mini ([link](https://thepihut.com/products/clipper-hat-mini-lte-4g-for-raspberry-pi?variant=53799699775873))
- Generic physical SIM
- Stock Raspberry Pi OS

## Installation & Setup
### Installation
- Git clone this repository (or download zip and unzip)
- Navigate to folder
- Create python .venv
- Install requirements.txt within .venv

To run the program once setup, run `bash run_bluchat.sh`, this will create a new detached tmux session, and launch the program with the .venv. tmux is used to allow the terminal to be closed after starting BluChat.

### Setup
Once the program is running the program will request a password to be set, **this cannot be changed without deleting your settings**

Following this navigate to the settings page and enter your API key for your chosen model (or models)

Set the "default LLM for chats" to your chosen LLM

### Reseting System/ Changing Password
To reset the system delete the folder `data` then restart the program, this will trigger the first time setup again, allowing for a new password to be set.

Note: all currently saved data will be deleted (obviously), and will require re-reconfiguring the system


## Reccomended LLM Instructions
`Respond in less than 1000 characters, without any emojis. Do not include any
symbols which cannot be displayed via SMS. You do not have any form of memory, do not ask for follow ups.`
