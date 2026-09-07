import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
import os

wb = openpyxl.Workbook()

# ==========================================
# SHEET 1: MAIN DINING ROOMS (CERES & VESTA)
# ==========================================
ws1 = wb.active
ws1.title = "Main Dining"

navy_fill = PatternFill(start_color="00224D", end_color="00224D", fill_type="solid")
blue_fill = PatternFill(start_color="00387A", end_color="00387A", fill_type="solid")
light_blue = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
gold_fill = PatternFill(start_color="FDB913", end_color="FDB913", fill_type="solid")
gray_fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
white_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
bold_font = Font(name="Calibri", size=10, bold=True)
regular_font = Font(name="Calibri", size=10)

# Header Row
ws1.merge_cells("A1:F1")
ws1['A1'] = "August 23, 2026"
ws1['A1'].font = white_font
ws1['A1'].fill = blue_fill
ws1['A1'].alignment = Alignment(horizontal="center")

ws1.merge_cells("A2:F2")
ws1['A2'] = "KAOHSIUNG"
ws1['A2'].font = Font(name="Calibri", size=14, bold=True, color="000000")
ws1['A2'].alignment = Alignment(horizontal="center")

ws1.merge_cells("A4:F4")
ws1['A4'] = "LUNCH REPORT 11:00"
ws1['A4'].font = white_font
ws1['A4'].fill = blue_fill
ws1['A4'].alignment = Alignment(horizontal="center")

# Ceres Main Headers
ws1.merge_cells("A5:F5")
ws1['A5'] = "CERES RESTAURANT MAIN"
ws1['A5'].font = bold_font
ws1['A5'].fill = light_blue

headers = ["STN", "ID", "WAITER", "ID", "ATTENDANT", "TABLES"]
for col_num, h in enumerate(headers, 1):
    cell = ws1.cell(row=6, column=col_num, value=h)
    cell.font = bold_font
    cell.fill = gray_fill

ceres_data = [
    (1, "796341", "WIBOWO ANDRI -BS", "", "", "302, 304, 306, 362, 364"),
    (2, "780418", "PUTRA DUWI LAKSANA -BS", "", "", "308, 310, 312, 366, 368"),
    (3, "814624", "SETIOBUDI NIDZAR DICKY -TR -CT", "", "", "314, 316, 370, 372, 374"),
    (4, "821652", "WIJAYA I GEDE ARIK -TR CT", "", "", "318, 320, 322, 324, 344, 346"),
    (5, "812444", "WIDYANTARA I GUSTI NGURAH -TR", "", "", "326, 328, 330, 338, 340, 342"),
    (6, "827541", "HUSEN MUSTAFA AHMAD", "", "", "331, 332, 333, 334, 335, 336, 337"),
    (7, "820751", "ROHMAN FADILI", "", "", "325, 327, 329, 339, 341, 343, 345"),
    (8, "829207", "HAIRUDIN EXDA -CT", "", "", "317, 319, 321, 323, 347, 349"),
    (9, "817116", "SHARMA VICKY CHANDESWAR", "", "", "313, 315, 351, 373, 375, 377"),
    (10, "782718", "HALANKAR SACHIN SHAM -LINEN", "", "", "307, 309, 311, 357, 359"),
    (11, "784016", "THAKUR AKSHAY VISHNU -LINEN", "", "", "301, 303, 305, 365, 367"),
    (12, "835302", "SARMADI KEVIN TEGUH -DIRECTIONE", "", "", "376, 378, 380, 382, 410, 379, 381, 383, 385, 413"),
    (13, "829101", "CAMBA GHIEMER PAUL -CT", "", "", "403, 405, 407, 427"),
    (14, "782852", "JOSHI PREM", "", "", "400, 402, 404, 424")
]

for idx, row in enumerate(ceres_data, 7):
    for c_idx, val in enumerate(row, 1):
        ws1.cell(row=idx, column=c_idx, value=val)

# Ceres Refilling & Resetting Teams
ws1.merge_cells("A21:B21")
ws1['A21'] = "Refilling Team A (Report 10:45)"
ws1['A21'].font = bold_font
ws1['A21'].fill = light_blue

