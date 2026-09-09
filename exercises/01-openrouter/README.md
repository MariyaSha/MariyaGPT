# OpenRouter Example

This mini-project shows how MariyaGPT can connect to an LLM through
OpenRouter.

It demonstrates:

-   connecting to OpenRouter with the OpenAI Python SDK;
-   loading an API key from a `.env` file;
-   selecting an LLM through OpenRouter;
-   sending a prompt to the model;
-   printing the LLM response in the terminal.

## Setup

1.  Open the `.env` file.

2.  Add your OpenRouter API key:

``` env
OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEY
```

3.  Install the dependencies:

``` bash
pip install -r requirements.txt
```

## Run the Exercise

Run:

``` bash
python app.py
```

The application sends the example prompt to the LLM through OpenRouter
and prints the response in the terminal.
