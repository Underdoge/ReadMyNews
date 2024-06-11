# Read My News :newspaper::microphone::speaker:

Today, there is such an abundance of news and information that it is a real challenge to stay up-to-date on the topics that interest us the most. Our project aims to compress this abundance of news and information through a news recommendation system capable of providing this content in a summarized, precise, and easy-to-digest manner, both in easy reading text and voice, and in multiple languages. This way, people with visual impairments can stay informed in an accessible way, thanks to Azure AI Speech's Speech-to-Text and Text-to-Speech services, and the incredible Generative AI of the Azure OpenAI Service.

# Azure AI Resource Creation

1. Create an Azure AI Speech resource on Azure, and obtain its Key and Region from Resource Management > Keys and Endpoints.
2. Create an Azure AI Language resource on Azure, and obtain its Endpoint and Key from Resource Management > Keys and Endpoints.
3. Create an Azure AI Translator resource on Azure, and obtain its Text Translation Endpoint and Key from Resource Management > Keys and Endpoints.
4. Create an Azure OpenAI resource on Azure, and obtain its Key and Endpoint from Resource Management > Keys and Endpoints.
5. Open Azure OpenAI Studio, deploy a new GPT model (3.5 or better recommended), and obtain your model's deployment name, e.g. 'mygpt4modeldeployment'.
6. Choose an Azure OpenAI API version, e.g. "2024-02-01". The available OpenAI API versions can be found [here](https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#chat-completions).
7. After cloning the repository (steps below), rename the provided .env-example file to just '.env', and enter the corresponding values from the previous steps.

# Hosted App

For a very limited time, you can try a hosted version of our Streamlit app, [here](https://readmynews.streamlit.app).

# Installing the App
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
# Dataset Source
- [MIND: MIcrosoft News Dataset](https://msnews.github.io/#getting-start).
#
# Acknowledgements
- We adapted several of the functions from the [Working with functions in Azure OpenAI Jupyter Notebook](https://github.com/Azure-Samples/openai/blob/main/Basic_Samples/Functions/working_with_functions.ipynb) found in the [Azure OpenAI Service Samples](https://github.com/Azure-Samples/openai/) repo.
- We adapted code available in the [mslearn-ai-language](https://github.com/MicrosoftLearning/mslearn-ai-language) repo.
# Responsible AI
- We filter out user input that doesn’t comply with Azure OpenAI’s GPT model’s default content filtering. We recommend using the default content filtering configuration for the GPT model in the Azure OpenAI service, since we find it is apt for the content in the Microsoft News Dataset. [The default content filtering configuration for the GPT model series is set to filter at the medium severity threshold for all four content harm categories (hate, violence, sexual, and self-harm) and applies to both prompts (text, multi-modal text/image) and completions (text). This means that content that is detected at severity level medium or high is filtered, while content detected at severity level low isn't filtered by the content filters.](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/content-filter?tabs=definitions%2Cpython-new#configurability-preview:~:text=The%20default%20content,the%20content%20filters.) Please use [this guide](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/content-filter) to customize content filtering if more strict filtering is required.