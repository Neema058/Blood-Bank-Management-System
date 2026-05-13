from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from donors.models import Donor
from donations.models import Donation
from inventory.models import BloodUnit, BLOOD_GROUPS
from patients.models import Patient
from blood_requests.models import BloodRequest
import datetime, io

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

RED   = colors.HexColor('#C0392B')
DRED  = colors.HexColor('#922B21')
PINK  = colors.HexColor('#FADBD8')
WHITE = colors.white
GRAY  = colors.HexColor('#888888')

REPORT_ROLES = ('admin', 'lab_technician')

def _check_report_access(request):
    if request.user.role == 'patient':
        return redirect('/patient-portal/')
    if request.user.role not in REPORT_ROLES:
        messages.error(request, 'Access denied! Only Admin and Lab Technician can view reports.')
        return redirect('/dashboard/')
    return None

def make_pdf_response(filename):
    resp = HttpResponse(content_type='application/pdf')
    resp['Content-Disposition'] = f'attachment; filename="{filename}"'
    return resp

def table_style(header_bg=PINK):
    return TableStyle([
        ('BACKGROUND', (0,0), (-1,0), header_bg),
        ('TEXTCOLOR',  (0,0), (-1,0), DRED),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,0), 9),
        ('FONTNAME',   (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE',   (0,1), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, colors.HexColor('#FEF9F9')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E8A0A0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 6),
    ])

def pdf_header(story, title, subtitle='Blood Bank Management System'):
    styles = getSampleStyleSheet()
    story.append(Paragraph(f'<font color="#922B21"><b>🩸 {subtitle}</b></font>',
        ParagraphStyle('sub', fontSize=11, textColor=DRED, spaceAfter=4)))
    story.append(Paragraph(f'<font color="#C0392B"><b>{title}</b></font>',
        ParagraphStyle('title', fontSize=16, textColor=RED, spaceAfter=4)))
    story.append(Paragraph(f'Generated: {datetime.datetime.now().strftime("%d %B %Y, %H:%M")}',
        ParagraphStyle('date', fontSize=8, textColor=GRAY, spaceAfter=12)))
    story.append(Spacer(1, 0.2*cm))

@login_required
def reports_home(request):
    denied = _check_report_access(request)
    if denied:
        return denied
    return render(request, 'reports/home.html')

# ── Donor Report ──────────────────────────────────────────
@login_required
def donor_report(request):
    denied = _check_report_access(request)
    if denied:
        return denied
    donors = Donor.objects.filter(is_active=True).order_by('blood_group', 'full_name')
    if request.GET.get('export') == 'pdf':
        resp = make_pdf_response('Donor_Report.pdf')
        buf  = io.BytesIO()
        doc  = SimpleDocTemplate(buf, pagesize=landscape(A4), topMargin=1*cm, bottomMargin=1*cm)
        story = []
        pdf_header(story, 'Donor Report')
        data = [['#','Donor ID','Name','Blood Group','Age','Gender','Phone','Last Donation','Eligible']]
        for i, d in enumerate(donors, 1):
            data.append([
                str(i), str(d.donor_id), d.full_name, d.blood_group,
                str(d.age), d.get_gender_display(), d.phone,
                str(d.last_donation or 'Never'),
                'Yes' if d.is_eligible() else f'No ({d.days_until_eligible()}d)',
            ])
        t = Table(data, colWidths=[1*cm,1.5*cm,4*cm,2*cm,1.5*cm,2*cm,2.5*cm,3*cm,2.5*cm])
        t.setStyle(table_style())
        story.append(t)
        doc.build(story)
        resp.write(buf.getvalue())
        return resp
    return render(request, 'reports/donors.html', {'donors': donors})

# ── Inventory Report ──────────────────────────────────────
@login_required
def inventory_report(request):
    denied = _check_report_access(request)
    if denied:
        return denied
    BloodUnit.auto_expire()
    units = BloodUnit.objects.all().order_by('blood_group', 'expiry_date')
    status_f = request.GET.get('status', '')
    if status_f:
        units = units.filter(status=status_f)

    if request.GET.get('export') == 'pdf':
        resp = make_pdf_response('Inventory_Report.pdf')
        buf  = io.BytesIO()
        doc  = SimpleDocTemplate(buf, pagesize=landscape(A4), topMargin=1*cm, bottomMargin=1*cm)
        story = []
        pdf_header(story, 'Blood Inventory Report')
        data = [['#','Unit ID','Blood Group','Collected','Expiry','Days Left','Status']]
        for i, u in enumerate(units, 1):
            days = u.days_to_expiry()
            data.append([
                str(i), str(u.id), u.blood_group,
                str(u.collected_date), str(u.expiry_date),
                str(days) if days >= 0 else 'EXPIRED',
                u.get_status_display(),
            ])
        t = Table(data, colWidths=[1*cm,1.5*cm,2.5*cm,3*cm,3*cm,2.5*cm,2.5*cm])
        t.setStyle(table_style())
        story.append(t)
        doc.build(story)
        resp.write(buf.getvalue())
        return resp
    return render(request, 'reports/inventory.html', {'units': units, 'status_f': status_f})

# ── Request Report ────────────────────────────────────────
@login_required
def request_report(request):
    denied = _check_report_access(request)
    if denied:
        return denied
    reqs = BloodRequest.objects.all().order_by('-request_date')
    if request.GET.get('export') == 'pdf':
        resp = make_pdf_response('Request_Report.pdf')
        buf  = io.BytesIO()
        doc  = SimpleDocTemplate(buf, pagesize=landscape(A4), topMargin=1*cm, bottomMargin=1*cm)
        story = []
        pdf_header(story, 'Blood Request Report')
        data = [['#','Req#','Patient','Blood Group','Units','Urgency','Status','Date']]
        for i, r in enumerate(reqs, 1):
            data.append([
                str(i), str(r.id), r.patient.full_name, r.blood_group,
                str(r.units_required), r.get_urgency_display(),
                r.get_status_display(), r.request_date.strftime('%d-%m-%Y'),
            ])
        t = Table(data, colWidths=[1*cm,1.2*cm,4*cm,2*cm,1.5*cm,2*cm,2*cm,2.5*cm])
        t.setStyle(table_style())
        story.append(t)
        doc.build(story)
        resp.write(buf.getvalue())
        return resp
    return render(request, 'reports/requests.html', {'reqs': reqs})

# ── Monthly Summary ───────────────────────────────────────
@login_required
def monthly_report(request):
    denied = _check_report_access(request)
    if denied:
        return denied
    year = int(request.GET.get('year', datetime.date.today().year))
    data = []
    for m in range(1, 13):
        don  = Donation.objects.filter(donation_date__year=year, donation_date__month=m, status='accepted').count()
        req  = BloodRequest.objects.filter(request_date__year=year, request_date__month=m).count()
        ful  = BloodRequest.objects.filter(request_date__year=year, request_date__month=m, status='fulfilled').count()
        data.append({'month': datetime.date(year, m, 1).strftime('%B'), 'donations': don, 'requests': req, 'fulfilled': ful})
    return render(request, 'reports/monthly.html', {'data': data, 'year': year})
