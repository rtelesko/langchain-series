from datetime import datetime

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle


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
    elements = []

    # Make heading for each column and start data list
    column1_heading = "Name"
    column2_heading = "Age"
    column3_heading = "Hobby"
    column4_heading = "Profession"

    # Assemble data for each column using simple loop to append it into data list
    # Initialize data of lists
    my_data = {'Name': ['Tom', 'Nick', 'Krish', 'Jack'], 'Age': [20, 21, 19, 18],
               'Hobby': ['Tennis', 'Soccer', 'Golf', 'Badminton'],
               'Profession': ['Developer', 'Manager', 'Assistant', 'Teacher']}

    # Create DataFrame
    df = pd.DataFrame(my_data)

    data = [[column1_heading, column2_heading, column3_heading, column4_heading]]
    for i, row in df.iterrows():
        data.append(list(row))

    table_that_splits_over_pages = Table(data, [4 * cm, 4 * cm, 4 * cm, 4 * cm], repeatRows=1)
    table_that_splits_over_pages.hAlign = 'LEFT'
    tbl_style = TableStyle([('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                            ('LINEBELOW', (0, 0), (-1, -1), 1, colors.black),
                            ('BOX', (0, 0), (-1, -1), 1, colors.black),
                            ('BOX', (0, 0), (0, -1), 1, colors.black),
                            ('BOX', (0, 0), (1, -1), 1, colors.black),
                            ('BOX', (0, 0), (2, -1), 1, colors.black)])
    tbl_style.add('BACKGROUND', (0, 0), (3, 0), colors.lightblue)
    tbl_style.add('BACKGROUND', (0, 1), (-1, -1), colors.white)
    table_that_splits_over_pages.setStyle(tbl_style)
    elements.append(table_that_splits_over_pages)

    doc.build(elements, onFirstPage=_header_footer, onLaterPages=_header_footer)
