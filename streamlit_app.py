import streamlit as st
from openai import OpenAI
import docx2txt
import docx
from io import BytesIO

# Show title and description.
st.title("Resume Optimizer")
st.sidebar.title("Configuration")

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.sidebar.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)
    resume_text=""

    st.write("Upload your resume to optimize your resume.")
    uploaded_resume = st.file_uploader("Choose a resume file in pdf or doc")

    if uploaded_resume is not None:
        try:
            if uploaded_resume.name.endswith('.docx') or uploaded_resume.name.endswith('.doc'):
                resume_text = docx2txt.process(uploaded_resume)
            elif uploaded_resume.name.endswith('.pdf'):
                from pdfminer.high_level import extract_text
                resume_text = extract_text(uploaded_resume)
            else:
                st.write("Please upload a PDF or Word document.")
                resume_text = None
            if resume_text:
                print("Successfuly converted resume to markdown")
                #st.write("Resume content (Markdown):")
                #st.text_area("Resume content", value=resume_text, height=300)

        except ImportError:
            st.write("Please install the required libraries (docx2txt, pdfminer.six).")

    ## Job description accept as document or text file
    job_description_text=""
    uploaded_job_description = st.file_uploader("Choose a job description file in pdf or doc")


    if uploaded_job_description is not None:
        try:
            if uploaded_job_description.name.endswith('.docx') or uploaded_job_description.name.endswith('.doc'):
                job_description_text = docx2txt.process(uploaded_job_description)
            elif uploaded_job_description.name.endswith('.pdf'):
                job_description_text = extract_text(uploaded_job_description)
            else:
                st.write("Please upload a PDF or Word document.")
                job_description_text = None
            if job_description_text:
                st.write("Job Description content (Markdown):")
                st.text_area("Job Description content", value=job_description_text, height=300)

        except ImportError:
            st.write("Please install the required libraries (docx2txt, pdfminer.six).")

    job_description_text_input = st.text_area("Or paste job description here:")

    if job_description_text_input:
        job_description_text = job_description_text_input

    prompt = f"""
    I have a resume formatted in Markdown and a job description. \
    Please adapt my resume to better align with the job requirements while \
    maintaining a professional tone. Tailor my skills, experiences, and \
    achievements to highlight the most relevant points for the position. \
    Ensure that my resume still reflects my unique qualifications and strengths \
    but emphasizes the skills and experiences that match the job description.

    ### Here is my resume in Markdown:
    {resume_text}

    ### Here is the job description:
    {job_description_text}

    Please modify the resume to:
    - Use keywords and phrases from the job description.
    - Adjust the bullet points under each role to emphasize relevant skills and achievements.
    - Make sure my experiences are presented in a way that matches the required qualifications.
    - Maintain clarity, conciseness, and professionalism throughout.

    Return the updated resume in Markdown format.

    """
    # make api call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ], 
        temperature = 0.25
    )
        
    # extract response
    resume = response.choices[0].message.content
    st.write("Optimized Resume (Markdown):")
    st.text_area("Optimized Resume", value=resume, height=300)

    #convert markdown to word
    filename="optimized_resume.docx"
    try:
        doc = docx.Document()
        doc.add_paragraph(resume)
        
        # Save the document to a BytesIO object
        file = BytesIO()
        doc.save(file)
        file.seek(0)

        st.download_button(
        label="Download Optimized Resume",
        data=file,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
    except Exception as e:
        st.error(f"An error occurred during conversion: {e}")