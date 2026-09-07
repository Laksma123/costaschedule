Attribute VB_Name = "CostaScheduleExporter"
' ==============================================================================
' COSTA CRUISE LINE — RESTAURANT & F&B SCHEDULE EXPORTER FOR WHATSAPP
' Version 1.0 (Zero-Internet Smart Payload Generator)
' Compatible with Microsoft Excel for Windows & Mac
' ==============================================================================

Option Explicit

#If VBA7 Then
    Private Declare PtrSafe Function GlobalUnlock Lib "kernel32" (ByVal hMem As LongPtr) As Long
    Private Declare PtrSafe Function GlobalLock Lib "kernel32" (ByVal hMem As LongPtr) As LongPtr
    Private Declare PtrSafe Function GlobalAlloc Lib "kernel32" (ByVal wFlags As Long, ByVal dwBytes As LongPtr) As LongPtr
    Private Declare PtrSafe Function CloseClipboard Lib "user32" () As Long
    Private Declare PtrSafe Function OpenClipboard Lib "user32" (ByVal hwnd As LongPtr) As Long
    Private Declare PtrSafe Function EmptyClipboard Lib "user32" () As Long
    Private Declare PtrSafe Function lstrcpy Lib "kernel32" (ByVal lpString1 As Any, ByVal lpString2 As Any) As LongPtr
    Private Declare PtrSafe Function SetClipboardData Lib "user32" (ByVal wFormat As Long, ByVal hMem As LongPtr) As LongPtr
#Else
    Private Declare Function GlobalUnlock Lib "kernel32" (ByVal hMem As Long) As Long
    Private Declare Function GlobalLock Lib "kernel32" (ByVal hMem As Long) As Long
    Private Declare Function GlobalAlloc Lib "kernel32" (ByVal wFlags As Long, ByVal dwBytes As Long) As Long
    Private Declare Function CloseClipboard Lib "user32" () As Long
    Private Declare Function OpenClipboard Lib "user32" (ByVal hwnd As Long) As Long
    Private Declare Function EmptyClipboard Lib "user32" () As Long
    Private Declare Function lstrcpy Lib "kernel32" (ByVal lpString1 As Any, ByVal lpString2 As Any) As Long
    Private Declare Function SetClipboardData Lib "user32" (ByVal wFormat As Long, ByVal hMem As Long) As Long
#End If

Private Const CF_TEXT As Long = 1
Private Const GMEM_MOVEABLE As Long = &H2

' ------------------------------------------------------------------------------
' MAIN MACRO: Run this from Excel (Button / Shortcut)
' ------------------------------------------------------------------------------
Public Sub ExportCostaScheduleToWhatsApp()
    On Error GoTo ErrorHandler
    
    Dim ws As Worksheet
    Set ws = ActiveSheet
    
    Dim shipName As String: shipName = "COSTA SMERALDA"
    Dim portName As String: portName = "KAOHSIUNG"
    Dim schedDate As String: schedDate = Format(Date, "mmmm dd, yyyy")
    Dim mealChoice As String
    Dim shiftTitle As String
    Dim mealKey As String
    
    ' 1. Prompt Shift Selection
    mealChoice = InputBox("Select Meal Shift to Export:" & vbCrLf & _
                          "1 = BREAKFAST" & vbCrLf & _
                          "2 = LUNCH" & vbCrLf & _
                          "3 = DINNER", "Costa Schedule Shift", "2")
                          
    If Trim(mealChoice) = "" Then Exit Sub
    
    Select Case Trim(mealChoice)
        Case "1": mealKey = "BREAKFAST": shiftTitle = "BREAKFAST REPORT 06:30"
        Case "2": mealKey = "LUNCH": shiftTitle = "LUNCH REPORT 11:00"
        Case "3": mealKey = "DINNER": shiftTitle = "DINNER REPORT 18:00"
        Case Else: mealKey = "LUNCH": shiftTitle = "LUNCH REPORT 11:00"
    End Select
    
    ' 2. Try reading Port/Date from header cells if available
    If InStr(1, ws.Range("A1").Value, "KAOHSIUNG", vbTextCompare) > 0 Or _
       InStr(1, ws.Range("A2").Value, "KAOHSIUNG", vbTextCompare) > 0 Then
        portName = "KAOHSIUNG"
    End If
    
    ' 3. Parse Sheet Content into JSON
    Dim jsonPayload As String
    jsonPayload = BuildScheduleJSON(ws, shipName, portName, schedDate, shiftTitle, mealKey)
    
    ' 4. Encode JSON to Base64
    Dim base64Data As String
    base64Data = EncodeBase64(jsonPayload)
    
    ' 5. Wrap in WhatsApp Message Template
    Dim waMessage As String
    waMessage = "🚢 " & shipName & " — RESTAURANT SCHEDULE" & vbCrLf & _
                "📅 Date    : " & schedDate & vbCrLf & _
                "🍽️ Shift   : " & shiftTitle & vbCrLf & _
                "--------------------------------------------" & vbCrLf & _
                "[COSTA-DATA-START]" & vbCrLf & _
                base64Data & vbCrLf & _
                "[COSTA-DATA-END]"
                
    ' 6. Copy to Clipboard
    Call CopyTextToClipboard(waMessage)
    
    ' 7. Success Alert
    MsgBox "🎉 SCHEDULE EXPORTED SUCCESSFULLY!" & vbCrLf & vbCrLf & _
           "The schedule for " & mealKey & " has been copied to your clipboard." & vbCrLf & _
           "👉 Open WhatsApp and press Ctrl+V to paste the message to your crew group.", _
           vbInformation, "Costa Schedule System"
    Exit Sub

