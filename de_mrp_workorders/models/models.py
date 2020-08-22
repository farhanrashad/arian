# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'
    
    qty_f_production = fields.Float('Original Production Quantity', readonly=True)







class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
   
    routing_f_id = fields.Many2one(
        'mrp.routing', srting='First Routing', store=True)
    routing_s_id = fields.Many2one(
        'mrp.routing', string='Second Routing', store=True)
    routing_t_id = fields.Many2one(
        'mrp.routing', string='Third Routing', store=True)
    routing_fo_id = fields.Many2one(
        'mrp.routing', string='Four Routing', store=True)
    product_f_qty = fields.Float(string='First Routing Quantity')
    product_s_qty = fields.Float(string='Second Routing Quantity')
    product_t_qty = fields.Float(string='Third Routing Quantity')
    product_fo_qty = fields.Float(string='Four Routing Quantity')
    
    
                
    def button_plans(self):      
        if self.routing_f_id != '' and self.product_f_qty != 0.0:
            work_order_line = self.env['mrp.workorder.line']
            
            quantity = max(self.product_f_qty - sum(self.move_finished_ids.filtered(lambda move: move.product_id == self.product_id).mapped('quantity_done')), 0)
            quantity = self.product_id.uom_id._compute_quantity(quantity, self.product_uom_id)
            for line in self.move_raw_ids:
                flines = {
                    'product_id': line.product_id.id,
                    'qty_to_consume': self.product_f_qty,
                    'qty_reserved': self.product_f_qty,
                    'qty_done': self.product_f_qty,
                    
                }
        
#                 workorder_lines = work_order_line.create(flines)
            fval = {
                'name': self.name,
                'production_id': self.id,
                'workcenter_id': self.routing_f_id.id,
#                 'qty_production': self.product_f_qty,
                'date_planned_start': self.date_planned_start,
                'date_planned_finished': self.date_planned_start,                             
                'product_uom_id': self.product_id.uom_id.id,
                'operation_id': self.routing_f_id.operation_ids.id,
                'duration_expected': self.routing_f_id.operation_ids.time_cycle,
                'state':'ready' or 'pending',
                'qty_f_production': self.product_f_qty,
                'qty_remaining': self.product_f_qty,                            
                'qty_producing': quantity,
                'consumption': self.bom_id.consumption,
                 'raw_workorder_line_ids': [(0, 0, flines)]
                
            }
            workorders = self.env['mrp.workorder'].create(fval)
        else:
            pass
            
        if self.routing_s_id != '' and self.product_s_qty != 0.0:
            work_orders_line = self.env['mrp.workorder.line']
            quantity = max(self.product_s_qty - sum(self.move_finished_ids.filtered(lambda move: move.product_id == self.product_id).mapped('quantity_done')), 0)
            quantity = self.product_id.uom_id._compute_quantity(quantity, self.product_uom_id)
            for line in self.move_raw_ids:
                slines = {
                    'product_id': line.product_id.id,
                    'qty_to_consume': self.product_s_qty,
                    'qty_reserved': self.product_s_qty,
                    'qty_done': self.product_s_qty,
                }
#                 workorder_lines = work_orders_line.create(slines)
            sval = {
                'name': self.name,
                'production_id': self.id,
                'workcenter_id': self.routing_s_id.id,
                'date_planned_start': self.date_planned_start,
                'date_planned_finished': self.date_planned_start,             
                'product_uom_id': self.product_id.uom_id.id,
                'operation_id': self.routing_s_id.operation_ids.id,
                'duration_expected': self.routing_s_id.operation_ids.time_cycle,
                'state':'ready' or 'pending',
                'qty_f_production': self.product_s_qty,
                'qty_remaining': self.product_s_qty,               
                'qty_producing': quantity,
                'consumption': self.bom_id.consumption,
                 'raw_workorder_line_ids': [(0, 0, slines)]
                
            }
            workorders = self.env['mrp.workorder'].create(sval)
        else:
            pass

        if self.routing_t_id != '' and self.product_t_qty != 0.0:
            work_ordert_line = self.env['mrp.workorder.line']
            quantity = max(self.product_t_qty - sum(self.move_finished_ids.filtered(lambda move: move.product_id == self.product_id).mapped('quantity_done')), 0)
            quantity = self.product_id.uom_id._compute_quantity(quantity, self.product_uom_id)
            for line in self.move_raw_ids:
                tlines = {
                    'product_id': line.product_id.id,
                    'qty_to_consume': self.product_t_qty,
                    'qty_reserved': self.product_t_qty,
                    'qty_done': self.product_t_qty,
                }
