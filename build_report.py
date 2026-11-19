from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Ellipse
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path(__file__).resolve().parent; DOCS=ROOT/'docs'; DOCS.mkdir(exist_ok=True)

def diagram(name,title,nodes,edges,vertical=False):
    fig,ax=plt.subplots(figsize=(11,6.2));ax.set_xlim(0,12);ax.set_ylim(0,8);ax.axis('off');ax.set_title(title,fontsize=16,fontweight='bold',pad=18,color='#173d2b')
    pos={k:(x,y) for k,x,y in nodes}
    for k,x,y in nodes:
        w=2.1;h=.72
        patch=FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=0.12,rounding_size=0.12',fc='#e9f4ed',ec='#26734d',lw=1.5)
        ax.add_patch(patch);ax.text(x,y,k,ha='center',va='center',fontsize=9,color='#173d2b',wrap=True)
    for a,b,label in edges:
        x1,y1=pos[a];x2,y2=pos[b]
        ar=FancyArrowPatch((x1,y1-.42 if y2<y1 else y1+.42),(x2,y2+.42 if y2<y1 else y2-.42),arrowstyle='-|>',mutation_scale=13,color='#66776c',lw=1.2,connectionstyle='arc3,rad=0.05')
        ax.add_patch(ar)
        if label: ax.text((x1+x2)/2,(y1+y2)/2+.12,label,ha='center',fontsize=8,color='#56665c',bbox=dict(fc='white',ec='none',alpha=.8))
    fig.tight_layout();fig.savefig(DOCS/name,dpi=180,bbox_inches='tight');plt.close(fig)

diagram('use_case.png','USE CASE DIAGRAM — WORKFORCEOS',[
('Employee',1.5,6.6),('Manager',1.5,4.3),('Admin',1.5,2.0),('View own shifts',5,7),('Submit timesheet',5,5.9),('Submit expense',5,4.8),('Review timesheets',8.8,5.8),('Approve / reject expenses',8.8,4.5),('Schedule shifts',8.8,3.2),('Manage employees',8.8,1.9),('View dashboard & reports',5,1.3)],
[('Employee','View own shifts',''),('Employee','Submit timesheet',''),('Employee','Submit expense',''),('Manager','Review timesheets',''),('Manager','Approve / reject expenses',''),('Manager','Schedule shifts',''),('Admin','Manage employees',''),('Admin','Schedule shifts',''),('Admin','View dashboard & reports',''),('Manager','View dashboard & reports',''),('Employee','View dashboard & reports','')])
diagram('activity.png','ACTIVITY DIAGRAM — TIMESHEET SUBMISSION & APPROVAL',[
('Start',1.2,6.8),('Employee logs in',3.5,6.8),('Open timesheets',6,6.8),('Enter date, clock times & break',9.5,6.8),('Validate input',9.5,5.1),('Submit record',6.5,5.1),('Manager reviews',3.5,5.1),('Approve?',1.4,3.2),('Mark approved',4,2.1),('Return for correction / reject',8,2.1),('Update dashboard',6,0.7),('End',10,0.7)],
[('Start','Employee logs in',''),('Employee logs in','Open timesheets',''),('Open timesheets','Enter date, clock times & break',''),('Enter date, clock times & break','Validate input',''),('Validate input','Submit record','Valid'),('Submit record','Manager reviews',''),('Manager reviews','Approve?',''),('Approve?','Mark approved','Yes'),('Approve?','Return for correction / reject','No'),('Mark approved','Update dashboard',''),('Return for correction / reject','Update dashboard',''),('Update dashboard','End','')])
diagram('sequence.png','SEQUENCE DIAGRAM — EXPENSE CLAIM APPROVAL',[
('Employee',1.2,6.7),('Browser UI',3.5,6.7),('HTTP API',6,6.7),('SQLite DB',9,6.7),('Manager UI',3.5,2.0),('Review API',6,2.0),('Status saved',9,2.0)],
[('Employee','Browser UI','1. Enter claim'),('Browser UI','HTTP API','2. POST /api/expenses'),('HTTP API','SQLite DB','3. INSERT pending'),('SQLite DB','HTTP API','4. Return success'),('HTTP API','Browser UI','5. Show confirmation'),('Manager UI','Review API','6. PATCH status'),('Review API','SQLite DB','7. UPDATE status'),('SQLite DB','Status saved','8. Commit')])
diagram('architecture.png','SYSTEM ARCHITECTURE — THREE-LAYER VIEW',[
('Presentation layer\nHTML · CSS · JavaScript',2.0,6),('HTTP application layer\nPython standard library',6,6),('Business logic\nValidation · approvals · calculations',10,6),('Data access layer\nSQLite queries',6,3.5),('Database layer\nEmployees · Shifts · Timesheets · Expenses',6,1)],
[('Presentation layer\nHTML · CSS · JavaScript','HTTP application layer\nPython standard library','HTTP / JSON'),('HTTP application layer\nPython standard library','Business logic\nValidation · approvals · calculations','Route request'),('Business logic\nValidation · approvals · calculations','Data access layer\nSQLite queries','Read / write'),('Data access layer\nSQLite queries','Database layer\nEmployees · Shifts · Timesheets · Expenses','SQL')])
diagram('er_diagram.png','ENTITY RELATIONSHIP DIAGRAM — WORKFORCEOS',[
('EMPLOYEE\nPK employee_id\nname, email, role',2,6),('SHIFT\nPK shift_id\nFK employee_id\ndate, start, end',6,6),('TIMESHEET\nPK timesheet_id\nFK employee_id\nhours, status',10,6),('EXPENSE\nPK expense_id\nFK employee_id\namount, category',6,2)],
[('EMPLOYEE\nPK employee_id\nname, email, role','SHIFT\nPK shift_id\nFK employee_id\ndate, start, end','1 : many'),('EMPLOYEE\nPK employee_id\nname, email, role','TIMESHEET\nPK timesheet_id\nFK employee_id\nhours, status','1 : many'),('EMPLOYEE\nPK employee_id\nname, email, role','EXPENSE\nPK expense_id\nFK employee_id\namount, category','1 : many')])