ws1.merge_cells("C21:D21")
ws1['C21'] = "Refilling Team B (Report 11:00)"
ws1['C21'].font = bold_font
ws1['C21'].fill = light_blue

ws1.merge_cells("E21:F21")
ws1['E21'] = "Resetting Team (Report 11:30)"
ws1['E21'].font = bold_font
ws1['E21'].fill = light_blue

refill_a_data = [
    ("778977", "ARYANTO I PUTU AGUS"),
    ("778102", "SUARJANA MADE"),
    ("519107", "ABADI SULASTOMO"),
    ("812919", "GADIANO PAICA APRILLE JANE"),
    ("541054", "ERYANTO XXX"),
    ("803572", "ANATHASYA PRILY")
]

refill_b_data = [
    ("515189", "DARSANA I NYOMAN"),
    ("818936", "MUKHI ROSHAN"),
    ("778952", "NEMIS BENEDICT"),
    ("790215", "FALLADO CARREL")
]

reset_data = [
    ("513468", "HERMAWAN WAWAN"),
    ("516491", "SANTIAGO ANDREW"),
    ("814601", "PRABANGKARA IDA BAGUS PUTU KRISNA -SG")
]

for i in range(max(len(refill_a_data), len(refill_b_data), len(reset_data))):
    r = 22 + i
    if i < len(refill_a_data):
        ws1.cell(row=r, column=1, value=refill_a_data[i][0])
        ws1.cell(row=r, column=2, value=refill_a_data[i][1])
    if i < len(refill_b_data):
        ws1.cell(row=r, column=3, value=refill_b_data[i][0])
        ws1.cell(row=r, column=4, value=refill_b_data[i][1])
    if i < len(reset_data):
        ws1.cell(row=r, column=5, value=reset_data[i][0])
        ws1.cell(row=r, column=6, value=reset_data[i][1])

# Ceres Upper
ws1.merge_cells("A34:F34")
ws1['A34'] = "CERES UPPER (REPORT 11:00)"
ws1['A34'].font = bold_font
ws1['A34'].fill = light_blue

cu_data = [
    ("28", "830813", "RAHI AKASH"),
    ("30", "820951", "SIPAHUTAR DOLY CRISTIAN"),
    ("32", "832123", "DSOUZA RITHESHA"),
    ("34", "832144", "MANNA MANOJ"),
    ("36", "832996", "MALE ASHISH ANTHONY"),
    ("37", "812443", "TEMAJA MADE SINGA"),
    ("39", "817037", "PRABOWO AJI SURYA")
]

for idx, (stn, cid, cname) in enumerate(cu_data, 35):
    ws1.cell(row=idx, column=1, value=stn)
    ws1.cell(row=idx, column=2, value=cid)
    ws1.cell(row=idx, column=3, value=cname)

# Vesta Upper
ws1.merge_cells("A43:F43")
ws1['A43'] = "VESTA UPPER (REPORT 11:00)"
ws1['A43'].font = bold_font
ws1['A43'].fill = light_blue

vu_data = [
    ("62", "794527", "SUSILA PUTU PANDE", "829242", "WARDANA WAYAN ADI WISNU"),
    ("63", "795035", "LAUAN MARY", "820216", "SATYAMA I KADEK"),
    ("64", "782745", "RAMESH KUMAR", "830770", "THAPA SAURABH"),
    ("65", "825675", "KARMAKAR SUDIP", "812619", "RAFLI RIFKI -TR"),
    ("66", "817003", "KALE SAGAR", "827336", "PRADHAN SAYANTA RABIN"),
    ("67", "541734", "DARMAWAN I GUSTI PUTU ERI -CC", "834952", "LAZAGA MARIA"),
    ("68", "810579", "KUMAR ABHIJEET", "826477", "WASIUN MOHAMMAD ROHIB"),
    ("69", "796889", "INDRAWAN SALEH ARIF", "832950", "CATINDIG MATAWARAN HEIDEE"),
    ("70", "821748", "PRAWIRA EDWIN -BS", "830793", "ALPHONSO MICHAEL PAUL")
]

