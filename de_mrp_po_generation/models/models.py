from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import format_date
from odoo.exceptions import UserError
from datetime import datetime
from odoo.exceptions import Warning



class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    
    
    def action_confirm(self):

        res = super(SaleOrder, self).action_confirm()
        vals = {
            'date': fields.Date.today(),
            'sale_id': self.id,
        }
        document = self.env['mrp.mo.beforehand'].create(vals)
        document.get_sheet_lines()
        document.action_generate_po()
        document.action_done()
        return res
    
    
    



class MoBeforhand(models.Model):
    _name = 'mrp.mo.beforehand'
    _description = 'Create PO from MO'
    _order = 'name desc, id desc'
    
    
    def material_planning(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'binding_type': 'action',
#             'multi': False,
            'name': 'Material Planning',
            'domain': [('mo_id','=', self.id)],
            'target': 'current',
            'res_model': 'mrp.mo.beforehand.line',
            'view_mode': 'tree,form',
        }
    
    
    @api.model
    def create(self,vals):
        if vals.get('name',_('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('mrp.mo.beforehand') or _('New')    
        res = super(MoBeforhand,self).create(vals)
        return res
    
    
    def unlink(self):
        for leave in self:
            if leave.state in ('process','done'):
                raise UserError(_('You cannot delete an Document  which is not draft or cancelled. '))
     
            return super(MoBeforhand, self).unlink()


   

    def get_sheet_lines(self):
#         datas[:] = [] 
        for rec in self:
            rec.mo_line_ids.unlink()
            order_data = self.env['mrp.production'].search([('sale_id', '=', rec.sale_id.name),('product_id.name', '=ilike', '[Un-Finished]%')])
            data = []
            for order in order_data:
                for line in order.move_raw_ids:
                    vendor_data = [] 
                    if not '[Cut Material]' in line.product_id.name:
                        product_vendor = self.env['product.product'].search([('name','=',line.product_id.name)])
                        for product in product_vendor:
                            for vendor in product.seller_ids:
                                vendor_data.append(vendor.name.id)
                    
                    line_data = [] 
                    if not '[Cut Material]' in line.product_id.name:
                        bom_produt = self.env['mrp.bom'].search([('product_id','=',line.product_id.id)])
                        for product in bom_produt:
                            for subcontractor in product.subcontractor_ids:
                                line_data.append(subcontractor.id)
                        if  line_data:       
                            data.append((0,0,{
                                        'mo_id': self.id,
                                        'po_process': True, 
                                         'product_id': line.product_id.id,
                                        'product_uom_qty_so': line.product_uom_qty,
                                        'seller_ids':  line_data,
                                        'product_uom_qty_order': line.product_uom_qty,
                                        'on_hand_qty':line.product_id.qty_available,
                                        'forcast_qty': line.product_id.virtual_available,
                                        'partner_id': line_data[0],
                                 }))
                        else:
                            data.append((0,0,{
                                        'mo_id': self.id,
                                        'po_process': True, 
                                         'product_id': line.product_id.id,
                                        'product_uom_qty_so': line.product_uom_qty,
                                        'seller_ids':  line_data,
                                        'product_uom_qty_order': line.product_uom_qty,
                                        'on_hand_qty':line.product_id.qty_available,
                                        'forcast_qty': line.product_id.virtual_available,
                                    }))


                        
            rec.mo_line_ids = data
            self.write ({
                'state': 'process'
            })
            
    def action_generate_po(self):
        for line in self.mo_line_ids:
            if line.partner_id:
                pass
            else:
                raise UserError(_('Please Select Vendor for all selected lines.'))
        vendor_list = []
        for line in self.mo_line_ids:
            if line.partner_id and line.po_created == False:
                vendor_list.append(line.partner_id)
            else:
                pass
        list = set(vendor_list)
        for te in list:
            product = []
            for re in self.mo_line_ids:
                if te == re.partner_id:
                    if re.po_created == False:
                        valss = {
                            'product_id': re.product_id.id,
                            'name': re.product_id.name,
                            'product_uom_qty': re.product_uom_qty_order,
                            'price_unit': re.product_id.standard_price,
                            'date_planned': fields.Date.today(),
                            'product_uom': re.product_id.uom_po_id.id,
                        }
                        product.append(valss)
            vals = {
                  'partner_id': te.id,
                  'date_order': fields.Date.today(),
                  'sale_ref_id': self.sale_id.name,
                  'origin': self.name,
                    }
            order = self.env['purchase.order'].create(vals)
            for test in product:
                order_line = {
                       'order_id': order.id,
                       'product_id': test['product_id'],
                       'name': test['name'],
                       'product_qty': test['product_uom_qty'],
                       'price_unit': test['price_unit'],
                       'date_planned': fields.Date.today(),
                       'product_uom': test['product_uom'],
                        }
                orders_lines = self.env['purchase.order.line'].create(order_line)
        for line in self.mo_line_ids:
            if line.po_process == True and not line.partner_id==' ':
                line.update ({
                   'po_process': False,
                    'po_created': True,
                  	})
                        
            
            
            
            


            
    def action_approve(self):
        self.state = 'approved'

    def action_done(self):
        sum = 0
        cout_sum = 0
        for line in self.mo_line_ids:
            sum = sum + 1            
            if line.po_created == True and  not line.partner_id==' ':
                cout_sum = cout_sum + 1                
        if  sum == cout_sum:        
            self.state = 'done'
        else:
            raise UserError(_('Please Create Purchase Order of all Material Planning Lines.'))


    

    name = fields.Char(
        'Reference', copy=False, readonly=True, default=lambda x: _('New'))
    date = fields.Date(string='Date', required=True)
    sale_id = fields.Many2one('sale.order',string="Ref Sale", required=True)
    mo_line_ids = fields.One2many('mrp.mo.beforehand.line','mo_id',string="Manufacturing Order")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('process', 'Process'),
        ('done', 'done')],
        readonly=True, string='State', default='draft')
    
    
    

    
  


    
    
    
