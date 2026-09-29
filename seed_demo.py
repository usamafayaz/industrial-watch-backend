"""
Resets the database and fills it with demo data for every screen of the app.

Run from the backend folder:  .venv/bin/python seed_demo.py

Employees 16-21 match the folders in EmployeeImages/ and the classes in the
trained face-recognition model, so attendance/monitoring can identify them.
"""
import os
from datetime import date, time, timedelta

from sqlalchemy import text

import DBHandler

TABLES = ['ViolationImages', 'Violation', 'Attendance', 'EmployeeImages', 'EmployeeProductivity',
          'EmployeeSection', 'Employee', 'Users', 'JobRole', 'SectionRule', 'ProductivityRule', 'Section',
          'StockInBatch', 'Batch', 'ProductLink', 'Stock', 'ProductFormula', 'Product', 'RawMaterial']

today = date.today()
month_start = today.replace(day=1)

# (id, name, username, password, role, job_role_id, job_type, gender, section_ids, productivity)
PEOPLE = [
    (1, 'Admin', 'admin', 'admin', 'Admin', 1, 'Full Time', 'Male', [], None),
    (20, 'Muhammad Usama', 'usama', 'usama123', 'Supervisor', 2, 'Full Time', 'Male', [1, 2, 3], 92.5),
    # Demo employee: no violations yet, works in Quality Control (mobile usage, 1 second allowed)
    (21, 'Abdullah Mustafa', 'abdullah', 'abdullah123', 'Employee', 3, 'Full Time', 'Male', [3], 100.0),
    (16, 'Kamran Ali', 'kamran', 'kamran123', 'Employee', 3, 'Full Time', 'Male', [1], 84.2),
    (17, 'Zia Ul Haq', 'zia', 'zia123', 'Employee', 3, 'Full Time', 'Male', [1], 76.8),
    (18, 'Umer Farooq', 'umer', 'umer123', 'Employee', 4, 'Part Time', 'Male', [2], 91.3),
    (19, 'Armaghan Ahmed', 'armaghan', 'armaghan123', 'Employee', 4, 'Full Time', 'Male', [1], 68.5),
]
GUESTS = [(23, 'Visitor Bilal'), (24, 'Visitor Hamza')]

# (id, name, status, is_special, [(rule_id, fine, allowed_time)])
SECTIONS = [
    (1, 'Assembly Line', 1, 0, [(1, 500, time(0, 5)), (2, 300, time(0, 10)), (3, 200, time(0, 15))]),
    (2, 'Packaging', 1, 0, [(1, 500, time(0, 5)), (2, 250, time(0, 10))]),
    (3, 'Quality Control', 1, 0, [(2, 200, time(0, 0, 1))]),
    (4, 'Canteen', 1, 1, [(1, 1000, time(0, 1))]),
    (5, 'Old Warehouse', 0, 0, [(3, 100, time(0, 30))]),
]

# (employee_id, rule_id, day_offset, start, end, image)
VIOLATIONS = [
    (16, 1, 1, time(10, 5), time(10, 17), 'smoking.jpg'),
    (16, 2, 3, time(11, 30), time(11, 52), 'mobile.jpg'),
    (17, 2, 2, time(14, 0), time(14, 25), 'mobile.jpg'),
    (17, 3, 5, time(15, 10), time(15, 40), 'sitting.jpg'),
    (17, 1, 8, time(12, 45), time(12, 58), 'smoking2.jpeg'),
    (18, 2, 4, time(9, 40), time(9, 55), 'mobile.jpg'),
    (19, 3, 6, time(13, 0), time(13, 35), 'sitting.jpg'),
    (19, 2, 9, time(16, 20), time(16, 32), 'mobile.jpg'),
    (23, 1, 7, time(12, 10), time(12, 14), 'smoking.jpg'),
]

RAW_MATERIALS = [(1, 'Cast Iron'), (2, 'Aluminium'), (3, 'PET Plastic'), (4, 'Cotton Yarn'), (5, 'Graphite')]

