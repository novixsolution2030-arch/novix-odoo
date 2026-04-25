from odoo import models, fields, api, _

class NawaemReport(models.Model):
    _name = 'nawaem.report'
    _description = 'Reports between Clients and Providers'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    reporter_id = fields.Many2one('res.users', string='Reporter', required=True, tracking=True)
    reported_id = fields.Many2one('res.users', string='Reported Party', required=True, tracking=True)
    order_id = fields.Many2one('sale.order', string='Related Order', required=True)
    
    reason_type = fields.Selection([
        ('delay', 'Delay'),
        ('behavior', 'Bad Behavior'),
        ('service', 'Service Quality'),
        ('no_show', 'No Show'),
        ('other', 'Other'),
    ], string='Reason', required=True, tracking=True)

    description = fields.Text(string='Description')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'In Investigation'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ], default='draft', string='Status', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('nawaem.report') or _('New')
        return super(NawaemReport, self).create(vals)

    def action_investigate(self):
        self.ensure_one()
        self.state = 'open'

    def action_resolve(self):
        self.ensure_one()
        self.state = 'resolved'