D=Document(); sec=D.sections[0];sec.top_margin=Inches(.7);sec.bottom_margin=Inches(.65);sec.left_margin=Inches(.8);sec.right_margin=Inches(.8)
styles=D.styles;styles['Normal'].font.name='Aptos';styles['Normal'].font.size=Pt(10);styles['Normal'].paragraph_format.space_after=Pt(6)
for sty,size,col in [('Title',26,'174D35'),('Heading 1',17,'174D35'),('Heading 2',13,'26734D'),('Heading 3',11,'26734D')]:
 s=styles[sty];s.font.name='Aptos Display';s.font.size=Pt(size);s.font.bold=True;s.font.color.rgb=RGBColor.from_string(col)
# header/footer
header=sec.header.paragraphs[0];header.text='GROUP 10  |  WORKFORCEOS';header.alignment=WD_ALIGN_PARAGRAPH.RIGHT
for r in header.runs:r.font.size=Pt(8);r.font.color.rgb=RGBColor(100,120,108)
footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
run=footer.add_run('Workforce Shift, Timesheet & Expense Reconciliation System  |  Page ');run.font.size=Pt(8)
fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');footer._p.append(fld)
def para(text='',bold=False,align=None):
 p=D.add_paragraph();p.alignment=align
 r=p.add_run(text);r.bold=bold;return p
def bullet(text):D.add_paragraph(text,style='List Bullet')
def numbered(text):D.add_paragraph(text,style='List Number')
def heading(text,level=1):D.add_heading(text,level=level)
def page():D.add_page_break()
def table(headers,rows):
 t=D.add_table(rows=1, cols=len(headers));t.style='Light Shading Accent 1'
 for i,h in enumerate(headers):t.rows[0].cells[i].text=h
 for row in rows:
  cells=t.add_row().cells
  for i,v in enumerate(row):cells[i].text=str(v)
 return t
def img(file,width=6.4):
 p=D.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.add_run().add_picture(str(DOCS/file),width=Inches(width))

# Cover
p=D.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_before=Pt(60)
r=p.add_run('PROJECT BASED LEARNING');r.bold=True;r.font.size=Pt(13);r.font.color.rgb=RGBColor.from_string('26734D')
p=D.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_before=Pt(35)
r=p.add_run('WORKFORCEOS');r.bold=True;r.font.size=Pt(30);r.font.color.rgb=RGBColor.from_string('174D35')
p=D.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run('Workforce Shift, Timesheet & Expense\nReconciliation System');r.font.size=Pt(17);r.bold=True
p=D.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_before=Pt(30);p.add_run('SOFTWARE DEVELOPMENT PROJECT REPORT').bold=True
p=D.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_before=Pt(38);p.add_run('Submitted by').bold=True
for s in ['Shivam  (1/24/SET/BCS/159)','Deepak  (1/24/SET/BCS/165)','Sameer  (1/24/SET/BCS/154)','Abhay  (1/24/SET/BCS/157)']:
 p=D.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.add_run(s)