# Product numbers match the folders in defected_items/ so image downloads work.
PRODUCTS = [
    ('Dis#21052024003152', 'Centrifugal Disc', 'front,back,sides'),
    ('Dis#21052024003405', 'Brake Disc', 'front,back,sides'),
    ('Wat#01092026090000', 'Water Bottle', 'front'),
    ('Tex#01092026090500', 'Textile Fabric', 'front'),
]
FORMULAS = [
    ('Dis#21052024003152', 1, 1500, 'g'), ('Dis#21052024003152', 5, 50, 'g'),
    ('Dis#21052024003405', 1, 2, 'kg'), ('Dis#21052024003405', 2, 300, 'g'),
    ('Wat#01092026090000', 3, 25, 'g'),
    ('Tex#01092026090500', 4, 400, 'g'),
]
# (id, product, packs_per_batch, piece_per_pack, rejection_tolerance)  -- Textile left unlinked on purpose
LINKS = [(1, 'Dis#21052024003152', 10, 10, 10.0), (2, 'Dis#21052024003405', 5, 20, 5.0),
         (3, 'Wat#01092026090000', 20, 24, 2.0)]
# (batch_number, link_id, days_ago, yield, defected)
BATCHES = [
    ('B#21052024003813', 1, 20, 94.0, 6), ('B#01092026101500', 1, 12, 86.0, 14),
    ('B#21052024003916', 2, 15, 96.0, 4), ('B#05092026110000', 2, 5, -1, 0),
    ('B#10092026120000', 3, 8, 99.4, 3),
]
# (stock_number, raw_material_id, quantity_kg, price_per_kg, days_ago)
STOCK = [
    ('Cas#01092026080000', 1, 500, 180, 25), ('Cas#15092026080000', 1, 300, 185, 10),
    ('Alu#02092026080000', 2, 200, 650, 24), ('PET#03092026080000', 3, 150, 320, 20),
    ('Cot#04092026080000', 4, 400, 900, 18), ('Gra#05092026080000', 5, 50, 1200, 16),
]


def weekdays_until_today():
    d = month_start
    while d <= today:
        if d.weekday() < 5:
            yield d
        d += timedelta(days=1)


