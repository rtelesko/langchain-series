from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph


# Defining Header and Footer
def header(canvas):
    canvas.saveState()
    canvas.setFont('Helvetica', 10)
    canvas.drawString(36, A4[1] - 36, "MC Quiz Questions")
    canvas.restoreState()


def footer(canvas, doc):
    now = datetime.now()  # current date and time
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    canvas.saveState()
    canvas.setFont('Helvetica', 10)
    page_number_text = "%d" % doc.page
    canvas.drawString(36, 36, "Released on " + date_time + " Page: " + page_number_text)
    canvas.restoreState()


def _header_footer(canvas, doc):
    # Save the state of our canvas, so we can draw on it
    canvas.saveState()
    # Header
    header(canvas)
    # Footer
    footer(canvas, doc)
    # Release the canvas
    canvas.restoreState()


def create_content(df):
    doc = SimpleDocTemplate("mc_questions.pdf", pagesize=A4)
    # Container for the "Flowable" objects
    elements = ""
    # Loop through the rows using iterrows()
    for index, row in df.iterrows():
        elements += "Question: " + str(index) + "\n"
        elements += row['MCQ'] + "\n"
        elements += "Choices: " + row["Choices"] + "\n"
        elements += "Correct: " + row["Correct"]
        elements += "\n\n"
    elements = elements.replace("|", "")
    doc.build([Paragraph(elements.replace("\n", "<br />"))], onFirstPage=_header_footer, onLaterPages=_header_footer)
