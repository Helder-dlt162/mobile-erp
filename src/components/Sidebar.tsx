import { BarChart3, Boxes, ChevronDown, ChevronRight, CircleDollarSign, Factory, LayoutDashboard, PackageCheck, Receipt, Settings2, Truck, Users } from 'lucide-react'
import type { Section } from '../domain'

interface SidebarProps {
  open: boolean
  section: Section
  currentRole?: string
  canSee: (permission: string) => boolean
  fiscalOpen: boolean
  financeOpen: boolean
  usersOpen: boolean
  onSectionChange: (section: Section) => void
  onToggleFiscal: () => void
  onToggleFinance: () => void
  onToggleUsers: () => void
}

const mainItems: Array<{ label: Section; icon: typeof LayoutDashboard; permission: string }> = [
  { label: 'Visão geral', icon: LayoutDashboard, permission: 'dashboard' },
  { label: 'Produção', icon: Factory, permission: 'production' },
  { label: 'Estoque', icon: Boxes, permission: 'inventory' },
  { label: 'Fornecedores', icon: Truck, permission: 'partners' },
  { label: 'Clientes', icon: Users, permission: 'partners' },
]

export function Sidebar({ open, section, currentRole, canSee, fiscalOpen, financeOpen, usersOpen, onSectionChange, onToggleFiscal, onToggleFinance, onToggleUsers }: SidebarProps) {
  return <aside className={`sidebar ${open ? 'is-open' : 'is-collapsed'}`}>
    <div className="brand-lockup"><div className="brand-mark">✦</div>{open && <div><strong>ATELIER</strong><span>INDUSTRIAL OS</span></div>}</div>
    <div className="workspace-switcher"><div className="workspace-avatar">AM</div>{open && <><div className="workspace-copy"><strong>Ateliê Móveis</strong><span>Unidade principal</span></div><ChevronRight size={15} /></>}</div>
    <nav className="main-nav" aria-label="Navegação principal">
      {mainItems.filter((item) => canSee(item.permission)).map(({ label, icon: Icon }) => <button key={label} className={`nav-item ${section === label ? 'active' : ''}`} onClick={() => onSectionChange(label)} title={label}><Icon size={18} />{open && <span>{label}</span>}{open && label === 'Estoque' && <span className="nav-badge">3</span>}</button>)}
      {canSee('purchasing') && <><button className={`nav-item ${(section === 'Nota fiscal de entrada' || section === 'Nota fiscal de venda') ? 'active' : ''}`} onClick={onToggleFiscal} title="Notas fiscais"><Receipt size={18} />{open && <span>Notas fiscais</span>}{open && (fiscalOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />)}</button>{open && fiscalOpen && <div className="nav-submenu"><button className={`nav-subitem ${section === 'Nota fiscal de entrada' ? 'active' : ''}`} onClick={() => onSectionChange('Nota fiscal de entrada')}>NF de entrada</button><button className="nav-subitem wip" onClick={() => onSectionChange('Nota fiscal de venda')}>NF de venda <small>WIP</small></button></div>}</>}
      {canSee('finance') && <><button className={`nav-item ${section === 'Contas a pagar' ? 'active' : ''}`} onClick={onToggleFinance} title="Financeiro"><CircleDollarSign size={18} />{open && <span>Financeiro</span>}{open && (financeOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />)}</button>{open && financeOpen && <div className="nav-submenu"><button className={`nav-subitem ${section === 'Contas a pagar' ? 'active' : ''}`} onClick={() => onSectionChange('Contas a pagar')}>Contas a pagar</button></div>}</>}
    </nav>
    {open && <div className="nav-label">Gestão</div>}
    <nav className="secondary-nav">{canSee('movements') && <button className={`nav-item ${section === 'Movimentações' ? 'active' : ''}`} onClick={() => onSectionChange('Movimentações')}><PackageCheck size={18} />{open && <span>Movimentações</span>}</button>}<button className="nav-item" onClick={() => onSectionChange('Relatórios' as Section)}><BarChart3 size={18} />{open && <span>Relatórios</span>}{open && <small className="nav-wip">WIP</small>}</button></nav>
    <div className="sidebar-bottom">{canSee('settings') && <button className={`nav-item ${section === 'Configurações' ? 'active' : ''}`} onClick={() => onSectionChange('Configurações')}><Settings2 size={18} />{open && <span>Configurações</span>}</button>}{currentRole === 'admin' && <><button className={`nav-item ${(section === 'Usuários' || section === 'Funcionários') ? 'active' : ''}`} onClick={onToggleUsers}><Users size={18} />{open && <span>Usuários</span>}{open && (usersOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />)}</button>{open && usersOpen && <div className="nav-submenu"><button className={`nav-subitem ${section === 'Usuários' ? 'active' : ''}`} onClick={() => onSectionChange('Usuários')}>Usuários</button><button className="nav-subitem wip" onClick={() => onSectionChange('Funcionários')}>Funcionários <small>WIP</small></button></div>}</>}<div className="profile-row"><div className="profile-avatar">RS</div>{open && <div className="workspace-copy"><strong>Rafael Silva</strong><span>Administrador</span></div>}</div></div>
  </aside>
}
