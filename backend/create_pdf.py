from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt="PitchIQ Test Document", ln=1, align="C")
pdf.cell(200, 10, txt="This is a dummy pitchbook for testing upload functionality.", ln=2, align="L")
pdf.output("test_pitchbook.pdf")
