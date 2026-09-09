import { useMemo, useState } from 'react'
import { createRoot } from 'react-dom/client'
import {
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  BarChart3,
  Bell,
  Boxes,
  Calculator,
  ChevronRight,
  CircleDollarSign,
  ClipboardList,
  Factory,
  FileText,
  LayoutDashboard,
  Menu,
  PackageCheck,
  PanelLeftClose,
  PanelLeftOpen,
  Plus,
  Search,
  Settings2,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  Truck,
  X,
} from 'lucide-react'
import './styles.css'

type Section = 'Visão geral' | 'Produção' | 'Estoque' | 'Custos e preços'

type OrderStatus = 'Em produção' | 'Aguardando' | 'Concluída'

interface ProductionOrder {
  id: string
  product: string
  quantity: number
  progress: number
  station: string
  due: string
  status: OrderStatus
}

const orders: ProductionOrder[] = [
  { id: 'OP-2408', product: 'Cadeira Lina · Natural', quantity: 180, progress: 72, station: 'Montagem', due: 'Hoje, 16:00', status: 'Em produção' },
  { id: 'OP-2407', product: 'Banqueta Oca · Nogueira', quantity: 96, progress: 41, station: 'Usinagem', due: 'Amanhã, 10:00', status: 'Em produção' },
  { id: 'OP-2406', product: 'Cadeira Lina · Preta', quantity: 240, progress: 100, station: 'Expedição', due: 'Concluída', status: 'Concluída' },
  { id: 'OP-2405', product: 'Banqueta Oca · Natural', quantity: 120, progress: 0, station: 'Corte', due: '12 set, 08:00', status: 'Aguardando' },
]

const inventory = [
  { name: 'Madeira Tauari · 25 mm', sku: 'MAT-001', stock: '18,4 m³', level: 82, state: 'Normal', color: 'green' },
  { name: 'Espuma D28 · 40 mm', sku: 'MAT-024', stock: '132 un', level: 58, state: 'Normal', color: 'green' },
  { name: 'Tecido Linho Cru', sku: 'MAT-017', stock: '38 m', level: 23, state: 'Repor em breve', color: 'yellow' },
  { name: 'Verniz PU Acetinado', sku: 'MAT-031', stock: '12 L', level: 9, state: 'Abaixo do mínimo', color: 'red' },
]

const navItems: { label: Section; icon: typeof LayoutDashboard }[] = [
  { label: 'Visão geral', icon: LayoutDashboard },
  { label: 'Produção', icon: Factory },
  { label: 'Estoque', icon: Boxes },
  { label: 'Custos e preços', icon: CircleDollarSign },
]

