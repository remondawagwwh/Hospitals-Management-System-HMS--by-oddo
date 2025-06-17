from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class HMSPatientLog(models.Model):
    _name = 'hms.patient.log'
    _description = 'Patient Log History'
    _order = 'date desc'

    created_by = fields.Many2one(
        'res.users',
        string='Created By',
        default=lambda self: self.env.user,
        readonly=True
    )
    date = fields.Datetime(
        string='Date',
        default=lambda self: fields.Datetime.now(),
        readonly=True
    )
    description = fields.Text(
        string='Description',
        required=True
    )
    patient_id = fields.Many2one(
        'hms.patient',
        string='Patient',
        ondelete='cascade',
        required=True
    )

class ResPartner(models.Model):
    _inherit = 'res.partner'
    _order = 'name asc'
    _sql_constraints = [
        ('email_uniq', 'UNIQUE(email, related_patient_id)',
         'Email must be unique per patient!'),
    ]

    related_patient_id = fields.Many2one(
        'hms.patient',
        string='Related Patient',
        tracking=True,
        help="Link to Hospital Management System patient record"
    )
    vat = fields.Char(
        string='Tax ID',
        required=True,
        tracking=True
    )

    @api.constrains('related_patient_id', 'email')
    def _check_patient_email_uniqueness(self):
        for partner in self:
            if partner.related_patient_id and partner.email:
                existing = self.search([
                    ('email', '=', partner.email),
                    ('related_patient_id', '!=', False),
                    ('id', '!=', partner.id)
                ], limit=1)
                if existing:
                    raise ValidationError(
                        "Email already linked to another patient!\n"
                        "Patient: %s\nPartner: %s" %
                        (existing.related_patient_id.name, existing.name)
                    )

    def unlink(self):
        protected_partners = self.filtered(lambda p: p.related_patient_id)
        if protected_partners:
            raise UserError(
                "Cannot delete partners linked to patients:\n%s" %
                "\n".join(p.name for p in protected_partners)
            )
        return super().unlink()

    def write(self, vals):
        if 'email' in vals and self.related_patient_id:
            self.related_patient_id.email = vals['email']
        return super().write(vals)

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        return res