#                 workorder_lines = work_ordert_line.create(tlines)
            tval = {
                'name': self.name,
                'production_id': self.id,
                'workcenter_id': self.routing_t_id.id,
                'date_planned_start': self.date_planned_start,
                'date_planned_finished': self.date_planned_start,                           
                'product_uom_id': self.product_id.uom_id.id,
                'operation_id': self.routing_t_id.operation_ids.id,
                'duration_expected': self.routing_t_id.operation_ids.time_cycle,
                'state':'ready' or 'pending',
                'qty_f_production': self.product_t_qty, 
                'qty_remaining': self.product_t_qty,               
                'qty_producing': quantity,
                'consumption': self.bom_id.consumption,
                 'raw_workorder_line_ids': [(0, 0, tlines)]
            }
            workorders = self.env['mrp.workorder'].create(tval)
        else:
            pass
            
        if self.routing_fo_id != '' and self.product_fo_qty != 0.0:
            work_orderfo_line = self.env['mrp.workorder.line']
            quantity = max(self.product_fo_qty - sum(self.move_finished_ids.filtered(lambda move: move.product_id == self.product_id).mapped('quantity_done')), 0)
            quantity = self.product_id.uom_id._compute_quantity(quantity, self.product_uom_id)
            for line in self.move_raw_ids:
                folines = {
                    'product_id': line.product_id.id,
                    'qty_to_consume': self.product_fo_qty,
                    'qty_reserved': self.product_fo_qty,
                    'qty_done': self.product_fo_qty,                   
                }
#                 workorder_lines = work_orderfo_line.create(folines)
            foval = {
                'name': self.name,
                'production_id': self.id,
                'workcenter_id': self.routing_fo_id.id,
                'date_planned_start': self.date_planned_start,
                'date_planned_finished': self.date_planned_start,             
                'product_uom_id': self.product_id.uom_id.id,
                'operation_id': self.routing_fo_id.operation_ids.id,
                'duration_expected': self.routing_fo_id.operation_ids.time_cycle,
                'state':'ready' or 'pending',
#                 'qty_production': self.product_fo_qty,
                 'qty_f_production': self.product_fo_qty, 
                 'qty_remaining': self.product_fo_qty,               
                'qty_producing': quantity,
                'consumption': self.bom_id.consumption,
                'raw_workorder_line_ids': [(0, 0, folines)]
            } 
            workorders = self.env['mrp.workorder'].create(foval)
        else:
            pass
        
    
#     def _prepare_workorder_vals(self, operation, workorders, quantity):
#         self.ensure_one()
#         data = {
#             'name': operation.name,
#             'production_id': self.id,
#             'workcenter_id': operation.workcenter_id.id,
#             'product_uom_id': self.product_id.uom_id.id,
#             'operation_id': operation.id,
#             'state':'ready' or 'pending',
#             'qty_producing': quantity,
#             'consumption': self.bom_id.consumption,
#         }
#         return data
#     def action_confirm(self):
#         self._check_company()
#         for production in self:
#             if not production.move_raw_ids:
#                 raise UserError(_("Add some materials to consume before marking this MO as to do."))
#             for move_raw in production.move_raw_ids:
#                 move_raw.write({
#                     'unit_factor': move_raw.product_uom_qty / production.product_f_qty,
#                 })
#             production._generate_finished_moves()
#             production.move_raw_ids._adjust_procure_method()
#             (production.move_raw_ids | production.move_finished_ids)._action_confirm()
#         for production in self:
#             if not production.move_raw_ids:
#                 raise UserError(_("Add some materials to consume before marking this MO as to do."))
#             for move_raw in production.move_raw_ids:
#                 move_raw.write({
#                     'unit_factor': move_raw.product_uom_qty / production.product_f_qty,
#                 })
#             production._generate_finished_moves()
#             production.move_raw_ids._adjust_procure_method()
#             (production.move_raw_ids | production.move_finished_ids)._action_confirm()   
#         return True
