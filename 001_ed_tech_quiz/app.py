import json
from PIL import Image

from dotenv import load_dotenv
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains import SequentialChain
from langchain.callbacks import get_openai_callback
import streamlit as st
import traceback
import pandas as pd
import imgkit

from utils import parse_file, get_table_data, create_pdf_from_dataframe, RESPONSE_JSON

import dataframe_image as dfi

# Load OpenAI API_KEY
load_dotenv()

# This is an LLMChain to create 10-20 multiple choice questions from a given piece of text.
llm = OpenAI(model_name="gpt-3.5-turbo", temperature=0, max_tokens=-1)

template = """
Text: {text}
You are an expert MCQ maker. Given the above text, it is your job to\
create a quiz of {number} multiple choice questions with a {level} level of difficulty in {tone} tone.
Make sure that questions are not repeated and check all the questions to be conforming to the text as well.
Make sure to format your response like the RESPONSE_JSON below and use it as a guide.\
Ensure to make the {number} MCQs.
### RESPONSE_JSON
{response_json}
"""
quiz_generation_prompt = PromptTemplate(
    input_variables=["text", "number", "level", "tone", "response_json"],
    template=template,
)
quiz_chain = LLMChain(
    llm=llm, prompt=quiz_generation_prompt, output_key="quiz", verbose=True
)

# This is an LLMChain to evaluate the multiple choice questions created by the above chain
llm = OpenAI(model_name="gpt-3.5-turbo", temperature=0)
template = """You are an expert english grammarian and writer. Given a multiple choice quiz with a {level} level of difficulty.\
You need to evaluate complexity of the questions and give a complete analysis of the quiz if the students 
will be able to understand the questions and answer them. Only use at max 50 words for complexity analysis.
If quiz is not at par with the cognitive and analytical abilities of the students,\
update the quiz questions which need to be changed and change the tone such that it perfectly fits the students abilities. 
Quiz MCQs:
{quiz}
Critique from an expert english writer of the above quiz:"""

quiz_evaluation_prompt = PromptTemplate(
    input_variables=["level", "quiz"], template=template
)
review_chain = LLMChain(
    llm=llm, prompt=quiz_evaluation_prompt, output_key="review", verbose=True
)

# This is the overall chain where we run these two chains in sequence.
generate_evaluate_chain = SequentialChain(
    chains=[quiz_chain, review_chain],
    input_variables=["text", "number", "level", "tone", "response_json"],
    # Here we return multiple variables
    output_variables=["quiz", "review"],
    verbose=True,
)

st.markdown("<h1 style='text-align: center; color: red;'>Quiz Generation for Educational Content</h1>",
            unsafe_allow_html=True)
st.balloons()
col1, col2, col3 = st.columns(3)
with col1:
    st.write(' ')
with col2:
    image = Image.open('img/quiz.jpg')
    st.image(image)
with col3:
    st.write(' ')

# Create a form using st.form
with st.form("user_inputs"):
    # File upload
    uploaded_files = st.file_uploader("Upload one or more pdf or text files", accept_multiple_files=True)

    # Input fields
    mcq_count = st.number_input("Number of MCQ", min_value=3, max_value=20)
    level = st.radio(label="Select applicable level of difficulty", options=["easy", "medium", "complex"])
    tone = st.radio(label="Select applicable tone for the quiz",
                    options=["formal", "informal", "friendly", "professional"])
    button = st.form_submit_button("Create quiz")

# Check if the button is clicked and all fields have inputs
if button and uploaded_files is not None and mcq_count and level and tone:

    # Create a list to store the uploaded file names
    file_list = []
    st.write("Uploaded Files:")
    for uploaded_file in uploaded_files:
        if uploaded_file is not None:
            # Append the name of the uploaded file to the file_list
            file_list.append(uploaded_file)
            st.markdown("- " + uploaded_file.name)

    with st.spinner("Loading..."):
        try:
            text = ""
            for uploaded_file in uploaded_files:
                text += parse_file(uploaded_file)

            # count tokens and cost of api call
            with get_openai_callback() as cb:
                response = generate_evaluate_chain(
                    {
                        "text": text,
                        "number": mcq_count,
                        "level": level,
                        "tone": tone,
                        "response_json": json.dumps(RESPONSE_JSON),
                    }
                )
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            st.error("Error: " + str(e))
        else:
            print(f"Total Tokens: {cb.total_tokens}")
            print(f"Prompt Tokens: {cb.prompt_tokens}")
            print(f"Completion Tokens: {cb.completion_tokens}")
            print(f"Total Cost (USD): ${cb.total_cost}")

            if isinstance(response, dict):
                # Extract quiz data from the response
                quiz = response.get("quiz", None)
                if quiz is not None:
                    table_data = get_table_data(quiz)
                    if table_data is not None:
                        df = pd.DataFrame(table_data)
                        df.index = df.index + 1
                        st.table(df)
                        # Display the review in a text box
                        st.text_area(label="Review", value=response["review"])
                        # Save results in a PDF file
                        create_pdf_from_dataframe(df)
                    else:
                        st.error("Error in table data")

            else:
                st.write(response)
