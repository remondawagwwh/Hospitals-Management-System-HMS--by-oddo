from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date


class Patient(models.Model):
    _name = 'hms.patient'
    _description = 'Hospital Patient'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'first_name'

    first_name = fields.Char(required=True)
    last_name = fields.Char(required=True)
    birth_date = fields.Date()
    age = fields.Integer(compute='_compute_age', store=True)
    blood_type = fields.Selection([
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ])
    pcr = fields.Boolean()
    cr_ratio = fields.Float(string="CR Ratio")
    image = fields.Binary()
    history = fields.Html()
    address = fields.Text()
    email = fields.Char(unique=True)
    department_id = fields.Many2one('hms.department')
    department_capacity = fields.Integer(related='department_id.capacity', string="Department Capacity")
    doctor_ids = fields.Many2many('hms.doctor', string="Doctors")
    state = fields.Selection([
        ('undetermined', 'Undetermined'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('serious', 'Serious'),
    ], default='undetermined')
    log_history_ids = fields.One2many('hms.patient.log', 'patient_id')
    related_partner_id = fields.Many2one('res.partner')

    @api.depends('birth_date')
    def _compute_age(self):
        for rec in self:
            if rec.birth_date:
                today = date.today()
                rec.age = today.year - rec.birth_date.year - (
                            (today.month, today.day) < (rec.birth_date.month, rec.birth_date.day))
            else:
                rec.age = 0

    @api.onchange('pcr')
    def _onchange_pcr(self):
        if self.pcr and not self.cr_ratio:
            return {
                'warning': {
                    'title': _("Warning"),
                    'message': _("CR Ratio is required when PCR is checked")
                }
            }

    @api.onchange('age')
    def _onchange_age(self):
        if self.age < 30:
            self.pcr = True
            return {
                'warning': {
                    'title': _("Warning"),
                    'message': _("PCR has been automatically checked for patients under 30")
                }
            }

    @api.constrains('email')
    def _check_email(self):
        for rec in self:
            if rec.email and not '@' in rec.email:
                raise ValidationError(_("Please enter a valid email address"))

    @api.constrains('department_id')
    def _check_department(self):
        for rec in self:
            if rec.department_id and not rec.department_id.is_opened:
                raise ValidationError(_("Cannot select a closed department"))

    def write(self, vals):
        if 'state' in vals:
            for rec in self:
                self.env['hms.patient.log'].create({
                    'patient_id': rec.id,
                    'description': f"State changed to {vals['state']}"
                })
        return super().write(vals)