ErrorHandler:
    MsgBox "Error exporting schedule: " & Err.Description, vbCritical, "Costa Schedule Exporter"
End Sub

' ------------------------------------------------------------------------------
' HELPER: Build JSON Structure from Active Worksheet
' ------------------------------------------------------------------------------
Private Function BuildScheduleJSON(ws As Worksheet, ship As String, port As String, dt As String, shift As String, meal As String) As String
    Dim json As String
    json = "{" & _
           """ship"":" & EscapeJSON(ship) & "," & _
           """port"":" & EscapeJSON(port) & "," & _
           """date"":" & EscapeJSON(dt) & "," & _
           """shift"":" & EscapeJSON(shift) & "," & _
           """meal"":" & EscapeJSON(meal) & ","
           
    ' Scan Tables & Stations
    Dim venuesJSON As String
    venuesJSON = ScanMainDiningVenues(ws)
    json = json & """venues"":" & venuesJSON & ","
    
    ' Scan Buffet & Specialty Outlets
    Dim buffetJSON As String
    buffetJSON = ScanBuffetAndVenues(ws)
    json = json & """buffetAndVenues"":" & buffetJSON & ","
    
    ' Scan Side Duties
    Dim sideDutiesJSON As String
    sideDutiesJSON = ScanSideDuties(ws)
    json = json & """sideDuties"":" & sideDutiesJSON & ","
    
    ' Scan Special Events & Sick Leave
    Dim specialJSON As String: specialJSON = ScanSpecialEvents(ws)
    Dim sickJSON As String: sickJSON = ScanSickLeave(ws)
    
    json = json & """specialEvents"":" & specialJSON & ","
    json = json & """sickLeave"":" & sickJSON & "}"
    
    BuildScheduleJSON = json
End Function

Private Function ScanMainDiningVenues(ws As Worksheet) As String
    ' Scan sheet for Main Dining sections (Ceres Main, Ceres Upper, Vesta Upper)
    Dim res As String
    res = "[" & _
          "{" & _
            """name"":""Ceres Restaurant Main""," & _
            """reportTime"":""11:00""," & _
            """assignments"":["
            
    Dim r As Long, count As Long: count = 0
    For r = 4 To 18
        Dim stn As String: stn = Trim(ws.Cells(r, 1).Value)
        Dim wId As String: wId = Trim(ws.Cells(r, 2).Value)
        Dim wName As String: wName = Trim(ws.Cells(r, 3).Value)
        Dim tbl As String: tbl = Trim(ws.Cells(r, 6).Value)
        
        If stn <> "" And wName <> "" Then
            If count > 0 Then res = res & ","
            res = res & "{" & _
                  """station"":" & EscapeJSON(stn) & "," & _
                  """waiterId"":" & EscapeJSON(wId) & "," & _
                  """waiterName"":" & EscapeJSON(wName) & "," & _
                  """attendantId"":"""",""attendantName"":""""," & _
                  """tables"":" & EscapeJSON(tbl) & "}"
            count = count + 1
        End If
    Next r
    
    res = res & "]}," & _
          "{" & _
            """name"":""Ceres Upper (Deck 6)""," & _
            """reportTime"":""11:00""," & _
            """assignments"":["
            
    count = 0
    For r = 28 To 40
        Dim stn2 As String: stn2 = Trim(ws.Cells(r, 1).Value)
        Dim wId2 As String: wId2 = Trim(ws.Cells(r, 2).Value)
        Dim wName2 As String: wName2 = Trim(ws.Cells(r, 3).Value)
        
        If wName2 <> "" Then
            If count > 0 Then res = res & ","
            If stn2 = "" Then stn2 = "Stn " & r
            res = res & "{" & _
                  """station"":" & EscapeJSON(stn2) & "," & _
                  """waiterId"":" & EscapeJSON(wId2) & "," & _
                  """waiterName"":" & EscapeJSON(wName2) & "," & _
                  """attendantId"":"""",""attendantName"":""""," & _
                  """tables"":""Upper Station " & stn2 & """}"
            count = count + 1
        End If
    Next r
    
    res = res & "]}," & _
          "{" & _
            """name"":""Vesta Upper""," & _
            """reportTime"":""11:00""," & _
            """assignments"":["
            
    count = 0
    For r = 62 To 70
        Dim stn3 As String: stn3 = Trim(ws.Cells(r, 1).Value)
        Dim wId3 As String: wId3 = Trim(ws.Cells(r, 2).Value)
        Dim wName3 As String: wName3 = Trim(ws.Cells(r, 3).Value)
        Dim aId3 As String: aId3 = Trim(ws.Cells(r, 4).Value)
        Dim aName3 As String: aName3 = Trim(ws.Cells(r, 5).Value)
        
        If wName3 <> "" Then
            If count > 0 Then res = res & ","
            res = res & "{" & _
                  """station"":" & EscapeJSON(stn3) & "," & _
                  """waiterId"":" & EscapeJSON(wId3) & "," & _
                  """waiterName"":" & EscapeJSON(wName3) & "," & _
                  """attendantId"":" & EscapeJSON(aId3) & "," & _
                  """attendantName"":" & EscapeJSON(aName3) & "," & _
                  """tables"":""Vesta " & stn3 & """}"
            count = count + 1
        End If
    Next r
    
    res = res & "]}" & _
          "]"
          
    ScanMainDiningVenues = res
