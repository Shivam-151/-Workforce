"""Group 10 Workforce Shift, Timesheet & Expense Reconciliation System.
Runs on Python standard library only. Demo credentials are documented in README.md.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from pathlib import Path
import sqlite3, json, hashlib, secrets, hmac, os, datetime, mimetypes

BASE = Path(__file__).resolve().parent
DB = BASE / 'workforce.db'
HOST, PORT = '127.0.0.1', int(os.environ.get('PORT', '8000'))
SESSIONS = {}  # demo in-memory sessions; use a persistent session store in production

def connect():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row; c.execute('PRAGMA foreign_keys=ON'); return c

def pw_hash(p): return hashlib.sha256(('group10-demo:'+p).encode()).hexdigest()

def init_db():
    with connect() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS employees(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,department TEXT NOT NULL,role TEXT NOT NULL CHECK(role IN ('admin','manager','employee')),password_hash TEXT NOT NULL,active INTEGER NOT NULL DEFAULT 1,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS shifts(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,department TEXT NOT NULL,shift_date TEXT NOT NULL,start_time TEXT NOT NULL,end_time TEXT NOT NULL,employee_id INTEGER NOT NULL REFERENCES employees(id),status TEXT NOT NULL DEFAULT 'scheduled',notes TEXT DEFAULT '',created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS timesheets(id INTEGER PRIMARY KEY AUTOINCREMENT,employee_id INTEGER NOT NULL REFERENCES employees(id),work_date TEXT NOT NULL,clock_in TEXT,clock_out TEXT,break_minutes INTEGER NOT NULL DEFAULT 0,hours REAL NOT NULL DEFAULT 0,overtime REAL NOT NULL DEFAULT 0,status TEXT NOT NULL DEFAULT 'submitted',notes TEXT DEFAULT '',created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,UNIQUE(employee_id,work_date));
        CREATE TABLE IF NOT EXISTS expenses(id INTEGER PRIMARY KEY AUTOINCREMENT,employee_id INTEGER NOT NULL REFERENCES employees(id),expense_date TEXT NOT NULL,category TEXT NOT NULL,description TEXT NOT NULL,amount REAL NOT NULL CHECK(amount>0),receipt_name TEXT DEFAULT '',status TEXT NOT NULL DEFAULT 'pending',manager_note TEXT DEFAULT '',created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        ''')
        if c.execute('SELECT COUNT(*) FROM employees').fetchone()[0] == 0:
            people=[('System Admin','admin@group10.local','Operations','admin','admin123'),('Riya Sharma','manager@group10.local','Operations','manager','manager123'),('Aarav Mehta','aarav@group10.local','Operations','employee','employee123'),('Neha Verma','neha@group10.local','Finance','employee','employee123'),('Kabir Singh','kabir@group10.local','Engineering','employee','employee123')]
            for n,e,d,r,p in people: c.execute('INSERT INTO employees(name,email,department,role,password_hash) VALUES(?,?,?,?,?)',(n,e,d,r,pw_hash(p)))
            today=datetime.date.today(); ids={r['email']:r['id'] for r in c.execute('SELECT id,email FROM employees')}
            for i,(email,title,st,en) in enumerate([('aarav@group10.local','Morning Operations','09:00','17:00'),('neha@group10.local','Finance Support','10:00','18:00'),('kabir@group10.local','Engineering Coverage','12:00','20:00')]):
                c.execute('INSERT INTO shifts(title,department,shift_date,start_time,end_time,employee_id,notes) VALUES(?,?,?,?,?,?,?)',(title,'Operations' if i==0 else ('Finance' if i==1 else 'Engineering'),(today+datetime.timedelta(days=i)).isoformat(),st,en,ids[email],'Seeded demonstration shift'))
            c.execute('INSERT INTO timesheets(employee_id,work_date,clock_in,clock_out,break_minutes,hours,overtime,status,notes) VALUES(?,?,?,?,?,?,?,?,?)',(ids['aarav@group10.local'],(today-datetime.timedelta(days=1)).isoformat(),'09:02','17:35',30,8.05,0.05,'approved','Demo approved entry'))
            c.execute('INSERT INTO expenses(employee_id,expense_date,category,description,amount,status) VALUES(?,?,?,?,?,?)',(ids['aarav@group10.local'],today.isoformat(),'Travel','Local client visit',420.0,'pending'))

def rowdicts(rows): return [dict(x) for x in rows]
def json_bytes(obj): return json.dumps(obj, default=str).encode()
def calc_hours(start,end,break_minutes):
    a=datetime.datetime.strptime(start,'%H:%M'); b=datetime.datetime.strptime(end,'%H:%M')
    if b<a: b += datetime.timedelta(days=1)
    hours=max(0,(b-a).total_seconds()/3600-break_minutes/60)
    return round(hours,2),round(max(0,hours-8),2)

class Handler(BaseHTTPRequestHandler):
    server_version='Group10Workforce/1.0'
    def log_message(self,*args): pass
    def send(self,status,body,ctype='application/json; charset=utf-8',headers=None):
        self.send_response(status); self.send_header('Content-Type',ctype); self.send_header('X-Content-Type-Options','nosniff'); self.send_header('Cache-Control','no-store')
        for k,v in (headers or {}).items(): self.send_header(k,v)
        self.end_headers();
        if isinstance(body, (dict,list)): body=json_bytes(body)
        self.wfile.write(body if isinstance(body,bytes) else body.encode())
    def body(self):
        n=int(self.headers.get('Content-Length','0') or 0); raw=self.rfile.read(n) if n else b'{}'
        try: return json.loads(raw)
        except Exception: return {}
    def user(self):
        token=''
        for part in self.headers.get('Cookie','').split(';'):
            if part.strip().startswith('g10session='): token=part.strip().split('=',1)[1]
        uid=SESSIONS.get(token)
        if not uid:return None
        with connect() as c: r=c.execute('SELECT id,name,email,department,role,active FROM employees WHERE id=?',(uid,)).fetchone()
        return dict(r) if r and r['active'] else None
    def require(self,roles=None):
        u=self.user()
        if not u: self.send(401,{'error':'Please log in again.'}); return None
        if roles and u['role'] not in roles: self.send(403,{'error':'You do not have permission for this action.'}); return None
        return u
    def do_GET(self):
        p=urlparse(self.path).path
        if p=='/' or p=='/index.html':
            f=BASE/'static'/'index.html'; return self.send(200,f.read_bytes(),'text/html; charset=utf-8')
        if p.startswith('/static/'):
            f=BASE/p.lstrip('/')
            if f.exists() and f.is_file(): return self.send(200,f.read_bytes(),mimetypes.guess_type(str(f))[0] or 'application/octet-stream')
            return self.send(404,b'Not found','text/plain')
        if p=='/api/me':
            u=self.user(); return self.send(200,{'user':u})
        if p=='/api/health': return self.send(200,{'status':'ok','database':str(DB.name)})
        u=self.require()
        if not u:return
        with connect() as c:
            if p=='/api/dashboard':
                own='' if u['role'] in ('admin','manager') else ' WHERE employee_id=?'; args=() if not own else (u['id'],)
                data={'employees':c.execute('SELECT COUNT(*) FROM employees WHERE active=1').fetchone()[0] if u['role'] in ('admin','manager') else 1,'shifts':c.execute('SELECT COUNT(*) FROM shifts WHERE status="scheduled"').fetchone()[0],'timesheets_pending':c.execute('SELECT COUNT(*) FROM timesheets WHERE status="submitted"'+(' AND employee_id=?' if own else ''),args).fetchone()[0],'expenses_pending':c.execute('SELECT COUNT(*) FROM expenses WHERE status="pending"'+(' AND employee_id=?' if own else ''),args).fetchone()[0],'hours_this_month':c.execute("SELECT COALESCE(SUM(hours),0) FROM timesheets WHERE substr(work_date,1,7)=substr(date('now'),1,7)"+(' AND employee_id=?' if own else ''),args).fetchone()[0],'expense_total':c.execute('SELECT COALESCE(SUM(amount),0) FROM expenses WHERE status="approved"'+(' AND employee_id=?' if own else ''),args).fetchone()[0]}
                return self.send(200,data)
            if p=='/api/employees':
                if u['role'] not in ('admin','manager'): return self.send(403,{'error':'Only managers can view the team directory.'})
                return self.send(200,{'items':rowdicts(c.execute('SELECT id,name,email,department,role,active,created_at FROM employees ORDER BY name'))})
            if p=='/api/shifts':
                sql='SELECT s.*,e.name employee_name FROM shifts s JOIN employees e ON e.id=s.employee_id'; args=()
                if u['role']=='employee':sql+=' WHERE s.employee_id=?';args=(u['id'],)
                sql+=' ORDER BY s.shift_date,s.start_time'
                return self.send(200,{'items':rowdicts(c.execute(sql,args))})
            if p=='/api/timesheets':
                sql='SELECT t.*,e.name employee_name FROM timesheets t JOIN employees e ON e.id=t.employee_id';args=()
                if u['role']=='employee':sql+=' WHERE t.employee_id=?';args=(u['id'],)
                sql+=' ORDER BY t.work_date DESC,t.id DESC'
                return self.send(200,{'items':rowdicts(c.execute(sql,args))})
            if p=='/api/expenses':
                sql='SELECT x.*,e.name employee_name FROM expenses x JOIN employees e ON e.id=x.employee_id';args=()
                if u['role']=='employee':sql+=' WHERE x.employee_id=?';args=(u['id'],)
                sql+=' ORDER BY x.expense_date DESC,x.id DESC'
                return self.send(200,{'items':rowdicts(c.execute(sql,args))})
        return self.send(404,{'error':'Endpoint not found.'})
    def do_POST(self):
        p=urlparse(self.path).path; d=self.body()
        if p=='/api/login':
            email=str(d.get('email','')).strip().lower(); password=str(d.get('password',''))
            with connect() as c:r=c.execute('SELECT id FROM employees WHERE email=? AND password_hash=? AND active=1',(email,pw_hash(password))).fetchone()
            if not r:return self.send(401,{'error':'Incorrect email or password.'})
            token=secrets.token_urlsafe(32);SESSIONS[token]=r['id'];return self.send(200,{'ok':True},{'Content-Type':'application/json; charset=utf-8'} if False else 'application/json; charset=utf-8',{'Set-Cookie':f'g10session={token}; HttpOnly; SameSite=Lax; Path=/'})
        u=self.require()
        if not u:return
        try:
            with connect() as c:
                if p=='/api/logout':
                    token='';
                    for part in self.headers.get('Cookie','').split(';'):
                        if part.strip().startswith('g10session='):token=part.strip().split('=',1)[1]
                    SESSIONS.pop(token,None);return self.send(200,{'ok':True},headers={'Set-Cookie':'g10session=; Max-Age=0; Path=/; HttpOnly; SameSite=Lax'})
                if p=='/api/employees':
                    if u['role']!='admin':return self.send(403,{'error':'Only an admin can add employees.'})
                    name=str(d.get('name','')).strip();email=str(d.get('email','')).strip().lower();dept=str(d.get('department','Operations')).strip();role=d.get('role','employee');pw=str(d.get('password','employee123'))
                    if not name or '@' not in email or role not in ('manager','employee') or len(pw)<6:return self.send(400,{'error':'Enter a name, valid email, role and password of at least 6 characters.'})
                    c.execute('INSERT INTO employees(name,email,department,role,password_hash) VALUES(?,?,?,?,?)',(name,email,dept,role,pw_hash(pw)));return self.send(201,{'ok':True})
                if p=='/api/shifts':
                    if u['role'] not in ('admin','manager'):return self.send(403,{'error':'Only managers can schedule shifts.'})
                    required=['title','department','shift_date','start_time','end_time','employee_id']
                    if any(not d.get(k) for k in required):return self.send(400,{'error':'Complete all required shift fields.'})
                    c.execute('INSERT INTO shifts(title,department,shift_date,start_time,end_time,employee_id,notes) VALUES(?,?,?,?,?,?,?)',(d['title'],d['department'],d['shift_date'],d['start_time'],d['end_time'],int(d['employee_id']),d.get('notes','')));return self.send(201,{'ok':True})
                if p=='/api/timesheets':
                    eid=u['id'] if u['role']=='employee' else int(d.get('employee_id') or u['id']); date=str(d.get('work_date','')); cin=str(d.get('clock_in',''));cout=str(d.get('clock_out','')); br=int(d.get('break_minutes',0))
                    if not date or not cin:return self.send(400,{'error':'Work date and clock-in time are required.'})
                    if br<0 or br>600:return self.send(400,{'error':'Break must be between 0 and 600 minutes.'})
                    hrs,ot=calc_hours(cin,cout,br) if cout else (0,0)
                    c.execute('INSERT INTO timesheets(employee_id,work_date,clock_in,clock_out,break_minutes,hours,overtime,status,notes) VALUES(?,?,?,?,?,?,?,?,?)',(eid,date,cin,cout or None,br,hrs,ot,'submitted',d.get('notes','')));return self.send(201,{'ok':True,'hours':hrs,'overtime':ot})
                if p=='/api/expenses':
                    amount=float(d.get('amount',0));desc=str(d.get('description','')).strip();category=str(d.get('category','Other'))
                    if amount<=0 or not desc or not d.get('expense_date'):return self.send(400,{'error':'Enter a date, description and positive amount.'})
                    c.execute('INSERT INTO expenses(employee_id,expense_date,category,description,amount,receipt_name,status) VALUES(?,?,?,?,?,?,?)',(u['id'],d['expense_date'],category,desc,amount,str(d.get('receipt_name','')),'pending'));return self.send(201,{'ok':True})
        except sqlite3.IntegrityError as e:return self.send(409,{'error':'This record conflicts with existing data. Check duplicate date or employee details.'})
        except (ValueError,TypeError):return self.send(400,{'error':'Invalid field value.'})
        return self.send(404,{'error':'Endpoint not found.'})
    def do_PATCH(self):
        p=urlparse(self.path).path;u=self.require(('admin','manager'))
        if not u:return
        d=self.body()
        try:
            with connect() as c:
                if p.startswith('/api/timesheets/'):
                    tid=int(p.rsplit('/',1)[1]);status=d.get('status')
                    if status not in ('approved','rejected','submitted'):return self.send(400,{'error':'Invalid timesheet status.'})
                    c.execute('UPDATE timesheets SET status=? WHERE id=?',(status,tid))
                    if c.total_changes==0:return self.send(404,{'error':'Timesheet not found.'})
                    return self.send(200,{'ok':True})
                if p.startswith('/api/expenses/'):
                    eid=int(p.rsplit('/',1)[1]);status=d.get('status');note=str(d.get('manager_note',''))
                    if status not in ('approved','rejected','pending'):return self.send(400,{'error':'Invalid expense status.'})
                    c.execute('UPDATE expenses SET status=?,manager_note=? WHERE id=?',(status,note,eid))
                    if c.total_changes==0:return self.send(404,{'error':'Expense not found.'})
                    return self.send(200,{'ok':True})
        except ValueError:return self.send(400,{'error':'Invalid record id.'})
        return self.send(404,{'error':'Endpoint not found.'})

def main():
    init_db(); print(f'Group 10 Workforce System running at http://{HOST}:{PORT}'); print('Demo: admin@group10.local / admin123')
    ThreadingHTTPServer((HOST,PORT),Handler).serve_forever()
if __name__=='__main__': main()
