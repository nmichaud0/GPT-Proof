import openai
import pandas as pd
import os
import string
import json

FILE_PATH = 'example_questions.xlsx'

KEY = 'YOUR_API_KEY'
openai.api_key = KEY

N_VARIATIONS = 5  # Number of variations of the question to be asked
N_BEFORE_CREATIVE = 3  # Number of variations before the model will increase the level of creativity
OUTPUT_DIRECTORY = 'GPT_Proofing'
REMOVE_OUTPUT_DIR_CONTENT = True

if not os.path.exists(OUTPUT_DIRECTORY):
    os.mkdir(OUTPUT_DIRECTORY)

if REMOVE_OUTPUT_DIR_CONTENT:
    for file in os.listdir(OUTPUT_DIRECTORY):
        os.remove(os.path.join(OUTPUT_DIRECTORY, file))


PROMPTS = {
    'Paraphrase questions':
        f"For the following sentence, you'll be asked to paraphrase it {N_VARIATIONS} times in the same language as the"
        f" sentence is given to you. Once you have given {N_BEFORE_CREATIVE} sentences, you will increase your level of"
        f" creativity for the next {N_BEFORE_CREATIVE} and so on. Only list the paraphrased sentences with one blank "
        f"line between each sentence, without repeating or answering anything else. Here is the sentence you will"
        f" paraphrase:",

    'Test answer':
        "A question has been asked to a student. You'll be given the original question, the student's answer and the "
        "valid answer. The grade is based on a scale of 10. If the student completely failed the question mark it 0, if"
        "the student completely passed the question mark it 10. The more the student's answer is far from the valid"
        "answer the more points will be lost. Respond with a number between 0 to 10 and absolutely nothing else than"
        " one of these numbers!"
}

test_answer = lambda question_, student_answer, valid_answer: f"{PROMPTS['Test answer']}\n" \
                                                              f"Question: {question_}\n" \
                                                              f"Student's answer: {student_answer}\n" \
                                                              f"Valid answer: {valid_answer}"

listing_paraphrases = lambda x: [i for i in x.split('\n') if len(i) > 3]


def get_response(messages_):

    if not isinstance(messages_, list):
        messages_ = [messages_]

    model = openai.ChatCompletion()
    model_to_use = 'gpt-3.5-turbo'
    return model.create(model=model_to_use, messages=messages_)['choices'][0]['message']['content']


def get_message(prompt, sub_prompt=''):

    return {'role': 'user', 'content': prompt + '\n' + sub_prompt if sub_prompt else prompt}


def json_per_question(questions_: list, answers_: list, marks: list):

    assert len(questions_) == len(answers_) == len(marks)

    json_ = {}

    for q, a, m in zip(questions_, answers_, marks):

        json_[q] = {'answer': a, 'mark': m}

    return json_


def full_pipe(question_: str, valid_answer_: str):

    gpt_answer_ = get_response(get_message(question_))
    gpt_mark_ = get_response(get_message(test_answer(question_=question_,
                                                     student_answer=gpt_answer_,
                                                     valid_answer=valid_answer_)))

    return gpt_answer_, gpt_mark_


remove_char = lambda x, char: x.replace(char, '')


def clean_string(string_):

    trash_char = [j for j in string_ if j not in string.ascii_letters]
    
    for char in trash_char:
        string_ = remove_char(string_, char)

    return string_


df = pd.read_excel(FILE_PATH)
columns = list(df.columns)

assert columns == ['question', 'answer']

dic = dict(zip(df[columns[0]], df[columns[1]]))

LOOP = True

if LOOP:

    for question, answer in dic.items():

        # Get GPT answer for Original question
        OG_gpt_answer, OG_gpt_mark = full_pipe(question, answer)

        frame = {'Original_question': question, 'Original_answer': answer,
                 'Original_GPT_answer': OG_gpt_answer, 'Original_GPT_mark': OG_gpt_mark,
                 'Paraphrasing': []}

        # Paraphrases generation
        paraphrases_message = get_message(PROMPTS['Paraphrase questions'], question)

        paraphrases = listing_paraphrases(get_response([paraphrases_message]))

        # Empty dataframe to store the results
        df_paraphrases = pd.DataFrame(columns=['Paraphrase', 'GPT_answer', 'GPT_mark'])

        for paraphrase in paraphrases:

            gpt_answer, gpt_mark = full_pipe(paraphrase, answer)

            # Store the results in df_paraphrases
            df_paraphrases = df_paraphrases.append({'Paraphrase': paraphrase,
                                                    'GPT_answer': gpt_answer,
                                                    'GPT_mark': gpt_mark}, ignore_index=True)

        # Order dataframe ascending by GPT_mark
        df_paraphrases = df_paraphrases.sort_values(by='GPT_mark', ascending=True)

        # Store the results in frame
        for i in range(len(df_paraphrases)):

            frame['Paraphrasing'].append({'Paraphrase': df_paraphrases['Paraphrase'][i],
                                        'GPT_answer': df_paraphrases['GPT_answer'][i],
                                        'GPT_mark': df_paraphrases['GPT_mark'][i]})

        json_question_file_name = clean_string(question) + '.json'

        # Output frame to json file
        with open(os.path.join(OUTPUT_DIRECTORY, json_question_file_name), 'w') as f:
            json.dump(frame, f)
