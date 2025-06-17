{
    'name': 'Hospitals Management System (HMS)',
    'version': '1.0',
    'summary': 'Manage hospital patients data',
    'description': 'Track patient records, medical history, and more.',
    'depends': ['base', 'mail', 'crm'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/patient_views.xml',
        'views/doctor_views.xml',
        'views/department_views.xml',
        'views/menu.xml',
        'reports/reports.xml',
        'reports/patient_report.xml',
    ],
    'installable': True,
    'application': True,
}
