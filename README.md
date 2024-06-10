# Read My News :newspaper::microphone::speaker:

Today, there is such an abundance of news and information that it is a real challenge to stay up-to-date on the topics that interest us the most. Our project aims to compress this abundance of news and information through a news recommendation system capable of providing this content in a summarized, precise, and easy-to-digest manner, both in easy reading text and voice, and in multiple languages. This way, people with visual impairments can stay informed in an accessible way, thanks to Azure AI Speech's Speech-to-Text and Text-to-Speech services, and the incredible Generative AI of the Azure OpenAI Service.

## Azure AI Resource Creation

1. Create an Azure AI Speech resource on Azure, and obtain its Key and Region from Resource Management > Keys and Endpoints.
2. Create an Azure AI Language resource on Azure, and obtain its Endpoint and Key from Resource Management > Keys and Endpoints.
3. Create an Azure AI Translator resource on Azure, and obtain its Text Translation Endpoint and Key from Resource Management > Keys and Endpoints.
4. Create an Azure OpenAI resource on Azure, and obtain its Key and Endpoint from Resource Management > Keys and Endpoints.
5. Open Azure OpenAI Studio, deploy a new GPT model (3.5 or better recommended), and obtain your model's deployment name, e.g. 'mygpt4modeldeployment'.
6. Choose an Azure OpenAI API version, e.g. "2024-02-01". The available OpenAI API versions can be found [here](https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#chat-completions).
7. After cloning the repository (steps below), rename the provided .env-example file to just '.env', and enter the corresponding values from the previous steps.

## Installing the App
Open up a Terminal (macOS/Linux) or PowerShell (Windows) and enter the following commands:
### Cloning the repository
```sh
git clone https://github.com/Underdoge/ReadMyNews

cd ReadMyNews
```
### Creating the virtual environment
```sh
python -m venv venv
```
### Activating the virtual environment on macOS / Linux
```sh
source venv/bin/activate
```
### Activating the virtual environment on Windows (PowerShell)
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```
### Installing requirements
```sh
pip install -r requirements.txt
```
### Installing ffmpeg (required for Speech Synthesis)
### On Windows
```powershell
winget install ffmpeg
```
### On Linux (Ubuntu and other distros)
```sh
apt install ffmpeg
```
### On macOS (using brew)
```sh
brew install ffmpeg
```
# Running the App
### Running the command line app
```sh
python app.py
```
### Running the Streamlit app
```sh
streamlit run streamlit.py
```
#
# Dataset Sources
- [MIND: MIcrosoft News Dataset](https://msnews.github.io/#getting-start).
#
