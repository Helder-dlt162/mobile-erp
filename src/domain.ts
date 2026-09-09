import { Boxes, Factory, LayoutDashboard, Truck, Users } from 'lucide-react'

export type Section = 'Visão geral' | 'Produção' | 'Estoque' | 'Movimentações' | 'Nota fiscal de entrada' | 'Nota fiscal de venda' | 'Fornecedores' | 'Clientes' | 'Contas a pagar' | 'Configurações' | 'Usuários' | 'Funcionários'
export type OrderStatus = 'Em produção' | 'Aguardando' | 'Concluída'

export interface ProductionOrder { id: string; product: string; quantity: number; progress: number; station: string; due: string; status: OrderStatus }
export interface InventoryItem { id: number; name: string; sku: string; stock: number; unit: string; minimum_stock: number; state: string; color: string; last_entry: string }
export interface DashboardData { production_month: number; occupancy: number; average_cost: number; contribution_margin: number; orders: Array<{ code: string; product: string; quantity: number; progress: number; station: string; due: string; status: OrderStatus }>; inventory: InventoryItem[] }
export interface InvoiceItem { id: number; sku: string; description: string; quantity: number; unit_cost: number; total: number }
export interface PurchaseInvoice { id: number; number: string; supplier: string; issue_date: string; due_date: string; payment_method: string; description: string; barcode: string; category: string; notes: string; status: string; total: number; items: InvoiceItem[] }
export interface Partner { id: number; document: string; legal_name: string; trade_name: string; email: string; phone: string; address: string; city: string; state: string; zip_code: string }
export interface StockMovement { id: number; inventory_item_id: number; movement_type: 'Entrada' | 'Saída'; quantity: number; reason: string; reference: string; movement_date: string; item_name: string; sku: string }
export interface AppSetting { category: string; payload: Record<string, string | number | boolean> }
export interface AppUser { id: number; name: string; email: string; role: string; permissions: string[] }

export const demoOrders: ProductionOrder[] = [
  { id: 'OP-2408', product: 'Cadeira Lina · Natural', quantity: 180, progress: 72, station: 'Montagem', due: 'Hoje, 16:00', status: 'Em produção' },
  { id: 'OP-2407', product: 'Banqueta Oca · Nogueira', quantity: 96, progress: 41, station: 'Usinagem', due: 'Amanhã, 10:00', status: 'Em produção' },
  { id: 'OP-2406', product: 'Cadeira Lina · Preta', quantity: 240, progress: 100, station: 'Expedição', due: 'Concluída', status: 'Concluída' },
  { id: 'OP-2405', product: 'Banqueta Oca · Natural', quantity: 120, progress: 0, station: 'Corte', due: '12 set, 08:00', status: 'Aguardando' },
]

export const demoInventory: InventoryItem[] = [
  { id: 1, name: 'Madeira Tauari · 25 mm', sku: 'MAT-001', stock: 18.4, unit: 'm³', minimum_stock: 8, state: 'Normal', color: 'green', last_entry: '08 set' },
  { id: 2, name: 'Espuma D28 · 40 mm', sku: 'MAT-024', stock: 132, unit: 'un', minimum_stock: 60, state: 'Normal', color: 'green', last_entry: '08 set' },
  { id: 3, name: 'Tecido Linho Cru', sku: 'MAT-017', stock: 38, unit: 'm', minimum_stock: 30, state: 'Repor em breve', color: 'yellow', last_entry: '08 set' },
  { id: 4, name: 'Verniz PU Acetinado', sku: 'MAT-031', stock: 12, unit: 'L', minimum_stock: 20, state: 'Abaixo do mínimo', color: 'red', last_entry: '08 set' },
]

export const navItems: { label: Section; icon: typeof LayoutDashboard }[] = [
  { label: 'Visão geral', icon: LayoutDashboard }, { label: 'Produção', icon: Factory }, { label: 'Estoque', icon: Boxes }, { label: 'Fornecedores', icon: Truck }, { label: 'Clientes', icon: Users },
]

export function mapOrders(data: DashboardData['orders']): ProductionOrder[] { return data.map((order) => ({ id: order.code, product: order.product, quantity: order.quantity, progress: order.progress, station: order.station, due: order.due, status: order.status })) }
export function inventoryLevel(item: InventoryItem) { return item.minimum_stock > 0 ? Math.min(100, Math.round((item.stock / (item.minimum_stock * 2)) * 100)) : 100 }
export function formatBRL(value: number) { return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) }