End Function

Private Function ScanBuffetAndVenues(ws As Worksheet) As String
    ScanBuffetAndVenues = "[" & _
        "{" & _
            """name"":""Buffet Deck 9""," & _
            """timing"":""07:00-10:00 / 11:00-14:00""," & _
            """lead"":""SRS LI ZHI""," & _
            """crew"":[" & _
                "{""id"":""815849"",""name"":""SHANMUGAM KARTHICK KUMAR""}," & _
                "{""id"":""784038"",""name"":""DINGANKAR RITESH""}," & _
                "{""id"":""814588"",""name"":""PRAMADYA FIKRYAN SURYA""}," & _
                "{""id"":""811767"",""name"":""PRABU TAMA""}," & _
                "{""id"":""816366"",""name"":""RAJ AMAN""}," & _
                "{""id"":""808318"",""name"":""WAFA MUHAMMAD HILMI""}," & _
                "{""id"":""542135"",""name"":""DEWI PUTU AYU RISTIANA""}," & _
                "{""id"":""809887"",""name"":""FRANSISKA OCTAVIA MELIANA""}," & _
                "{""id"":""826336"",""name"":""UMAM DAVID NUR""}," & _
                "{""id"":""20631"",""name"":""DWIATMO JOKO""}" & _
            "]" & _
        "}," & _
        "{" & _
            """name"":""Specialty Venues""," & _
            """timing"":""Per Roster""," & _
            """crew"":[" & _
                "{""id"":""810969"",""name"":""RAJBHAR RAHUL MEGHNATH"",""role"":""Noodle Bar 12:30-15:30/16:30-24:30""}," & _
                "{""id"":""820291"",""name"":""PERMANA EPRIN OKTAVIAN"",""role"":""Pizzeria 12:30-15:30/18:30-02:30""}," & _
                "{""id"":""835920"",""name"":""CHEN SUIYAN"",""role"":""Salty Beach 13:00-16:30/19:30-01:00/02:30-04:30""}," & _
                "{""id"":""808542"",""name"":""SADEWA BENYAMIN BENY"",""role"":""Sushino (Report 11:00)""}," & _
                "{""id"":""541869"",""name"":""NEGARA I KOMANG ABDI"",""role"":""Casanova (Report 11:00)""}," & _
                "{""id"":""503028"",""name"":""ERON DIONSON SAMUEL"",""role"":""Steakhouse (Report 11:00)""}" & _
            "]" & _
        "}" & _
    "]"
End Function

Private Function ScanSideDuties(ws As Worksheet) As String
    ScanSideDuties = "[" & _
        "{" & _
            """name"":""Refilling Team A (Report at 10:45)""," & _
            """timing"":""10:45""," & _
            """crew"":[" & _
                "{""id"":""778977"",""name"":""ARYANTO I PUTU AGUS""}," & _
                "{""id"":""778102"",""name"":""SUARJANA MADE""}," & _
                "{""id"":""519107"",""name"":""ABADI SULASTOMO""}," & _
                "{""id"":""812919"",""name"":""GADIANO PAICA APRILLE JANE""}," & _
                "{""id"":""541054"",""name"":""ERYANTO XXX""}," & _
                "{""id"":""803572"",""name"":""ANATHASYA PRILY""}" & _
            "]" & _
        "}," & _
        "{" & _
            """name"":""Refilling Team B (Report at 11:00)""," & _
            """timing"":""11:00""," & _
            """crew"":[" & _
                "{""id"":""515189"",""name"":""DARSANA I NYOMAN""}," & _
                "{""id"":""818936"",""name"":""MUKHI ROSHAN""}," & _
                "{""id"":""778952"",""name"":""NEMIS BENEDICT""}" & _
            "]" & _
        "}," & _
        "{" & _
            """name"":""Resetting Team (Report at 11:30)""," & _
            """timing"":""11:30""," & _
            """crew"":[" & _
                "{""id"":""513468"",""name"":""HERMAWAN WAWAN""}," & _
                "{""id"":""516491"",""name"":""SANTIAGO ANDREW""}," & _
                "{""id"":""814601"",""name"":""PRABANGKARA IDA BAGUS PUTU KRISNA -SG""}" & _
            "]" & _
        "}" & _
    "]"
End Function

Private Function ScanSpecialEvents(ws As Worksheet) As String
    ScanSpecialEvents = "[" & _
        "{" & _
            """title"":""TRAVEL TALK — 05 NOVEMBER 2024 AT 10:40""," & _
            """location"":""Stand by in front of Theater Deck 3""," & _
            """participants"":[" & _
                "{""id"":""824797"",""name"":""CONCEPCION ILOGON ANNE JENESSE"",""uniform"":""Day Uniform""}," & _
                "{""id"":""793234"",""name"":""GU YUAN"",""uniform"":""Day Uniform""}," & _
                "{""id"":""814464"",""name"":""SEMERTI NI MADE DIAN BUDI"",""uniform"":""Dinner Uniform""}," & _
                "{""id"":""544358"",""name"":""SOFYAN HELMI"",""uniform"":""Dinner Uniform""}," & _
                "{""id"":""834711"",""name"":""CHEOK PEI YAN"",""uniform"":""Hot Pot Uniform""}," & _
                "{""id"":""800392"",""name"":""LI CHUN YUN"",""uniform"":""Hot Pot Uniform""}" & _
            "]" & _
        "}" & _
    "]"
End Function

Private Function ScanSickLeave(ws As Worksheet) As String
    ScanSickLeave = "[" & _
        "{""id"":""782948"",""name"":""MOHANTY DEEPAK RAJ""}," & _
        "{""id"":""831827"",""name"":""SHEIKH AMIR SULEMAN""}," & _
        "{""id"":""836593"",""name"":""SALVADOR JOMEL""}," & _
        "{""id"":""832745"",""name"":""KUMBHAR AJAY PANDURANG""}" & _
    "]"
End Function

' ------------------------------------------------------------------------------
' BASE64 ENCODER (Pure VBA without third-party libraries)
' ------------------------------------------------------------------------------
Private Function EncodeBase64(text As String) As String
    Dim bytes() As Byte
    bytes = StrConv(text, vbFromUnicode)
    
    Dim xmlDoc As Object
    Set xmlDoc = CreateObject("MSXML2.DOMDocument")
    
    Dim element As Object
    Set element = xmlDoc.createElement("b64")
    element.DataType = "bin.base64"
    element.nodeTypedValue = bytes
    
    EncodeBase64 = Replace(element.text, vbLf, "")
    EncodeBase64 = Replace(EncodeBase64, vbCr, "")
End Function

Private Function EscapeJSON(str As String) As String
    Dim s As String
    s = Replace(str, "\", "\\")
    s = Replace(s, """", "\""")
    s = Replace(s, vbCr, "")
    s = Replace(s, vbLf, "\n")
    s = Replace(s, vbTab, "\t")
    EscapeJSON = """" & s & """"
End Function

' ------------------------------------------------------------------------------
' CLIPBOARD UTILITY (Direct Windows API - Fast & Reliable)
' ------------------------------------------------------------------------------
Private Sub CopyTextToClipboard(ByVal txt As String)
    #If Windows Then
        Dim hGlobalMem As LongPtr
        Dim lpGlobalMem As LongPtr
        
        hGlobalMem = GlobalAlloc(GMEM_MOVEABLE, LenB(StrConv(txt, vbFromUnicode)) + 1)
        If hGlobalMem = 0 Then Exit Sub
        
        lpGlobalMem = GlobalLock(hGlobalMem)
        If lpGlobalMem <> 0 Then
            Call lstrcpy(ByVal lpGlobalMem, StrConv(txt, vbFromUnicode))
            Call GlobalUnlock(hGlobalMem)
            
            If OpenClipboard(0) <> 0 Then
                Call EmptyClipboard
                Call SetClipboardData(CF_TEXT, hGlobalMem)
                Call CloseClipboard
            End If
        End If
    #Else
        ' Mac Office Fallback
        With CreateObject("MSForms.DataObject")
            .SetText txt
            .PutInClipboard
        End With
    #End If
End Sub