function formatBRL(value: number) {
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function App() {
  const [section, setSection] = useState<Section>('Visão geral')
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [search, setSearch] = useState('')
  const [selectedLine, setSelectedLine] = useState('Todas as linhas')
  const [showNotifications, setShowNotifications] = useState(false)
  const [cost, setCost] = useState(148.5)
  const [margin, setMargin] = useState(32)
  const [tax, setTax] = useState(12.45)

  const filteredOrders = useMemo(() => {
    const term = search.toLowerCase().trim()
    if (!term) return orders
    return orders.filter((order) => `${order.id} ${order.product} ${order.station}`.toLowerCase().includes(term))
  }, [search])

  const salePrice = cost / (1 - (margin + tax) / 100)
  const contribution = salePrice - cost - salePrice * (tax / 100)

  return (
    <div className="app-shell">
      <aside className={`sidebar ${sidebarOpen ? 'is-open' : 'is-collapsed'}`}>
        <div className="brand-lockup">
          <div className="brand-mark"><Sparkles size={18} strokeWidth={2.5} /></div>
          {sidebarOpen && <div><strong>ATELIER</strong><span>INDUSTRIAL OS</span></div>}
        </div>
        <div className="workspace-switcher">
          <div className="workspace-avatar">AM</div>
          {sidebarOpen && <><div className="workspace-copy"><strong>Ateliê Móveis</strong><span>Unidade principal</span></div><ChevronRight size={15} /></>}
        </div>
        <nav className="main-nav" aria-label="Navegação principal">
          {navItems.map(({ label, icon: Icon }) => (
            <button key={label} className={`nav-item ${section === label ? 'active' : ''}`} onClick={() => setSection(label)} title={label}>
              <Icon size={18} />{sidebarOpen && <span>{label}</span>}{sidebarOpen && label === 'Estoque' && <span className="nav-badge">3</span>}
            </button>
          ))}
        </nav>
        {sidebarOpen && <div className="nav-label">Gestão</div>}
        <nav className="secondary-nav">
          <button className="nav-item" onClick={() => setSection('Produção')}><ClipboardList size={18} />{sidebarOpen && <span>Ordens de produção</span>}</button>
          <button className="nav-item" onClick={() => setSection('Estoque')}><PackageCheck size={18} />{sidebarOpen && <span>Movimentações</span>}</button>
          <button className="nav-item"><BarChart3 size={18} />{sidebarOpen && <span>Relatórios</span>}</button>
        </nav>
        <div className="sidebar-bottom">
          <button className="nav-item"><Settings2 size={18} />{sidebarOpen && <span>Configurações</span>}</button>
          <div className="profile-row"><div className="profile-avatar">RS</div>{sidebarOpen && <div className="workspace-copy"><strong>Rafael Silva</strong><span>Administrador</span></div>}</div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="topbar-left"><button className="icon-button menu-button" onClick={() => setSidebarOpen(!sidebarOpen)} aria-label="Alternar menu">{sidebarOpen ? <PanelLeftClose size={18} /> : <PanelLeftOpen size={18} />}</button><span className="breadcrumb">Operação <ChevronRight size={14} /> <strong>{section}</strong></span></div>
          <div className="topbar-actions"><div className="status-pill"><span className="status-dot" /> Sistema online</div><button className="icon-button notification-button" onClick={() => setShowNotifications(!showNotifications)} aria-label="Notificações"><Bell size={18} /><span /></button><div className="topbar-date">09 setembro 2026</div></div>
          {showNotifications && <div className="notification-popover"><div className="popover-heading"><strong>Notificações</strong><span>3 novas</span></div><div className="notification-item"><AlertTriangle size={16} /><div><strong>Verniz PU abaixo do mínimo</strong><small>Estoque · há 12 min</small></div></div><div className="notification-item"><Truck size={16} /><div><strong>Recebimento NF 02841 conferido</strong><small>Almoxarifado · há 42 min</small></div></div><div className="notification-item"><ShieldCheck size={16} /><div><strong>OP-2406 encerrada com sucesso</strong><small>Produção · há 1 h</small></div></div></div>}
        </header>

        <div className="page-wrap">
          {section === 'Visão geral' && <Overview onOpenProduction={() => setSection('Produção')} onOpenStock={() => setSection('Estoque')} selectedLine={selectedLine} setSelectedLine={setSelectedLine} />}
          {section === 'Produção' && <ProductionView search={search} setSearch={setSearch} filteredOrders={filteredOrders} />}
          {section === 'Estoque' && <StockView />}
          {section === 'Custos e preços' && <PricingView cost={cost} setCost={setCost} margin={margin} setMargin={setMargin} tax={tax} setTax={setTax} salePrice={salePrice} contribution={contribution} />}
        </div>
      </main>
    </div>
  )
}

function PageHeading({ eyebrow, title, description, action }: { eyebrow: string; title: string; description: string; action?: React.ReactNode }) {
  return <div className="page-heading"><div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{description}</p></div>{action}</div>
}

function Overview({ onOpenProduction, onOpenStock, selectedLine, setSelectedLine }: { onOpenProduction: () => void; onOpenStock: () => void; selectedLine: string; setSelectedLine: (value: string) => void }) {
  return <>
    <PageHeading eyebrow="Terça-feira, 09 de setembro" title="Bom dia, Rafael" description="A fábrica está em ritmo forte. Aqui está o pulso da sua operação." action={<button className="primary-button" onClick={onOpenProduction}><Plus size={17} /> Nova ordem de produção</button>} />
    <div className="alert-banner"><div className="alert-icon"><AlertTriangle size={18} /></div><div><strong>Configuração fiscal requer atenção</strong><span>O regime informado mistura Lucro Real e Simples Nacional. Confirme a opção tributária antes de publicar preços.</span></div><button onClick={() => alert('A parametrização fiscal será aberta na Etapa 3.')}>Revisar agora <ChevronRight size={15} /></button></div>
    <div className="filter-row"><div className="filter-caption"><SlidersHorizontal size={15} /> Visão da operação</div><div className="filter-control"><span>Linha</span><select value={selectedLine} onChange={(event) => setSelectedLine(event.target.value)}><option>Todas as linhas</option><option>Cadeiras Lina</option><option>Banquetas Oca</option></select></div><div className="period-control">Últimos 30 dias <ChevronRight size={14} /></div></div>
    <div className="metric-grid"><MetricCard label="Produção no mês" value="1.248" detail="peças finalizadas" trend="18,4%" direction="up" accent="teal" /><MetricCard label="Ocupação fabril" value="78,6%" detail="capacidade efetiva" trend="6,2%" direction="up" accent="peach" /><MetricCard label="Custo médio / peça" value="R$ 148,50" detail="vs. R$ 153,20 anterior" trend="3,1%" direction="down" accent="cream" /><MetricCard label="Margem de contribuição" value="32,4%" detail="média vendida" trend="2,8%" direction="up" accent="lilac" /></div>
    <div className="dashboard-grid"><section className="panel production-panel"><div className="panel-header"><div><span className="panel-kicker">Acompanhamento ao vivo</span><h2>Ordens em produção</h2></div><button className="text-button" onClick={onOpenProduction}>Ver todas <ChevronRight size={15} /></button></div><div className="order-table"><div className="table-head"><span>Ordem / produto</span><span>Etapa atual</span><span>Avanço</span><span>Entrega</span></div>{orders.slice(0, 3).map((order) => <OrderRow key={order.id} order={order} />)}</div></section><section className="panel stock-panel"><div className="panel-header"><div><span className="panel-kicker">Atenção necessária</span><h2>Saúde do estoque</h2></div><button className="text-button" onClick={onOpenStock}>Abrir estoque <ChevronRight size={15} /></button></div><div className="stock-list">{inventory.map((item) => <StockRow key={item.sku} item={item} />)}</div></section></div>
    <div className="bottom-grid"><section className="panel chart-panel"><div className="panel-header"><div><span className="panel-kicker">Performance industrial</span><h2>Produção x capacidade</h2></div><div className="legend"><span><i className="legend-dot produced" /> Produzido</span><span><i className="legend-dot capacity" /> Capacidade</span></div></div><CapacityChart /></section><section className="panel bottleneck-panel"><div className="panel-header"><div><span className="panel-kicker">Análise de gargalo</span><h2>Fluxo da linha</h2></div><button className="icon-button"><BarChart3 size={17} /></button></div><Bottleneck /></section></div>
  </>
}

function MetricCard({ label, value, detail, trend, direction, accent }: { label: string; value: string; detail: string; trend: string; direction: 'up' | 'down'; accent: string }) { return <div className={`metric-card ${accent}`}><div className="metric-top"><span>{label}</span><div className={`trend ${direction}`} >{direction === 'up' ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}{trend}</div></div><strong>{value}</strong><small>{detail}</small></div> }
function OrderRow({ order }: { order: ProductionOrder }) { return <div className="order-row"><div className="order-id"><span className="status-marker" data-status={order.status} /><div><strong>{order.id}</strong><small>{order.product} · {order.quantity} un</small></div></div><span className="stage-label">{order.station}</span><div className="progress-wrap"><div className="progress-track"><span style={{ width: `${order.progress}%` }} /></div><small>{order.progress}%</small></div><span className={`status-label ${order.status.toLowerCase().replace(' ', '-')}`}>{order.due}</span></div> }
function StockRow({ item }: { item: typeof inventory[number] }) { return <div className="stock-row"><div className={`stock-symbol ${item.color}`}><Boxes size={15} /></div><div className="stock-info"><strong>{item.name}</strong><small>{item.sku}</small></div><div className="stock-level"><strong>{item.stock}</strong><div className="mini-track"><span className={item.color} style={{ width: `${item.level}%` }} /></div></div></div> }
function CapacityChart() { const bars = [62, 68, 70, 76, 72, 84, 79, 88, 81, 91, 86, 94]; return <div className="chart-area"><div className="chart-y"><span>100%</span><span>75%</span><span>50%</span><span>25%</span><span>0%</span></div><div className="chart-bars">{bars.map((height, index) => <div className="bar-group" key={index}><div className="bar-pair"><span className="bar capacity" style={{ height: `${Math.min(height + 8, 100)}%` }} /><span className="bar produced" style={{ height: `${height}%` }} /></div><small>{['Jun 10', 'Jun 12', 'Jun 14', 'Jun 16', 'Jun 18', 'Jun 20', 'Jun 22', 'Jun 24', 'Jun 26', 'Jun 28', 'Jun 30', 'Jul 02'][index]}</small></div>)}</div></div> }
function Bottleneck() { return <div className="bottleneck-list"><div className="bottleneck-row"><div><strong>1. Usinagem</strong><small>2,8 min / peça</small></div><span className="bottleneck-value high">92%</span></div><div className="bottleneck-bar"><span style={{ width: '92%' }} /></div><div className="bottleneck-row"><div><strong>2. Montagem</strong><small>2,1 min / peça</small></div><span className="bottleneck-value medium">74%</span></div><div className="bottleneck-bar"><span style={{ width: '74%' }} /></div><div className="bottleneck-row"><div><strong>3. Estofamento</strong><small>1,6 min / peça</small></div><span className="bottleneck-value low">58%</span></div><div className="bottleneck-bar"><span style={{ width: '58%' }} /></div><div className="bottleneck-callout"><BarChart3 size={16} /><span>Adicionar 1 operador em usinagem eleva a capacidade em <strong>14,8%</strong>.</span></div></div> }

function ProductionView({ search, setSearch, filteredOrders }: { search: string; setSearch: (value: string) => void; filteredOrders: ProductionOrder[] }) { return <><PageHeading eyebrow="PCP · Fábrica" title="Ordens de produção" description="Acompanhe o avanço de cada ordem e mantenha o fluxo sem interrupções." action={<button className="primary-button"><Plus size={17} /> Emitir OP</button>} /><div className="production-summary"><div><span>Em andamento</span><strong>02</strong></div><div><span>Em espera</span><strong>01</strong></div><div><span>Concluídas hoje</span><strong>03</strong></div><div><span>Peças no fluxo</span><strong>516</strong></div></div><section className="panel full-panel"><div className="panel-toolbar"><div className="search-box"><Search size={16} /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Buscar por OP, produto ou etapa" /></div><button className="secondary-button"><SlidersHorizontal size={16} /> Filtrar</button><button className="secondary-button"><FileText size={16} /> Exportar</button></div><div className="full-order-table"><div className="table-head"><span>Ordem / produto</span><span>Etapa atual</span><span>Avanço</span><span>Prazo</span><span>Status</span></div>{filteredOrders.map((order) => <div className="full-order-row" key={order.id}><div className="order-id"><span className="status-marker" data-status={order.status} /><div><strong>{order.id}</strong><small>{order.product} · lote de {order.quantity} un</small></div></div><span className="stage-label">{order.station}</span><div className="progress-wrap"><div className="progress-track"><span style={{ width: `${order.progress}%` }} /></div><small>{order.progress}%</small></div><span>{order.due}</span><span className={`pill-status ${order.status.toLowerCase().replace(' ', '-')}`}>{order.status}</span></div>)}</div></section></> }

function StockView() { return <><PageHeading eyebrow="Almoxarifado · Inventário" title="Estoque e materiais" description="Visibilidade dos insumos críticos, entradas recentes e pontos de reposição." action={<button className="primary-button"><Plus size={17} /> Registrar entrada</button>} /><div className="metric-grid stock-metrics"><MetricCard label="Valor em estoque" value="R$ 284,8 mil" detail="custo médio ponderado" trend="4,2%" direction="up" accent="teal" /><MetricCard label="Itens cadastrados" value="248" detail="12 movimentados hoje" trend="12" direction="up" accent="cream" /><MetricCard label="Abaixo do mínimo" value="03" detail="reposição necessária" trend="2" direction="down" accent="peach" /><MetricCard label="Giro médio" value="3,8x" detail="últimos 90 dias" trend="0,4x" direction="up" accent="lilac" /></div><section className="panel full-panel"><div className="panel-header"><div><span className="panel-kicker">Inventário atual</span><h2>Materiais críticos</h2></div><button className="text-button">Ver catálogo <ChevronRight size={15} /></button></div><div className="inventory-grid">{inventory.map((item) => <div className="inventory-card" key={item.sku}><div className={`inventory-card-icon ${item.color}`}><Boxes size={19} /></div><div className="inventory-card-top"><span>{item.sku}</span><span className={`inventory-state ${item.color}`}>{item.state}</span></div><h3>{item.name}</h3><strong>{item.stock}</strong><div className="inventory-meter"><span className={item.color} style={{ width: `${item.level}%` }} /></div><div className="inventory-footer"><small>Última entrada: 08 set</small><button className="icon-button"><ChevronRight size={15} /></button></div></div>)}</div></section></> }

function PricingView({ cost, setCost, margin, setMargin, tax, setTax, salePrice, contribution }: { cost: number; setCost: (value: number) => void; margin: number; setMargin: (value: number) => void; tax: number; setTax: (value: number) => void; salePrice: number; contribution: number }) { return <><PageHeading eyebrow="Custos industriais · Simulação" title="Custos e preços" description="Modele o preço de venda com base no custo fabril e nos parâmetros comerciais." action={<button className="secondary-button"><FileText size={16} /> Salvar simulação</button>} /><div className="pricing-layout"><section className="panel pricing-inputs"><div className="panel-header"><div><span className="panel-kicker">Simulador de preço</span><h2>Parâmetros da Cadeira Lina</h2></div><span className="draft-status">Rascunho</span></div><div className="input-group"><label>Custo unitário de fabricação <span>CUF</span></label><div className="money-input"><span>R$</span><input type="number" value={cost} onChange={(event) => setCost(Number(event.target.value))} /></div><small>MP + MOD + CIF rateado</small></div><div className="input-group"><label>Tributos sobre venda <span>Regime pendente</span></label><div className="range-value"><input type="range" min="0" max="30" step="0.05" value={tax} onChange={(event) => setTax(Number(event.target.value))} /><strong>{tax.toFixed(2).replace('.', ',')}%</strong></div><small>Parâmetro provisório para simulação. Valide o regime fiscal.</small></div><div className="input-group"><label>Margem líquida pretendida</label><div className="range-value"><input type="range" min="5" max="60" step="1" value={margin} onChange={(event) => setMargin(Number(event.target.value))} /><strong>{margin}%</strong></div><small>Margem após tributos e despesas comerciais</small></div><div className="cost-breakdown"><div><span>Matéria-prima</span><strong>R$ 74,20</strong></div><div><span>Mão de obra direta</span><strong>R$ 42,80</strong></div><div><span>CIF rateado</span><strong>R$ 31,50</strong></div><div className="breakdown-total"><span>Custo de fabricação</span><strong>{formatBRL(cost)}</strong></div></div></section><section className="price-result"><div className="result-orbit"><Calculator size={22} /></div><span className="panel-kicker">Preço sugerido</span><strong>{formatBRL(salePrice)}</strong><span className="result-note">por unidade · markup divisor</span><div className="result-divider" /><div className="result-stats"><div><span>Margem líquida</span><strong>{formatBRL(contribution)}</strong></div><div><span>Markup aplicado</span><strong>{(salePrice / cost).toFixed(2).replace('.', ',')}x</strong></div><div><span>Tributos estimados</span><strong>{formatBRL(salePrice * tax / 100)}</strong></div></div><button className="result-button"><ShieldCheck size={16} /> Validar com financeiro</button></section></div><div className="pricing-note"><AlertTriangle size={16} /><span><strong>Atenção:</strong> o motor fiscal está aguardando a confirmação entre Lucro Real e Simples Nacional. O valor acima é apenas uma simulação gerencial.</span></div></> }

export default App

createRoot(document.getElementById('root')!).render(<App />)