def main():
    engine = DBHandler.DBHandler().engine
    with engine.begin() as c:
        def run(sql, **params):
            c.execute(text(sql), params)

        def with_ids(table, sql, rows):
            run(f'SET IDENTITY_INSERT {table} ON')
            for r in rows:
                run(sql, **r)
            run(f'SET IDENTITY_INSERT {table} OFF')

        for t in TABLES:
            run(f'DELETE FROM {t}')

        with_ids('ProductivityRule', 'INSERT INTO ProductivityRule (id, name) VALUES (:id, :name)',
                 [dict(id=1, name='Smoking'), dict(id=2, name='Mobile Usage'), dict(id=3, name='Sitting')])
        with_ids('JobRole', 'INSERT INTO JobRole (id, name) VALUES (:id, :name)',
                 [dict(id=i + 1, name=n) for i, n in enumerate(['Admin', 'Supervisor', 'Machine Operator', 'Packer'])])

        with_ids('Section', 'INSERT INTO Section (id, name, status, is_sepecial) VALUES (:id, :n, :s, :sp)',
                 [dict(id=i, n=n, s=s, sp=sp) for i, n, s, sp, _ in SECTIONS])
        for sid, _, _, _, rules in SECTIONS:
            for rule_id, fine, allowed in rules:
                run('INSERT INTO SectionRule (section_id, rule_id, fine, allowed_time, date_time) '
                    'VALUES (:s, :r, :f, :a, :d)', s=sid, r=rule_id, f=fine, a=allowed, d=month_start)

        with_ids('Users', 'INSERT INTO Users (id, username, password, user_role) VALUES (:id, :u, :p, :r)',
                 [dict(id=p[0], u=p[2], p=p[3], r=p[4]) for p in PEOPLE] +
                 [dict(id=g[0], u=None, p=None, r=None) for g in GUESTS])
        with_ids('Employee', 'INSERT INTO Employee (id, name, salary, job_role_id, job_type, date_of_joining, '
                             'gender, user_id, is_guest) VALUES (:id, :n, :sal, :jr, :jt, :doj, :g, :id, :guest)',
                 [dict(id=p[0], n=p[1], sal=150000 if p[4] != 'Employee' else 60000, jr=p[5], jt=p[6],
                       doj=date(2024, 1, 15), g=p[7], guest=0) for p in PEOPLE] +
                 [dict(id=g[0], n=g[1], sal=None, jr=None, jt=None, doj=None, g=None, guest=1) for g in GUESTS])

        special = [s[0] for s in SECTIONS if s[3] == 1]
        for pid, _, _, _, role, _, _, _, sections, productivity in PEOPLE:
            if role == 'Admin':
                continue
            for sid in sections + special:
                run('INSERT INTO EmployeeSection (employee_id, section_id, date_time) VALUES (:e, :s, :d)',
                    e=pid, s=sid, d=date(2024, 1, 15))
            run('INSERT INTO EmployeeProductivity (employee_id, productivity, productivity_month) '
                'VALUES (:e, :p, :m)', e=pid, p=productivity, m=month_start)
            folder = os.path.join('EmployeeImages', str(pid))
            if os.path.isdir(folder):
                for f in sorted(os.listdir(folder)):
                    run('INSERT INTO EmployeeImages (employee_id, image_url) VALUES (:e, :u)', e=pid, u=f)
            # Attendance on weekdays, with a few absences
            for i, d in enumerate(weekdays_until_today()):
                if (i + pid) % 7 == 0:
                    continue
                run('INSERT INTO Attendance (check_in, check_out, attendance_date, employee_id) '
                    'VALUES (:ci, :co, :d, :e)', ci=time(9, (pid * 3) % 20), co=time(17, 5), d=d, e=pid)

        for gid, _ in GUESTS:
            folder = os.path.join('EmployeeImages', str(gid))
            if os.path.isdir(folder):
                for f in sorted(os.listdir(folder)):
                    run('INSERT INTO EmployeeImages (employee_id, image_url) VALUES (:e, :u)', e=gid, u=f)

        for eid, rule_id, offset, start, end, image in VIOLATIONS:
            vdate = min(month_start + timedelta(days=offset), today)
            vid = c.execute(text('INSERT INTO Violation (employee_id, rule_id, date, start_time, end_time) '
                                 'OUTPUT INSERTED.id VALUES (:e, :r, :d, :s, :en)'),
                            dict(e=eid, r=rule_id, d=vdate, s=start, en=end)).scalar()
            run('INSERT INTO ViolationImages (violation_id, image_url, capture_time) VALUES (:v, :u, :t)',
                v=vid, u=image, t=start)

        with_ids('RawMaterial', 'INSERT INTO RawMaterial (id, name) VALUES (:id, :n)',
                 [dict(id=i, n=n) for i, n in RAW_MATERIALS])
        for num, rm, qty, price, ago in STOCK:
            run('INSERT INTO Stock (stock_number, raw_material_id, quantity, price_per_kg, purchased_date) '
                'VALUES (:n, :r, :q, :p, :d)', n=num, r=rm, q=qty, p=price, d=today - timedelta(days=ago))
        for num, name, angles in PRODUCTS:
            run('INSERT INTO Product (product_number, name, inspection_angles) VALUES (:n, :m, :a)',
                n=num, m=name, a=angles)
        for prod, rm, qty, unit in FORMULAS:
            run('INSERT INTO ProductFormula (product_number, raw_material_id, quantity, unit) '
                'VALUES (:p, :r, :q, :u)', p=prod, r=rm, q=qty, u=unit)
        with_ids('ProductLink', 'INSERT INTO ProductLink (id, packs_per_batch, piece_per_pack, rejection_tolerance, '
                                'product_number) VALUES (:id, :pk, :pp, :rt, :p)',
                 [dict(id=i, p=p, pk=pk, pp=pp, rt=rt) for i, p, pk, pp, rt in LINKS])
        for num, link, ago, yld, defected in BATCHES:
            run('INSERT INTO Batch (batch_number, product_link_id, manufacturing_date, batch_yield, defected_pieces) '
                'VALUES (:n, :l, :d, :y, :df)', n=num, l=link, d=today - timedelta(days=ago), y=yld, df=defected)
            run('INSERT INTO StockInBatch (stock_number, batch_number) VALUES (:s, :b)',
                s='Cas#01092026080000' if link in (1, 2) else 'PET#03092026080000', b=num)

    print('Demo data seeded. Logins:')
    for p in PEOPLE:
        print(f'  {p[4]:<11} {p[2]:<10} / {p[3]}')


if __name__ == '__main__':
    main()