for idx, (stn, wid, wname, aid, aname) in enumerate(vu_data, 44):
    ws1.cell(row=idx, column=1, value=stn)
    ws1.cell(row=idx, column=2, value=wid)
    ws1.cell(row=idx, column=3, value=wname)
    ws1.cell(row=idx, column=4, value=aid)
    ws1.cell(row=idx, column=5, value=aname)

# ==========================================
# SHEET 2: BUFFET & ALL SIDE DUTIES (DRS, OUTLETS, ETC.)
# ==========================================
ws2 = wb.create_sheet(title="Buffet & Side Duties")

ws2.merge_cells("A1:F1")
ws2['A1'] = "August 23, 2026"
ws2['A1'].font = white_font
ws2['A1'].fill = blue_fill
ws2['A1'].alignment = Alignment(horizontal="center")

ws2.merge_cells("A2:F2")
ws2['A2'] = "KAOHSIUNG"
ws2['A2'].font = Font(name="Calibri", size=14, bold=True)
ws2['A2'].alignment = Alignment(horizontal="center")

ws2.merge_cells("A3:F3")
ws2['A3'] = "PLEASE CHECK BUFFET SCHEDULE (32 CREW)"
ws2['A3'].font = bold_font
ws2['A3'].fill = light_blue
ws2['A3'].alignment = Alignment(horizontal="center")

buffet_grid = [
    ("815849", "SHANMUGAM KARTHICK KUMAR", "784038", "DINGANKAR RITESH", "814588", "PRAMADYA FIKRYAN SURYA"),
    ("811767", "PRABU TAMA", "816366", "RAJ AMAN", "808318", "WAFA MUHAMMAD HILMI"),
    ("542135", "DEWI PUTU AYU RISTIANA", "809887", "FRANSISKA OCTAVIA MELIANA", "826336", "UMAM DAVID NUR"),
    ("20631", "DWIATMO JOKO", "801865", "YULIASTUTI EKA", "827493", "KESUMA SANG NYOMAN ARDIKA"),
    ("22426", "JAMALUDDIN XXX", "812457", "SETIAWAN MUKLIS", "808309", "WIDIARTA I PUTU HENDRA"),
    ("813364", "MUMAR BALONGA ZISKA", "802034", "CARDOZO BENZY FRANKLLIN", "829296", "BITUIN JOHN HOWEN"),
    ("542122", "ARTHA WIGUNA GEDE KOMANG", "803805", "GEORGE PETER SEBASTIAN", "832137", "SHAHI VIKRANT"),
    ("541974", "SAPUTRA I WAYAN SUMADI ADI", "798218", "SHAABAN ALI", "820210", "SEJATI MUHAMMAD AGUS WAHYU"),
    ("808132", "SOMBILON TACANG SHEENA LOU", "812681", "FLORES LENNY JOY", "823542", "TOGNI JUDY ANN"),
    ("802859", "NANDA JUILTA ARIA", "824664", "JASMINE IVANA", "", "")
]

for idx, row in enumerate(buffet_grid, 4):
    for c_idx, val in enumerate(row, 1):
        ws2.cell(row=idx, column=c_idx, value=val)

# Row 15: Office Disposition & Reservation & Vesta Upper Door
ws2.merge_cells("A15:B15")
ws2['A15'] = "OFFICE DISPOSITION 07:00-13:00"
ws2['A15'].font = bold_font
ws2['A15'].fill = light_blue

ws2.merge_cells("C15:D15")
ws2['C15'] = "RESERVATION CALL"
ws2['C15'].font = bold_font
ws2['C15'].fill = light_blue

ws2.merge_cells("E15:F15")
ws2['E15'] = "VESTA UPPER BY THE DOOR 11:00"
ws2['E15'].font = bold_font
ws2['E15'].fill = light_blue

ws2['A16'] = "824977"; ws2['B16'] = "RAMOS LESLIE"
ws2['C16'] = "805134"; ws2['D16'] = "LU YANLING"
ws2['E16'] = "811770"; ws2['F16'] = "ANTARI NI WAYAN DESI -FRONT"

ws2['A17'] = "813414"; ws2['B17'] = "JUANILLO USOG MAE RUSELLE -HANDOVER RECEIVER"