class MoBeforhandWizardLine(models.Model):
    _name = 'mrp.mo.beforehand.line'
    _description = 'Create PO from MO'
    
    
    def unlink(self):
        for leave in self:
            if leave.po_created == True   or leave.po_process == True:
                raise UserError(_('You cannot delete an order'))
     
            return super(MoBeforhandWizardLine, self).unlink()
     
                
                
    po_process = fields.Boolean(string='Select')
    po_created = fields.Boolean(string='PO Created')
    product_id = fields.Many2one('product.product',string="Product")
    seller_ids = fields.Many2many('res.partner', string='Vendor list')
    product_uom_qty_so = fields.Float(string='Quantity Required in SO')
    product_uom_qty_order = fields.Float(string='Quantity to Order')
    on_hand_qty = fields.Float(string="Quantity On Hand")
    forcast_qty = fields.Float(string="Forcast Quantity")
    mo_id = fields.Many2one('mrp.mo.beforehand',string="Document")
    partner_id = fields.Many2one('res.partner', string="Vendor",domain="[('id', 'in', seller_ids)]")
    
#  domain=lambda self: [('id', 'in', seller_ids)]

    @api.constrains('product_uom_qty_order')
    def product_uom_qty_order_val(self):
        for qty in self:
            if qty.product_uom_qty_order > qty.product_uom_qty_so:
                raise Warning("You can't add Quantity to Order Greater than:" + str(qty.product_uom_qty_so) + " "+"For Product"+ " "+ str(qty.product_id.name)) 
    
    def action_update_vendor(self):
        for line in self:
#         order_data = self.env['mrp.production'].search([('sale_id', '=', self.mo_id.sale_id.name),('product_id.name', '=ilike', '[Un-Finished]%')])
#         for order in order_data:
#             for line in order.move_raw_ids:
            line_data = [] 
    #         if not '[Cut Material]' in line.product_id.name:
            bom_produt = self.env['mrp.bom'].search([('product_id','=',line.product_id.id)])
            for product in bom_produt:
                for subcontractor in product.subcontractor_ids:
                    line_data.append(subcontractor.id)
            line.update ({
                'seller_ids': line_data,
                })
    
    
    def action_generate_po(self):
        for line in self:
            if line.partner_id:
                pass
            else:
                raise UserError(_('Please Select Vendor for all selected lines.'))
        vendor_list = []
        for line in self:
            if line.partner_id and line.po_created == False:
                vendor_list.append(line.partner_id)
            else:
                pass
        list = set(vendor_list)
        for te in list:
            product = []
            for re in self:
                if te == re.partner_id:
                    if re.po_created == False:
                        valss = {
                            'product_id': re.product_id.id,
                            'name': re.product_id.name,
                            'product_uom_qty': re.product_uom_qty_order,
                            'price_unit': re.product_id.standard_price,
                            'date_planned': fields.Date.today(),
                            'product_uom': re.product_id.uom_po_id.id,
                        }
                        product.append(valss)
            vals = {
                  'partner_id': te.id,
                  'date_order': fields.Date.today(),
                  'sale_ref_id': self.mo_id.sale_id.name,
                  'origin': self.mo_id.name,
                    }
            order = self.env['purchase.order'].create(vals)
            for test in product:
                order_line = {
                       'order_id': order.id,
                       'product_id': test['product_id'],
                       'name': test['name'],
                       'product_qty': test['product_uom_qty'],
                       'price_unit': test['price_unit'],
                       'date_planned': fields.Date.today(),
                       'product_uom': test['product_uom'],
                        }
                orders_lines = self.env['purchase.order.line'].create(order_line)
        for line in self:
            if line.po_process == True and not line.partner_id==' ':
                line.update ({
                   'po_process': False,
                    'po_created': True,
                  	})
                
                
                
                



