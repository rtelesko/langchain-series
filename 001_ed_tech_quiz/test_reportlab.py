from datetime import datetime

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle


# Defining Header and Footer
def header(canvas, doc):
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
    # Save the state of our canvas so we can draw on it
    canvas.saveState()
    styles = getSampleStyleSheet()

    # Header
    header(canvas, doc)

    # Footer
    footer(canvas, doc)
    # Release the canvas
    canvas.restoreState()


pdfReportPages = "mc_questions.pdf"
doc = SimpleDocTemplate(pdfReportPages, pagesize=A4)

# container for the "Flowable" objects
elements = []
styles = getSampleStyleSheet()
styleN = styles["Normal"]

# Make heading for each column and start data list
column1Heading = "Name"
column2Heading = "Age"
column3Heading = "Hobby"
column4Heading = "Profession"
# Assemble data for each column using simple loop to append it into data list
# intialise data of lists.
my_data = {'Name': ['Tom', 'Nick', 'Krish', 'Jack'], 'Age': [20, 21, 19, 18],
           'Hobby': ['Tennis', 'Soccer', 'Golf', 'Badminton'],
           'Profession': ['Developer', 'Manager', 'Assistant', 'Teacher']}

# Create DataFrame
df = pd.DataFrame(my_data)

data = [[column1Heading, column2Heading, column3Heading, column4Heading]]
for i, row in df.iterrows():
    data.append(list(row))

tableThatSplitsOverPages = Table(data, [4 * cm, 4 * cm, 4 * cm, 4 * cm], repeatRows=1)
tableThatSplitsOverPages.hAlign = 'LEFT'
tblStyle = TableStyle([('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                       ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                       ('LINEBELOW', (0, 0), (-1, -1), 1, colors.black),
                       ('BOX', (0, 0), (-1, -1), 1, colors.black),
                       ('BOX', (0, 0), (0, -1), 1, colors.black),
                       ('BOX', (0, 0), (1, -1), 1, colors.black),
                       ('BOX', (0, 0), (2, -1), 1, colors.black)])
tblStyle.add('BACKGROUND', (0, 0), (3, 0), colors.lightblue)
tblStyle.add('BACKGROUND', (0, 1), (-1, -1), colors.white)
tableThatSplitsOverPages.setStyle(tblStyle)
elements.append(tableThatSplitsOverPages)

doc.build(elements, onFirstPage=_header_footer, onLaterPages=_header_footer)