# Row 18: DRS 07:00-13:00 (RAMANDA LAKSMANA DIAN) & VESTA LOWER DOOR
ws2.merge_cells("A18:D18")
ws2['A18'] = "DRS 07:00-13:00"
ws2['A18'].font = bold_font
ws2['A18'].fill = light_blue

ws2.merge_cells("E18:F18")
ws2['E18'] = "VESTA LOWER BY THE DOOR 11:15-14:15"
ws2['E18'].font = bold_font
ws2['E18'].fill = light_blue

ws2['A19'] = "796336"; ws2['B19'] = "RAMANDA LAKSMANA DIAN"
ws2['E19'] = "805134"; ws2['F19'] = "LU YANLING -FRONT"

# Outlets: Noodle Bar, Pizzeria, Salty Beach
ws2.merge_cells("A20:B20")
ws2['A20'] = "NOODLE BAR 12:30-15:30/16:30-24:30"
ws2['A20'].font = bold_font
ws2['A20'].fill = light_blue

ws2.merge_cells("C20:D20")
ws2['C20'] = "PIZZERIA, REPORT TO SRM SUDHIR"
ws2['C20'].font = bold_font
ws2['C20'].fill = light_blue

ws2.merge_cells("E20:F20")
ws2['E20'] = "SALTY BEACH"
ws2['E20'].font = bold_font
ws2['E20'].fill = light_blue

ws2['A21'] = "810969"; ws2['B21'] = "RAJBHAR RAHUL MEGHNATH"
ws2['C21'] = "820291"; ws2['D21'] = "PERMANA EPRIN OKTAVIAN 12:30-15:30 /18:30-02:30"
ws2['E21'] = "835920"; ws2['F21'] = "CHEN SUIYAN 13:00-16:30/19:30-01:00/02:30-04:30"

ws2['C22'] = "821124"; ws2['D22'] = "CHHETRI SHUBHAM 12:15-15:15/18:15-02:15"
ws2['E22'] = "812629"; ws2['F22'] = "WIJAYA KETUT PUTRA 17:00-19:30/20:30-02:30/04:00-06:30"

ws2['C23'] = "830141"; ws2['D23'] = "BHADALE SIDDHANT 12:30-15:30 /18:30-02:30"

# Linen Incharge
ws2.merge_cells("A24:B24")
ws2['A24'] = "LINEN INCHARGE REPORT AT 08:00-14:00"
ws2['A24'].font = bold_font
ws2['A24'].fill = light_blue

ws2['A25'] = "796337"; ws2['B25'] = "DJODI ACHMAD SETIA"

# Cleaning & Buffet Deck 9 Report
ws2.merge_cells("A26:B26")
ws2['A26'] = "CLEANING AFTER BREAKFAST 13:00"
ws2['A26'].font = bold_font
ws2['A26'].fill = light_blue

ws2.merge_cells("C26:F26")
ws2['C26'] = "REPORT BUFFET DECK 9 WITH SRS LI ZHI AT 07:00-10:00 / 11:00-14:00"
ws2['C26'].font = bold_font
ws2['C26'].fill = light_blue

ws2['A27'] = "810948"; ws2['B27'] = "BURHANUDIN MUHAMAD RIZKI -CT"
ws2['C27'] = "801795"; ws2['D27'] = "PRATAMA WILY -DECK 3 FWD ELEVATOR & LOBBY"
ws2['E27'] = "804098"; ws2['F27'] = "NUGRAHA PUTU WIRA - DECK 3 CERES & LOUNGES"

ws2['A28'] = "827569"; ws2['B28'] = "PUTRA ERICHO ALLAM FAQIHSYAH -CT"
ws2['C28'] = "788204"; ws2['D28'] = "ENDANG SAHIDIN -DECK 5 ALL LOUNGES"
ws2['E28'] = "811986"; ws2['F28'] = "ASEO GLADY'S -BUFFET DECK 9"

ws2['A29'] = "824440"; ws2['B29'] = "SETIAWAN HERU -CT"

