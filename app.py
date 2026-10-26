import streamlit as st
import networkx as nx
import plotly.graph_objects as go

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="ReliefLink: Disaster Management System",
    page_icon="🚑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean UI styling
st.markdown("""
    <style>
    .main-header { font-size: 26px; font-weight: 700; color: #0284c7; margin-bottom: 0px; }
    .sub-text { font-size: 14px; color: #64748b; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# CORE SYSTEM ENGINE (ReliefLink Logic)
# ==========================================
class ReliefLinkSystem:
    def __init__(self):
        if 'G' not in st.session_state:
            self.init_scenario()

    def init_scenario(self):
        st.session_state.G = nx.Graph()
        st.session_state.blocked_edges = set()
        
        # Node positions & coordinates
        st.session_state.node_positions = {
            'RC_North': (2, 8), 'RC_East': (8, 6), 'RC_South': (4, 1),
            'RZ_Alpha': (1, 5), 'RZ_Beta': (5, 5), 'RZ_Gamma': (8, 2), 'RZ_Delta': (3, 3),
            'Junct_1': (4, 7), 'Junct_2': (6, 3)
        }
        
        st.session_state.node_types = {
            'RC_North': 'relief_center', 'RC_East': 'relief_center', 'RC_South': 'relief_center',
            'RZ_Alpha': 'red_zone', 'RZ_Beta': 'red_zone', 'RZ_Gamma': 'red_zone', 'RZ_Delta': 'red_zone',
            'Junct_1': 'junction', 'Junct_2': 'junction'
        }

        edges = [
            ('RC_North', 'Junct_1', 3), ('RC_North', 'RZ_Alpha', 4),
            ('Junct_1', 'RZ_Beta', 3), ('Junct_1', 'RC_East', 5),
            ('RZ_Alpha', 'RZ_Delta', 4), ('RZ_Alpha', 'Junct_1', 3),
            ('RZ_Beta', 'RC_East', 4), ('RZ_Beta', 'Junct_2', 3), ('RZ_Beta', 'RZ_Delta', 3),
            ('RC_East', 'Junct_2', 4), ('RC_East', 'RZ_Gamma', 5),
            ('RZ_Delta', 'RC_South', 3), ('RZ_Delta', 'Junct_2', 4),
            ('Junct_2', 'RZ_Gamma', 3), ('RC_South', 'RZ_Gamma', 5)
        ]

        for u, v, w in edges:
            st.session_state.G.add_edge(u, v, weight=w)

        st.session_state.center_inventories = {
            'RC_North': {'food': 120, 'water': 200, 'medicine': 50, 'ambulance': 5},
            'RC_East':  {'food': 80,  'water': 150, 'medicine': 30, 'ambulance': 3},
            'RC_South': {'food': 100, 'water': 180, 'medicine': 40, 'ambulance': 4}
        }

        st.session_state.zone_demands = {
            'RZ_Alpha': {'priority': 'High',   'food': 50, 'water': 80, 'medicine': 25, 'ambulance': 2},
            'RZ_Beta':  {'priority': 'High',   'food': 90, 'water': 120, 'medicine': 35, 'ambulance': 3},
            'RZ_Gamma': {'priority': 'Medium', 'food': 40, 'water': 60,  'medicine': 15, 'ambulance': 1},
            'RZ_Delta': {'priority': 'Low',    'food': 30, 'water': 40,  'medicine': 10, 'ambulance': 1}
        }

    def get_active_graph(self):
        active_G = st.session_state.G.copy()
        for u, v in list(st.session_state.blocked_edges):
            if active_G.has_edge(u, v):
                active_G.remove_edge(u, v)
        return active_G

system = ReliefLinkSystem()

# ==========================================
# SIDEBAR CONTROLS & MANAGEMENT PANEL
# ==========================================
st.sidebar.markdown("### 🎛️ Control Operations Panel")

if st.sidebar.button("🔄 Reset Entire Scenario", use_container_width=True):
    system.init_scenario()
    st.sidebar.success("Scenario reset to default!")
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("🚧 Road Blockage Management")
edges_list = [f"{u} <-> {v}" for u, v in st.session_state.G.edges()]
selected_edge = st.sidebar.selectbox("Select Road Segment", edges_list)
u_node, v_node = selected_edge.split(" <-> ")

col_b1, col_b2 = st.sidebar.columns(2)
if col_b1.button("Block Road", type="primary", use_container_width=True):
    st.session_state.blocked_edges.add(tuple(sorted((u_node, v_node))))
    st.success(f"Blocked road: {u_node} ↔ {v_node}")
    st.rerun()

if col_b2.button("Unblock", use_container_width=True):
    st.session_state.blocked_edges.discard(tuple(sorted((u_node, v_node))))
    st.success(f"Cleared road: {u_node} ↔ {v_node}")
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("📍 Mission Parameters")
centers = [n for n, t in st.session_state.node_types.items() if t == 'relief_center']
zones = [n for n, t in st.session_state.node_types.items() if t == 'red_zone']

sel_center = st.sidebar.selectbox("Relief Center Source", centers)
sel_zone = st.sidebar.selectbox("Target Red Zone", zones)
sel_resource = st.sidebar.selectbox("Resource Type", ['food', 'water', 'medicine', 'ambulance'])

# ==========================================
# MAIN DASHBOARD LAYOUT
# ==========================================
st.markdown('<p class="main-header">🚑 ReliefLink: Graph-Based Disaster Operations Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">Integrated Dijkstra Routing, Menger’s Theorem Resilience, and Multi-Center Resource Allocation.</p>', unsafe_allow_html=True)

col_map, col_controls = st.columns([1.3, 1])
highlight_path = st.session_state.get('highlight_path', None)

with col_map:
    st.subheader("🗺️ Network Topology & Field View")
    
    pos = st.session_state.node_positions
    G = st.session_state.G
    
    edge_x, edge_y = [], []
    for u, v, d in G.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        
    edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=2, color='#94a3b8'), hoverinfo='none', mode='lines')

    blocked_x, blocked_y = [], []
    for u, v in st.session_state.blocked_edges:
        if G.has_edge(u, v):
            x0, y0 = pos[u]; x1, y1 = pos[v]
            blocked_x.extend([x0, x1, None]); blocked_y.extend([y0, y1, None])
    blocked_trace = go.Scatter(x=blocked_x, y=blocked_y, line=dict(width=4, color='#ef4444', dash='dash'), name='Blocked', mode='lines')

    path_x, path_y = [], []
    if highlight_path:
        for i in range(len(highlight_path) - 1):
            u, v = highlight_path[i], highlight_path[i+1]
            x0, y0 = pos[u]; x1, y1 = pos[v]
            path_x.extend([x0, x1, None]); path_y.extend([y0, y1, None])
    path_trace = go.Scatter(x=path_x, y=path_y, line=dict(width=6, color='#0284c7'), name='Optimal Route', mode='lines')

    node_x, node_y, node_color, node_text, node_size = [], [], [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x); node_y.append(y)
        n_type = st.session_state.node_types[node]
        if n_type == 'relief_center':
            inv = st.session_state.center_inventories[node]
            node_color.append('#22c55e')
            node_size.append(24)
            node_text.append(f"<b>{node} (Center)</b><br>Food: {inv['food']} | Water: {inv['water']}<br>Meds: {inv['medicine']} | Amb: {inv['ambulance']}")
        elif n_type == 'red_zone':
            dem = st.session_state.zone_demands[node]
            node_color.append('#ef4444')
            node_size.append(24)
            node_text.append(f"<b>{node} ({dem['priority']} Priority)</b><br>Food Req: {dem['food']} | Water Req: {dem['water']}<br>Meds Req: {dem['medicine']} | Amb Req: {dem['ambulance']}")
        else:
            node_color.append('#64748b')
            node_size.append(14)
            node_text.append(f"Junction: {node}")

    node_trace = go.Scatter(
        x=node_x, y=node_y, mode='markers+text', hoverinfo='text',
        text=[n for n in G.nodes()], textposition="top center", hovertext=node_text,
        marker=dict(size=node_size, color=node_color, line=dict(width=2, color='#ffffff'))
    )

    fig = go.Figure(data=[edge_trace, blocked_trace, path_trace, node_trace])
    fig.update_layout(showlegend=False, hovermode='closest', margin=dict(b=0, l=0, r=0, t=10),
                      xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                      yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                      height=480, template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

with col_controls:
    st.subheader("⚡ Advanced Graph Analytics")
    
    tab1, tab2, tab3 = st.tabs(["Shortest Route", "Menger Resilience", "Multi-Center Alloc"])
    active_G = system.get_active_graph()

    with tab1:
        st.markdown("**Dijkstra's Shortest Path Algorithm**[cite: 5]")
        if st.button("Compute Optimal Route", type="primary", use_container_width=True):
            if nx.has_path(active_G, sel_center, sel_zone):
                path = nx.dijkstra_path(active_G, sel_center, sel_zone, weight='weight')
                dist = nx.dijkstra_path_length(active_G, sel_center, sel_zone, weight='weight')
                st.session_state.highlight_path = path
                st.success(f"Route Found! Distance: **{dist} km**")
                st.markdown(f"**Path Sequence:** `{' ➔ '.join(path)}`")
                st.rerun()
            else:
                st.error("No available path! Road blockages have severed connection.")
                st.session_state.highlight_path = None

    with tab2:
        st.markdown("**Network Resilience & Menger's Theorem**[cite: 4]")
        if st.button("Analyze $k$-Connectivity", use_container_width=True):
            if nx.has_path(active_G, sel_center, sel_zone):
                k = nx.edge_connectivity(active_G, sel_center, sel_zone)
                disjoint_paths = list(nx.edge_disjoint_paths(active_G, sel_center, sel_zone))
                st.metric("Edge Connectivity ($k$-value)", f"{k}")
                st.info(f"Resilient against single-road failure: **{'YES' if k >= 2 else 'NO (Vulnerable Bottleneck)'}**")
                st.markdown(f"**Independent Edge-Disjoint Paths ({len(disjoint_paths)}):**")
                for idx, p in enumerate(disjoint_paths, 1):
                    st.text(f"Path {idx}: {' -> '.join(p)}")
            else:
                st.error("Nodes are disconnected.")

    with tab3:
        st.markdown("**Multi-Center Resource Dispatching**[cite: 5]")
        if st.button("Execute Supply Allocation", type="primary", use_container_width=True):
            demand = st.session_state.zone_demands[sel_zone][sel_resource]
            if demand <= 0:
                st.warning(f"Red Zone {sel_zone} has no remaining demand for {sel_resource}.")
            else:
                center_distances = []
                for c in centers:
                    if nx.has_path(active_G, c, sel_zone):
                        d = nx.dijkstra_path_length(active_G, c, sel_zone, weight='weight')
                        center_distances.append((c, d))
                center_distances.sort(key=lambda x: x[1])

                needed = demand
                allocated_log = []
                for c, dist in center_distances:
                    avail = st.session_state.center_inventories[c][sel_resource]
                    if avail > 0:
                        take = min(needed, avail)
                        allocated_log.append((c, take, dist))
                        needed -= take
                        if needed == 0:
                            break

                for c, amt, dist in allocated_log:
                    st.session_state.center_inventories[c][sel_resource] -= amt
                    st.markdown(f"✔ **{c}** dispatched **{amt} units** of {sel_resource} ({dist} km away)")

                st.session_state.zone_demands[sel_zone][sel_resource] = needed
                if needed == 0:
                    st.success("Allocation fully satisfied across centers!")
                else:
                    st.warning(f"Partial allocation complete. Deficit remaining: {needed} units.")