p=D.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_before=Pt(22);p.add_run('Academic Year: 2026–2027').bold=True
p=D.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_before=Pt(35);p.add_run('Department of Computer Science and Engineering\nManav Rachna International Institute of Research and Studies')
page()
heading('INDEX')
for x in ['1. Abstract','2. Introduction','3. Objectives','4. System Analysis','5. ER Diagram and Schema Design','6. Implementation','7. Output','8. Results and Discussion','9. Conclusion and Future Work','10. References','Appendix A — Installation and User Guide','Appendix B — Test Cases']:
 bullet(x)
page()
heading('1. ABSTRACT')
para('WorkforceOS is a web-based Workforce Shift, Timesheet & Expense Reconciliation System developed to centralize routine workforce administration. The system provides role-aware access for administrators, managers and employees. Administrators can create team accounts, managers can schedule shifts and review submitted records, and employees can view their assigned shifts, submit working hours and register business expenses. The application calculates daily worked hours after subtracting breaks and calculates overtime as hours beyond eight hours for a workday. Expense and timesheet records follow an approval workflow and are stored persistently in an SQLite relational database.')
para('The solution is implemented using Python’s standard-library HTTP server and SQLite for the backend, with HTML, CSS and JavaScript for a responsive browser interface. It includes a dashboard, searchable tables, role checks, input validation and demonstration data. The project applies software engineering concepts including modular design, client-server communication, relational data modelling, CRUD operations, authentication, validation, workflow management and testing. It is intended as an academic prototype; production deployment would require stronger authentication, secure session persistence, audit controls and jurisdiction-specific payroll rules.')
heading('2. INTRODUCTION')
heading('2.1 Background',2)
para('Organizations with shift-based teams need to coordinate who works, when work is performed and which costs are associated with that work. When schedules, hours and expenses are tracked in separate spreadsheets or messages, managers may face duplicate entries, delayed approvals, inconsistent calculations and limited visibility. A unified system can reduce repeated data entry and provide a shared operational view.')
heading('2.2 Problem Statement',2)
para('The project addresses the absence of a single lightweight platform for shift assignment, daily timesheet submission, expense recording and manager review. The system must keep records associated with employees, enforce role permissions, calculate hours consistently and expose the state of submitted records.')
heading('2.3 Proposed Solution',2)
para('WorkforceOS provides a browser-based interface connected to a Python application server and SQLite database. Users authenticate with role-specific accounts. Employees submit timesheets and expenses; managers schedule shifts and review employee submissions; administrators maintain employee accounts. Dashboard counters summarize pending approvals and workforce activity.')
heading('2.4 Scope',2)
for x in ['Employee, manager and administrator roles with role-based access checks.','Shift creation and assignment to an employee.','Timesheet entry with clock-in, clock-out, break deduction and overtime calculation.','Expense submission with category, description, amount and optional receipt filename.','Approval or rejection of submitted timesheets and expenses.','Dashboard, searchable records and persistent local database.'] : bullet(x)
heading('2.5 Intended Users',2)
table(['User role','Primary responsibilities'],[['Employee','View own shifts; submit timesheets and expense claims; review own record statuses.'],['Manager','Schedule shifts; view team records; approve or reject timesheets and expenses.'],['Administrator','Create team accounts; perform manager-level operational functions; view workforce dashboard.']])
page()
heading('3. OBJECTIVES')
for x in ['Develop a functional browser-based workforce administration application.','Provide authentication and role-aware authorization for three user roles.','Create and maintain employee shift schedules.','Record work dates, clock-in/out times and break duration.','Calculate net daily hours and overtime using a documented rule.','Record business expenses and support review decisions.','Maintain persistent relational records using SQLite and foreign-key relationships.','Provide dashboard summaries and searchable operational tables.','Validate user input and handle duplicate or invalid records gracefully.','Document architecture, data model, workflows and test evidence.'] : bullet(x)
heading('3.1 Expected Outcomes',2)
para('A runnable local application, seeded demonstration database, source code, installation guide, test suite and this PBL report. The project is designed to demonstrate end-to-end software development rather than a static screen mock-up.')
heading('3.2 Success Criteria',2)
table(['ID','Success criterion','Verification'],[['SC-01','Valid user can log in','Login test with demo accounts'],['SC-02','Employee can submit a timesheet','Create and retrieve API record'],['SC-03','Hours and overtime are calculated correctly','Unit tests for normal and overnight shifts'],['SC-04','Employee can submit an expense','Create and retrieve API record'],['SC-05','Manager can approve/reject submissions','PATCH status workflow test'],['SC-06','Employee cannot access manager-only actions','Role authorization test'],['SC-07','Records persist after server restart','SQLite persistence check']])
page()
heading('4. SYSTEM ANALYSIS')
heading('4.1 Existing System',2)
para('A manual or spreadsheet-driven process typically requires separate files for staff lists, shift calendars, attendance and expense claims. The same employee or date may be typed repeatedly. Review status may be communicated informally, making it difficult to determine which records are awaiting action.')
heading('4.2 Proposed System',2)
para('The proposed application centralizes the core records in one relational database. The browser communicates with the application through JSON endpoints. Server-side validation and role checks protect operations, while the interface presents the appropriate actions to each role.')
heading('4.3 Functional Requirements',2)
for x in ['FR-01: The system shall authenticate active users using email and password.','FR-02: The system shall distinguish admin, manager and employee roles.','FR-03: Admin shall be able to create employee and manager accounts.','FR-04: Admin/manager shall be able to create a shift and assign it to an employee.','FR-05: Employees shall be able to view only their own shifts.','FR-06: An employee shall submit one timesheet per work date with clock-in, optional clock-out, break minutes and notes.','FR-07: The system shall calculate net hours as elapsed time minus break duration.','FR-08: The system shall calculate overtime as max(0, net hours − 8).','FR-09: Employees shall submit expense date, category, description, amount and optional receipt filename.','FR-10: Admin/manager shall approve or reject submitted timesheets and pending expenses.','FR-11: The system shall display dashboard totals and pending-work counts.','FR-12: The system shall retain records in SQLite across restarts.'] : bullet(x)
heading('4.4 Non-Functional Requirements',2)
for x in ['Usability: responsive layout, clear labels, status indicators and searchable tables.','Performance: lightweight local deployment suitable for a classroom demonstration.','Reliability: database constraints, validation and explicit error responses.','Maintainability: separated frontend assets, server routes and database tables.','Security: server-side authorization and password hashing for demonstration.','Portability: Python 3.10+ and no third-party Python package requirement.'] : bullet(x)
heading('4.5 Use Case Diagram',2);img('use_case.png')
para('The use case diagram identifies the three actors. Employees view their shifts, submit timesheets and expenses, and view their dashboard. Managers review records and schedule shifts. Administrators additionally manage employee accounts. The backend enforces these permissions; hiding a menu item is not treated as the security boundary.')
heading('4.6 Activity Diagram — Timesheet Workflow',2);img('activity.png')
para('The activity diagram follows a timesheet from login through entry validation and submission to manager review. A review decision changes the status to approved or rejected. Invalid inputs are rejected before a record is stored.')
heading('4.7 Sequence Diagram — Expense Approval',2);img('sequence.png')
para('The sequence diagram shows the employee submitting an expense from the browser, the HTTP API validating and storing it as pending, and a manager later sending an approval decision. The database persists the status update.')
heading('4.8 Feasibility Analysis',2)
table(['Type','Analysis'],[['Technical','Uses Python, browser technologies and SQLite; can run on a standard student laptop.'],['Operational','Role-based screens map to familiar employee and manager tasks.'],['Economic','Uses free, built-in technologies; no paid hosting or database is needed for the demo.'],['Schedule','Core workflows are small enough to implement and test within a semester project.']])
page()
heading('5. ER DIAGRAM AND SCHEMA DESIGN')
para('The database contains four principal entities: Employee, Shift, Timesheet and Expense. Employee is the parent entity for the three operational record types. Each shift, timesheet and expense belongs to one employee, while an employee can have multiple records over time.')
img('er_diagram.png')
heading('5.1 Relational Schema',2)
table(['Table','Important attributes','Keys / constraints'],[['employees','id, name, email, department, role, password_hash, active','PK id; email UNIQUE; role in admin/manager/employee'],['shifts','id, title, department, shift_date, start_time, end_time, employee_id, status','PK id; FK employee_id → employees.id'],['timesheets','id, employee_id, work_date, clock_in, clock_out, break_minutes, hours, overtime, status','PK id; FK employee_id; UNIQUE(employee_id, work_date)'],['expenses','id, employee_id, expense_date, category, description, amount, receipt_name, status, manager_note','PK id; FK employee_id; amount > 0']])
heading('5.2 Data Dictionary',2)
for x in ['Employee: stores identity, department, account role and password hash.','Shift: stores the scheduled work period, assigned employee and schedule status.','Timesheet: stores one employee workday, clock times, break duration, computed hours, overtime and approval status.','Expense: stores an employee cost claim, category, amount, optional receipt reference and review decision.'] : bullet(x)
heading('5.3 Relationships and Integrity',2)
para('The relationship between Employee and each operational table is one-to-many. Foreign keys prevent operational records from referencing nonexistent employees. Employee email is unique. Timesheet employee/date is unique to prevent duplicate daily submissions. Expense amount must be positive. SQLite foreign-key enforcement is enabled for every connection.')
page()
heading('6. IMPLEMENTATION')
heading('6.1 Technology Stack',2)
table(['Layer','Technology','Purpose'],[['Frontend','HTML5, CSS3, JavaScript','Responsive screens, forms, tables and browser interactions'],['Backend','Python 3 standard library','HTTP request handling, validation, authorization and calculations'],['Database','SQLite 3','Persistent relational data store'],['Communication','HTTP + JSON','Client/server API requests and responses'],['Testing','Python unittest','Business logic tests']])
heading('6.2 System Architecture',2);img('architecture.png')
heading('6.3 Module Description',2)
for x in ['Authentication module: validates email/password, creates a session token and returns the current user profile.','Employee module: lists team members for authorized roles and creates employee/manager accounts for administrators.','Shift module: validates and stores scheduled shifts and returns employee-specific or team-wide rosters.','Timesheet module: validates date/time/break inputs, computes net hours and overtime, and supports approval status updates.','Expense module: validates positive claim amounts and required details, stores claims as pending and supports review decisions.','Dashboard module: calculates employee counts, scheduled shifts, pending submissions, month-to-date hours and approved expense totals.'] : bullet(x)
heading('6.4 Key Algorithms',2)
heading('Net Hours Calculation',3)
para('Let start and end be local clock times. If end is earlier than start, the end time is treated as occurring on the next day (overnight shift). ElapsedHours = (EndDateTime − StartDateTime) / 3600. NetHours = max(0, ElapsedHours − BreakMinutes/60). OvertimeHours = max(0, NetHours − 8). Values are rounded to two decimal places.')
heading('Authorization Check',3)
para('For every protected API request, the server resolves the session cookie to an active employee record. If no valid user exists, it returns HTTP 401. If the user role is not in the permitted role set for the operation, it returns HTTP 403. Employee list queries are restricted to the current employee for employee-role users.')
heading('6.5 API Design',2)
table(['Method & endpoint','Purpose','Access'],[['POST /api/login','Authenticate user','Public'],['GET /api/me','Current session profile','Authenticated'],['GET /api/dashboard','Summary counters','Authenticated'],['GET/POST /api/employees','List/create accounts','Admin for create; manager/admin list'],['GET/POST /api/shifts','View/create shifts','Authenticated view; manager/admin create'],['GET/POST /api/timesheets','View/submit timesheets','Authenticated; employee submits own'],['PATCH /api/timesheets/{id}','Review timesheet','Manager/admin'],['GET/POST /api/expenses','View/submit expenses','Authenticated; employee submits own'],['PATCH /api/expenses/{id}','Review expense','Manager/admin']])
heading('6.6 Security and Validation',2)
para('The application hashes demo passwords before storage and performs role checks on protected API endpoints. Inputs are validated for required fields, allowed role/status values, positive expense amount and sensible break duration. SQL values are passed as parameters rather than concatenated into query strings. This is an academic prototype: SHA-256 with a fixed demo prefix and in-memory sessions are not suitable for production. Production use should add Argon2id/bcrypt, HTTPS, CSRF protection, secure persistent sessions, rate limiting, audit trails and a formal authorization review.')
heading('6.7 Implementation Note',2)
para('The provided application is implemented using the Python standard library and does not require Flask or a separate SQL server. Running app.py initializes the database and seeds demonstration records if the database is empty.')
page()
heading('7. OUTPUT')
para('The following examples describe the seeded demonstration environment and expected user-visible outputs. When running the application, use the browser interface to reproduce these workflows and capture actual screenshots for submission.')
heading('7.1 Login Screen',2)
para('The login screen accepts an email address and password. A successful login opens the dashboard. Invalid credentials display an error message without exposing account details.')
heading('7.2 Dashboard Output',2)
para('The dashboard displays active employee count, scheduled shift count, pending timesheets, pending expenses, month-to-date logged hours and approved expense totals. Quick-action links open the relevant submission forms.')
heading('7.3 Shift Schedule Output',2)
table(['Shift','Employee','Date','Time','Status'],[['Morning Operations','Aarav Mehta','Next seeded date','09:00–17:00','scheduled'],['Finance Support','Neha Verma','Following seeded date','10:00–18:00','scheduled'],['Engineering Coverage','Kabir Singh','Third seeded date','12:00–20:00','scheduled']])
heading('7.4 Timesheet Calculation Example',2)
para('Input: clock-in 09:00, clock-out 18:30, break 30 minutes. Elapsed time = 9.5 hours; net hours = 9.0; overtime = 1.0 hour. The submitted record is initially marked submitted and becomes approved or rejected after manager review.')
heading('7.5 Expense Approval Example',2)
para('An employee submits a Travel expense for ₹420 with a description and date. The claim appears with Pending status. A manager can approve or reject it; approved expense totals are reflected in the dashboard.')
heading('7.6 Sample Console Output',2)
para('Group 10 Workforce System running at http://127.0.0.1:8000\nDatabase: workforce.db\nHealth endpoint: /api/health → {"status":"ok","database":"workforce.db"}')
heading('7.7 Screenshots to Add Before Submission',2)
for x in ['Login screen with the application title visible.','Admin dashboard showing summary cards and quick actions.','Shift schedule showing assigned employees and dates.','Timesheet table showing calculated hours and manager review controls.','Expense table showing pending and approved claims.','Team directory showing roles and departments.'] : bullet(x)
para('Screenshots should be captured from the running application on the project team’s own machine. The report does not fabricate screenshots or claim that a screenshot was captured.')
page()
heading('8. RESULTS AND DISCUSSION')
para('The implemented prototype provides the core workflows requested by the project title: employee records, shift assignment, timesheet submission, expense submission and manager review. Data is persisted in SQLite, and the dashboard reads live totals from the database. Employee-facing list queries are scoped to the logged-in employee, while manager/admin review endpoints enforce role restrictions.')
heading('8.1 Test Summary',2)
table(['Test ID','Scenario','Expected result'],[['T-01','Valid admin login','Dashboard opens'],['T-02','Invalid password','401 response and visible error'],['T-03','Employee requests team directory','403 response'],['T-04','Create shift as manager','Shift is saved and visible in roster'],['T-05','Submit timesheet 09:00–17:30 with 30m break','8.00 net hours, 0 overtime'],['T-06','Submit timesheet 09:00–18:30 with 30m break','9.00 net hours, 1.00 overtime'],['T-07','Submit positive expense','Claim stored with pending status'],['T-08','Manager approves expense','Status becomes approved'],['T-09','Duplicate employee/date timesheet','Database rejects duplicate record'],['T-10','Restart application','SQLite records remain available']])
heading('8.2 Test Execution',2)
para('The included automated unit tests cover regular shifts, overtime, overnight shifts and break deduction. Run `python -m unittest discover -s tests -v` from the project folder. The browser workflows and API role checks should also be demonstrated manually using the supplied accounts. Do not enter unverified test results in the final submission; record the actual test run and screenshots from your environment.')
heading('8.3 Discussion',2)
para('The prototype demonstrates how role-based workflows and a normalized relational model can bring several workforce tasks into one application. A clear approval status makes outstanding work visible. The daily timesheet uniqueness constraint prevents a common duplicate-entry case. The hour calculation is deterministic and covered by unit tests. The current implementation intentionally remains a local academic prototype and does not replace a payroll system or enforce country-specific labour law.')
heading('8.4 Limitations',2)
for x in ['Receipt files are represented by a filename only; actual binary upload and storage are not included.','A submitted timesheet cannot currently be edited or clocked out later if the clock-out field was left blank.','Shift conflict detection and leave management are not implemented.','Session tokens are stored in memory and are cleared when the server restarts.','The password hash method is for demonstration only and must be replaced before deployment.','No external payroll, accounting, calendar or biometric attendance integration is provided.'] : bullet(x)
page()
heading('9. CONCLUSION AND FUTURE WORK')
para('WorkforceOS demonstrates an end-to-end software development approach for a workforce operations problem. It combines a browser interface, Python HTTP application, business validation and an SQLite relational database. The system supports three user roles, shift scheduling, timesheet entry, work-hour calculation, expense claims and manager review. The project provides a practical demonstration of CRUD operations, relational schema design, API communication, authorization, input validation and automated unit testing.')
heading('9.1 Future Work',2)
for x in ['Add a secure clock-in/clock-out workflow with editable draft timesheets.','Implement actual receipt upload with file type/size validation and protected storage.','Add shift overlap detection, leave requests, availability and swap workflows.','Introduce configurable overtime rules, weekly limits and payroll exports.','Add audit logs recording who changed a status and when.','Replace demo authentication with a modern password KDF, persistent sessions, CSRF protection and HTTPS.','Add CSV/PDF reports and date-range analytics.','Deploy to a managed database and cloud hosting environment with backups and monitoring.','Add automated integration tests and broader accessibility testing.'] : bullet(x)
heading('10. REFERENCES')
refs=['Python Software Foundation. Python 3 Documentation — https://docs.python.org/3/','SQLite Consortium. SQLite Documentation — https://www.sqlite.org/docs.html','MDN Web Docs. HTML: HyperText Markup Language — https://developer.mozilla.org/docs/Web/HTML','MDN Web Docs. CSS — https://developer.mozilla.org/docs/Web/CSS','MDN Web Docs. JavaScript — https://developer.mozilla.org/docs/Web/JavaScript','OWASP Foundation. Authentication Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html','OWASP Foundation. Session Management Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html','Sommerville, I. Software Engineering. 10th Edition, Pearson, 2015.']
for r in refs:numbered(r)
page()
heading('APPENDIX A — INSTALLATION AND USER GUIDE')
heading('A.1 Run the Project',2)
for x in ['Install Python 3.10 or later.','Extract the project ZIP into a writable folder.','Open Command Prompt or PowerShell in the extracted folder.','Run `py app.py` on Windows or `python3 app.py` on macOS/Linux.','Open http://127.0.0.1:8000 in a modern browser.','The first run creates workforce.db and inserts demo accounts and sample records.'] : numbered(x)
heading('A.2 Demo Credentials',2)
table(['Role','Email','Password'],[['Admin','admin@group10.local','admin123'],['Manager','manager@group10.local','manager123'],['Employee','aarav@group10.local','employee123'],['Employee','neha@group10.local','employee123'],['Employee','kabir@group10.local','employee123']])
heading('A.3 Suggested Demonstration Flow',2)
for x in ['Sign in as admin and show the dashboard.','Open Team Directory and add a test employee.','Sign out and sign in as manager; create a shift for an employee.','Open Timesheets and submit a workday record as an employee.','Return as manager and approve the submitted timesheet.','Submit an expense as an employee and approve it as manager.','Refresh the dashboard to show updated totals.'] : numbered(x)
heading('APPENDIX B — TEST CASES')
table(['ID','Input / action','Expected outcome'],[['B-01','09:00 to 17:30; 30-minute break','8.00 hours; 0.00 overtime'],['B-02','09:00 to 18:30; 30-minute break','9.00 hours; 1.00 overtime'],['B-03','22:00 to 06:00; no break','8.00 hours; 0.00 overtime'],['B-04','09:00 to 17:00; 60-minute break','7.00 hours; 0.00 overtime'],['B-05','Expense amount 0 or negative','Validation error'],['B-06','Employee attempts manager-only action','403 forbidden'],['B-07','Duplicate employee/date timesheet','Conflict / database constraint error']])

out=ROOT/'PBL_Report_Group10.docx';D.save(out);print(out)
