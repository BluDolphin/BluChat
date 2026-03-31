# BluChat
Bluchat is a self-hosted SMS to LLM relay service to allow for searching for online content without any form of mobile data or internet connection. This projects main goal is to provide some level of internet access to areas with very poor or no form of internet access.

## Features
- LLM responses from a handful of LLM providers
  - Google
  - Deepseek
  - OpenAI 
  - Mistral 
  - Claude
- Open LLM model selection (use official LLM model names)
- Customisable LLM Context
- Whitelist for phone numbers
- Groups to manage numbers with custom settings
- Sensative data is stored encrypted (API keys, Phone numbers, LLM instructions)

## Hardware Used 
The project was developed on the following hardware but "should" be compatible with a anything that can run python, and modems which use AT commands.
- Raspberry Pi 5 (8gb)
- Clipper 4G LTE HAT Mini ([link](https://thepihut.com/products/clipper-hat-mini-lte-4g-for-raspberry-pi?variant=53799699775873))
- Generic physical SIM

## Installation


### Reccomended LLM Instructions
`Respond in less than 1000 characters, without any emojis. Do not include any
symbols which cannot be displayed via SMS. You do not have any form of memory, do not ask for follow ups.`
