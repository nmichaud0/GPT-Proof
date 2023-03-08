# GPT-Proof

## Introduction

GPT-Proof is a Python-based algorithm that generates paraphrases of exam questions and tests them with ChatGPT to restrain students from using ChatGPT during their exams. The main purpose of this repository is to provide academic professors with a tool that helps them ensure exam integrity.

## Features

- Generates multiple paraphrases of exam questions using ChatGPT.
- Tests generated questions with ChatGPT to ensure the originality of questions.
- Provides the option to adjust the amount of creativity required for generating paraphrases.
- Saves all paraphrased questions, answers and marks in JSON files.


## Getting Started

1. Clone the repository using the following command:
```bash 
git clone https://github.com/nmichaud0/GPT-Proof.git
```

2. Install the required packages using the following command:

``` bash
pip install -r requirements.txt
```

3. Modify the variables at the beginning of the GPT_Proofing_V1.py file, such as the API key, the number of paraphrases you want to generate, and the amount of creativity required for generating paraphrases.
4. Get your API key from OpenAI API references.
5. Run the GPT_Proofing_V1.py file and provide the path to your exam questions in an excel format (e.g., example_questions.xlsx).
6. The generated paraphrases, answers, and marks will be saved in a "GPT_Proofing" directory in JSON files, this label can be changed in the code.

## Authors

- Nizar Michaud (username: nmichaud0)

## License

This project is licensed under the MIT License