# Magazinero, Folding Napkin, Crew Mess
ws2.merge_cells("A30:B30")
ws2['A30'] = "MAGAZINERO REPORT AT 08:00-14:00"
ws2['A30'].font = bold_font
ws2['A30'].fill = light_blue

ws2.merge_cells("C30:D30")
ws2['C30'] = "FOLDING NAPKIN DECK 10"
ws2['C30'].font = bold_font
ws2['C30'].fill = light_blue

ws2.merge_cells("E30:F30")
ws2['E30'] = "CHECK CREW MESS SCHEDULE"
ws2['E30'].font = bold_font
ws2['E30'].fill = light_blue

ws2['A31'] = "808882"; ws2['B31'] = "BAPTISTA WILSON AUSTIN"
ws2['C31'] = "809147"; ws2['D31'] = "KRENDANA ANGGRA -07:00-10:00/11:00-14:00"
ws2['E31'] = "834885"; ws2['F31'] = "DSOUZA YORICK ROQUE JOHNSON"

ws2['A32'] = "791481"; ws2['B32'] = "SYAMSI KHAERUL"
ws2['C32'] = "820320"; ws2['D32'] = "HIDAYAH SHOHIBUL -07:00-10:00/11:00-14:00"
ws2['E32'] = "833055"; ws2['F32'] = "XXX EI EI HTAR"

ws2['E33'] = "837082"; ws2['F33'] = "XXX CHIT KO KO ZAW"

# Specialties: Sushino, Casanova, Steakhouse
ws2.merge_cells("A34:B34")
ws2['A34'] = "SUSHINO REPORT AT 11:00"
ws2['A34'].font = bold_font
ws2['A34'].fill = light_blue

ws2.merge_cells("C34:D34")
ws2['C34'] = "CASANOVA REPORT AT 11:00"
ws2['C34'].font = bold_font
ws2['C34'].fill = light_blue

ws2.merge_cells("E34:F34")
ws2['E34'] = "STEAKHOUSE REPORT AT 11:00"
ws2['E34'].font = bold_font
ws2['E34'].fill = light_blue

ws2['A35'] = "808542"; ws2['B35'] = "SADEWA BENYAMIN BENY"
ws2['C35'] = "541869"; ws2['D35'] = "NEGARA I KOMANG ABDI"
ws2['E35'] = "503028"; ws2['F35'] = "ERON DIONSON SAMUEL"

ws2['A36'] = "823907"; ws2['B36'] = "MUYCO VILLA ABRILLE JAN CLOYDE"
ws2['E36'] = "827318"; ws2['F36'] = "MAHENDRA PRATAMA I PUTU GEDE DEVA"

# Hot Pot Team & Sick Leave
ws2.merge_cells("A37:B37")
ws2['A37'] = "HOT POT TEAM REPORT 10:00-14:00"
ws2['A37'].font = bold_font
ws2['A37'].fill = light_blue

ws2.merge_cells("C37:F37")
ws2['C37'] = "SICK LEAVE PERSONNEL"
ws2['C37'].font = bold_font
ws2['C37'].fill = light_blue

ws2['A38'] = "801227"; ws2['B38'] = "GENG YANAN -SELLING HOTPOT AREA"
ws2['C38'] = "782948"; ws2['D38'] = "MOHANTY DEEPAK RAJ"

ws2['A39'] = "540938"; ws2['B39'] = "DEGUNE JASPAL -SELLING HOTPOT AREA"
ws2['C39'] = "831827"; ws2['D39'] = "SHEIKH AMIR SULEMAN"

ws2['A40'] = "823334"; ws2['B40'] = "KURNIA TEGAR"
ws2['C40'] = "836593"; ws2['D40'] = "SALVADOR JOMEL"

ws2['A41'] = "818339"; ws2['B41'] = "PANGESTU PANJI FAJAR"
ws2['C41'] = "832745"; ws2['D41'] = "KUMBHAR AJAY PANDURANG"

# Save file
out_path = "/Users/dianjulie/Documents/Schedule Costa/sample/Costa_Serena_Schedule_Sample.xlsx"
wb.save(out_path)
print(f"Generated complete 2-sheet Excel schedule with DRS (Ramanda Laksmana Dian): {out_path}")
